import copy

import numpy as np
import param
import matplotlib.ticker as mticker
from cartopy import crs as ccrs
from cartopy.io.img_tiles import GoogleTiles, QuadtreeTiles
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

try:
    from owslib.wmts import WebMapTileService
except ImportError:
    WebMapTileService = None

from holoviews.core import Store, HoloMap, Layout, Overlay, Element, NdLayout
from holoviews.core import util
from holoviews.core.data import GridInterface
from holoviews.core.options import SkipRendering, Options
from holoviews.plotting.mpl import (
    ElementPlot, PointPlot, AnnotationPlot, TextPlot, LabelsPlot,
    LayoutPlot as HvLayoutPlot, OverlayPlot as HvOverlayPlot,
    PathPlot, PolygonPlot, RasterPlot, ContourPlot, GraphPlot,
    TriMeshPlot, QuadMeshPlot, VectorFieldPlot, HexTilesPlot,
    SegmentPlot, RectanglesPlot
)
from holoviews.plotting.mpl.util import get_raster_array, wrap_formatter


from ...element import (
    Image, Points, Feature, WMTS, Tiles, Text, LineContours,
    FilledContours, is_geographic, Path, Polygons, Shape, RGB,
    Contours, Nodes, EdgePaths, Graph, TriMesh, QuadMesh, VectorField,
    HexTiles, Labels, Rectangles, Segments
)
from ...util import geo_mesh, poly_types
from ..plot import ProjectionPlot

from ...operation import (
    project_points, project_path, project_graph, project_quadmesh,
    project_geom
)



class LayoutPlot(ProjectionPlot, HvLayoutPlot):
    """
    Extends HoloViews LayoutPlot with functionality to determine
    the correct projection for each axis.
    """

    vspace = param.Number(default=0.3, doc="""
      Specifies the space between vertically adjacent elements in the grid.
      Default value is set conservatively to avoid overlap of subplots.""")

    v17_layout_format = True



class GeoOverlayPlot(ProjectionPlot, HvOverlayPlot):
    """
    Extends HoloViews OverlayPlot with functionality to determine
    the correct projection for each axis.
    """

    global_extent = param.Boolean(default=False, doc="""
        Set the extent of the Axes to the limits of the projection.""")

    _propagate_options = HvOverlayPlot._propagate_options + ['global_extent']

    def __init__(self, element, **params):
        super().__init__(element, **params)
        plot_opts = self.lookup_options(self.hmap.last, 'plot').options
        self.geographic = any(self.hmap.traverse(is_geographic, [Element]))
        if 'aspect' not in plot_opts and self.geographic:
            self.aspect = 'equal'

    def _finalize_axis(self, *args, **kwargs):
        gridlabels = self.geographic and isinstance(self.projection, (ccrs.PlateCarree, ccrs.Mercator))
        if gridlabels:
            xaxis, yaxis = self.xaxis, self.yaxis
            self.xaxis = self.yaxis = None
        try:
            ret = super()._finalize_axis(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            if gridlabels:
                self.xaxis, self.yaxis = xaxis, yaxis

        axis = self.handles['axis']
        if self.show_grid:
            axis.grid()
        if self.global_extent:
            axis.set_global()
        return ret



class GeoPlot(ProjectionPlot, ElementPlot):
    """
    Plotting baseclass for geographic plots with a cartopy projection.
    """

    apply_ranges = param.Boolean(default=False, doc="""
        Do not use ranges to compute plot extents by default.""")

    global_extent = param.Boolean(default=False, doc="""
        Whether the plot should display the whole globe.""")

    projection = param.Parameter(default=ccrs.PlateCarree())

    # Project operation to apply to the element
    _project_operation = None

    def __init__(self, element, **params):
        if 'projection' not in params:
            el = element.last if isinstance(element, HoloMap) else element
            params['projection'] = el.crs
        super().__init__(element, **params)
        plot_opts = self.lookup_options(self.hmap.last, 'plot').options
        self.geographic = is_geographic(self.hmap.last)
        if 'aspect' not in plot_opts:
            self.aspect = 'equal' if self.geographic else 'square'

    def _process_grid(self, gl):
        if not self.show_grid:
            gl.xlines = False
            gl.ylines = False

        if self.xaxis and self.xaxis != 'bare':
            xticksize = self._fontsize('xticks', common=False).get('fontsize')
            gl.xlabel_style = {'size': xticksize}

            if isinstance(self.xticks, list):
                gl.xlocator = mticker.FixedLocator(self.xticks)
            elif isinstance(self.xticks, int):
                gl.xlocator = mticker.MaxNLocator(self.xticks)

            if self.xaxis in ['bottom', 'top-bare']:
                gl.top_labels = False
            elif self.xaxis in ['top', 'bottom-bare']:
                gl.bottom_labels = False

            if self.xformatter is None:
                gl.xformatter = LONGITUDE_FORMATTER
            else:
                gl.xformatter = wrap_formatter(self.xformatter)
        else:
            gl.top_labels = False
            gl.bottom_labels = False


        if self.yaxis and self.yaxis != 'bare':
            yticksize = self._fontsize('yticks', common=False).get('fontsize')
            gl.ylabel_style = {'size': yticksize}

            if isinstance(self.yticks, list):
                gl.ylocator = mticker.FixedLocator(self.yticks)
            elif isinstance(self.yticks, int):
                gl.ylocator = mticker.MaxNLocator(self.yticks)

            if self.yaxis in ['left', 'right-bare']:
                gl.right_labels = False
            elif self.yaxis in ['right', 'left-bare']:
                gl.left_labels = False

            if self.yformatter is None:
                gl.yformatter = LATITUDE_FORMATTER
            else:
                gl.yformatter = wrap_formatter(self.yformatter)
        else:
            gl.left_labels = False
            gl.right_labels = False


    def _finalize_axis(self, *args, **kwargs):
        gridlabels = self.geographic and isinstance(self.projection, (ccrs.PlateCarree, ccrs.Mercator))
        if gridlabels:
            xaxis, yaxis = self.xaxis, self.yaxis
            self.xaxis = self.yaxis = None
        try:
            ret = super()._finalize_axis(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            if gridlabels:
                self.xaxis, self.yaxis = xaxis, yaxis

        axis = self.handles['axis']
        # Only PlateCarree and Mercator plots support grid labels.
        if 'gridlines' in self.handles:
            gl = self.handles['gridlines']
        else:
            self.handles['gridlines'] = gl = axis.gridlines(
                draw_labels=gridlabels and self.zorder == 0)
        self._process_grid(gl)

        if self.global_extent:
            axis.set_global()
        return ret

    def get_data(self, element, ranges, style):
        if self._project_operation and self.geographic:
            element = self._project_operation(element, projection=self.projection)
        return super().get_data(element, ranges, style)

    def teardown_handles(self):
        """
        Delete artist handle so it can be redrawn.
        """
        try:
            self.handles['artist'].remove()
        except ValueError:
            pass



class GeoImagePlot(GeoPlot, RasterPlot):
    """
    Draws a pcolormesh plot from the data in a Image Element.
    """

    style_opts = ['alpha', 'cmap', 'visible', 'filterrad', 'clims', 'norm']

    def get_data(self, element, ranges, style):
        self._norm_kwargs(element, ranges, style, element.vdims[0])
        style.pop('interpolation', None)
        xs, ys, zs = geo_mesh(element)
        xs = GridInterface._infer_interval_breaks(xs)
        ys = GridInterface._infer_interval_breaks(ys)
        if self.geographic:
            style['transform'] = element.crs
        return (xs, ys, zs), style, {}


    def init_artists(self, ax, plot_args, plot_kwargs):
        artist = ax.pcolormesh(*plot_args, **plot_kwargs)
        return {'artist': artist}


    def update_handles(self, *args):
        """
        Update the elements of the plot.
        """
        return GeoPlot.update_handles(self, *args)



class GeoQuadMeshPlot(GeoPlot, QuadMeshPlot):

    _project_operation = project_quadmesh

    def get_data(self, element, ranges, style):
        if self._project_operation and self.geographic:
            element = self._project_operation(element, projection=self.projection)
        return super(GeoPlot, self).get_data(element, ranges, style)



class GeoRGBPlot(GeoImagePlot):
    """
    Draws a imshow plot from the data in a RGB Element.
    """

    style_opts = ['alpha', 'visible', 'filterrad']

    def get_data(self, element, ranges, style):
        self._norm_kwargs(element, ranges, style, element.vdims[0])
        style.pop('interpolation', None)
        zs = get_raster_array(element)[::-1]
        l, b, r, t = element.bounds.lbrt()
        style['extent'] = [l, r, b, t]
        if self.geographic:
            style['transform'] = element.crs
        return (zs,), style, {}


    def init_artists(self, ax, plot_args, plot_kwargs):
        artist = ax.imshow(*plot_args, **plot_kwargs)
        return {'artist': artist}


    def update_handles(self, *args):
        """
        Update the elements of the plot.
        """
        return GeoPlot.update_handles(self, *args)


class GeoPointPlot(GeoPlot, PointPlot):
    """
    Draws a scatter plot from the data in a Points Element.
    """

    apply_ranges = param.Boolean(default=True)

    _project_operation = project_points


class GeoLabelsPlot(GeoPlot, LabelsPlot):
    """
    Draws a scatter plot from the data in a Labels Element.
    """

    apply_ranges = param.Boolean(default=True)

    _project_operation = project_points


class GeoHexTilesPlot(GeoPlot, HexTilesPlot):
    """
    Draws a scatter plot from the data in a Points Element.
    """

    apply_ranges = param.Boolean(default=True)

    _project_operation = project_points


class GeoVectorFieldPlot(GeoPlot, VectorFieldPlot):
    """
    Draws a vector field plot from the data in a VectorField Element.
    """

    apply_ranges = param.Boolean(default=True)

    _project_operation = project_points


class GeometryPlot(GeoPlot):

    def init_artists(self, ax, plot_args, plot_kwargs):
        if self.geographic:
            artist = ax.add_geometries(*plot_args, **plot_kwargs)
            return {'artist': artist}
        else:
            return super().init_artist(ax, plot_args, plot_kwargs)


class GeoPathPlot(GeoPlot, PathPlot):
    """
    Draws a Path plot from a Path Element.
    """

    apply_ranges = param.Boolean(default=True)

    _project_operation = project_path


class GeoContourPlot(GeoPlot, ContourPlot):
    """
    Draws a contour plot from a Contours Element.
    """

    apply_ranges = param.Boolean(default=True)

    _project_operation = project_path


class GeoPolygonPlot(GeoPlot, PolygonPlot):
    """
    Draws a scatter plot from the data in a Points Element.
    """

    apply_ranges = param.Boolean(default=True)

    _project_operation = project_path


class GeoSegmentPlot(GeoPlot, SegmentPlot):
    """
    Draws segments from the data in a the Segments Element.
    """

    apply_ranges = param.Boolean(default=True)

    _project_operation = project_geom


class GeoRectanglesPlot(GeoPlot, RectanglesPlot):
    """
    Draws rectangles from the data in a Rectangles Element.
    """

    apply_ranges = param.Boolean(default=True)

    _project_operation = project_geom


class LineContourPlot(GeoContourPlot):
    """
    Draws a contour plot.
    """

    levels = param.ClassSelector(default=10, class_=(list, int), doc="""
        A list of scalar values used to specify the contour levels.""")


class FilledContourPlot(GeoPolygonPlot):
    """
    Draws a filled contour plot.
    """

    levels = param.ClassSelector(default=10, class_=(list, int), doc="""
        A list of scalar values used to specify the contour levels.""")


class GeoShapePlot(GeometryPlot, PolygonPlot):
    """
    Draws a scatter plot from the data in a Points Element.
    """

    apply_ranges = param.Boolean(default=True)

    def get_data(self, element, ranges, style):
        if self.geographic:
            if not isinstance(element.data['geometry'], poly_types):
                style['facecolor'] = 'none'
            vdim = element.vdims[0] if element.vdims else None
            value = element.level
            if vdim is not None and (value is not None and np.isfinite(value)):
                self._norm_kwargs(element, ranges, style, vdim)
                style['clim'] = style.pop('vmin'), style.pop('vmax')
                style['array'] = np.array([value])
            return ([element.data['geometry']], element.crs), style, {}
        else:
            SkipRendering('Shape can only be plotted on geographic plot, '
                          'supply a coordinate reference system.')


class GeoGraphPlot(GeoPlot, GraphPlot):

    apply_ranges = param.Boolean(default=True)

    _project_operation = project_graph


class GeoTriMeshPlot(GeoPlot, TriMeshPlot):

    apply_ranges = param.Boolean(default=True)

    _project_operation = project_graph


########################################
#  Geographic features and annotations #
########################################


class FeaturePlot(GeoPlot):
    """
    Draws a feature from a Features Element.
    """

    scale = param.ObjectSelector(default='110m',
                                 objects=['10m', '50m', '110m'],
                                 doc="The scale of the Feature in meters.")

    style_opts = ['alpha', 'facecolor', 'edgecolor', 'linestyle', 'linewidth',
                  'visible']

    def get_data(self, element, ranges, style):
        if hasattr(element.data, 'with_scale'):
            feature = element.data.with_scale(self.scale)
        else:
            feature = copy.copy(element.data)
            feature.scale = self.scale
        return (feature,), style, {}

    def init_artists(self, ax, plot_args, plot_kwargs):
        return {'artist': ax.add_feature(*plot_args, **plot_kwargs)}


class WMTSPlot(GeoPlot):
    """
    Adds a Web Map Tile Service from a WMTS Element.
    """

    zoom = param.Integer(default=8, doc="""
        Controls the zoom level of the tile source.""")

    style_opts = ['alpha', 'cmap', 'interpolation', 'visible',
                  'filterrad', 'clims', 'norm']

    def get_data(self, element, ranges, style):
        if isinstance(element.data, str):
            if '{Q}' in element.data:
                tile_source = QuadtreeTiles(url=element.data)
            else:
                tile_source = GoogleTiles(url=element.data)
            return (tile_source, self.zoom), style, {}
        else:
            tile_source = element.data
            return (tile_source, element.layer), style, {}

    def init_artists(self, ax, plot_args, plot_kwargs):
        if isinstance(plot_args[0], GoogleTiles):
            if 'artist' in self.handles:
                return {'artist': self.handles['artist']}
            img = ax.add_image(*plot_args, **plot_kwargs)
            return {'artist': img or plot_args[0]}
        return {'artist': ax.add_wmts(*plot_args, **plot_kwargs)}

    def teardown_handles(self):
        """
        If no custom update_handles method is supplied this method
        is called to tear down any previous handles before replacing
        them.
        """
        if not isinstance(self.handles.get('artist'), GoogleTiles):
            self.handles['artist'].remove()



class GeoAnnotationPlot(AnnotationPlot):
    """
    AnnotationPlot handles the display of all annotation elements.
    """

    def initialize_plot(self, ranges=None):
        annotation = self.hmap.last
        key = self.keys[-1]
        ranges = self.compute_ranges(self.hmap, key, ranges)
        ranges = util.match_spec(annotation, ranges)
        axis = self.handles['axis']
        opts = self.style[self.cyclic_index]
        handles = self.draw_annotation(axis, annotation.data,
                                       annotation.crs, opts)
        self.handles['annotations'] = handles
        return self._finalize_axis(key, ranges=ranges)

    def update_handles(self, key, axis, annotation, ranges, style):
        # Clear all existing annotations
        for element in self.handles['annotations']:
            element.remove()

        self.handles['annotations'] = self.draw_annotation(axis,
                                                           annotation.data,
                                                           annotation.crs,
                                                           style)


class GeoTextPlot(GeoAnnotationPlot, TextPlot):
    "Draw the Text annotation object"

    def draw_annotation(self, axis, data, crs, opts):
        (x, y, text, fontsize,
         horizontalalignment, verticalalignment, rotation) = data
        opts['fontsize'] = fontsize
        if crs:
            x, y = axis.projection.transform_point(x, y, src_crs=crs)
        return [axis.text(x, y, text,
                          horizontalalignment=horizontalalignment,
                          verticalalignment=verticalalignment,
                          rotation=rotation, **opts)]


# Register plots with HoloViews
Store.register({LineContours: LineContourPlot,
                FilledContours: FilledContourPlot,
                Image: GeoImagePlot,
                Feature: FeaturePlot,
                WMTS: WMTSPlot,
                Tiles: WMTSPlot,
                Rectangles: GeoRectanglesPlot,
                Segments: GeoSegmentPlot,
                Points: GeoPointPlot,
                Labels: GeoLabelsPlot,
                VectorField: GeoVectorFieldPlot,
                Text: GeoTextPlot,
                Layout: LayoutPlot,
                NdLayout: LayoutPlot,
                Overlay: GeoOverlayPlot,
                Polygons: GeoPolygonPlot,
                Path: GeoPathPlot,
                Contours: GeoContourPlot,
                RGB: GeoRGBPlot,
                Shape: GeoShapePlot,
                Graph: GeoGraphPlot,
                TriMesh: GeoTriMeshPlot,
                Nodes: GeoPointPlot,
                EdgePaths: GeoPathPlot,
                HexTiles: GeoHexTilesPlot,
                QuadMesh: GeoQuadMeshPlot}, 'matplotlib')


# Define plot and style options
options = Store.options(backend='matplotlib')

options.Shape = Options('style', edgecolor='black', facecolor='#30A2DA')
