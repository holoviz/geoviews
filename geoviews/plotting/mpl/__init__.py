import copy

import numpy as np
import param
from cartopy import crs as ccrs
from cartopy.io.img_tiles import GoogleTiles

try:
    from owslib.wmts import WebMapTileService
except:
    WebMapTileService = None

from holoviews.core import Store, HoloMap, Layout, Overlay, Element, NdLayout
from holoviews.core import util
from holoviews.core.data import GridInterface
from holoviews.core.options import SkipRendering, Options
from holoviews.plotting.mpl import (ElementPlot, ColorbarPlot, PointPlot,
                                    AnnotationPlot, TextPlot,
                                    LayoutPlot as HvLayoutPlot,
                                    OverlayPlot as HvOverlayPlot,
                                    PathPlot, PolygonPlot, RasterPlot,
                                    ContourPlot, GraphPlot, TriMeshPlot,
                                    QuadMeshPlot, VectorFieldPlot,
                                    HexTilesPlot, LabelsPlot)
from holoviews.plotting.mpl.util import get_raster_array


from ...element import (Image, Points, Feature, WMTS, Tiles, Text,
                        LineContours, FilledContours, is_geographic,
                        Path, Polygons, Shape, RGB, Contours, Nodes,
                        EdgePaths, Graph, TriMesh, QuadMesh, VectorField,
                        HexTiles, Labels)
from ...util import project_extents, geo_mesh
from ..plot import ProjectionPlot

from ...operation import project_points, project_path, project_graph, project_quadmesh



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
        super(GeoOverlayPlot, self).__init__(element, **params)
        plot_opts = self.lookup_options(self.hmap.last, 'plot').options
        self.geographic = any(self.hmap.traverse(is_geographic, [Element]))
        if 'aspect' not in plot_opts and self.geographic:
            self.aspect = 'equal'

    def _finalize_axis(self, *args, **kwargs):
        ret = super(GeoOverlayPlot, self)._finalize_axis(*args, **kwargs)
        axis = self.handles['axis']
        if self.show_grid:
            axis.gridlines()
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
        super(GeoPlot, self).__init__(element, **params)
        plot_opts = self.lookup_options(self.hmap.last, 'plot').options
        self.geographic = is_geographic(self.hmap.last)
        if 'aspect' not in plot_opts:
            self.aspect = 'equal' if self.geographic else 'square'


    def get_extents(self, element, ranges):
        """
        Subclasses the get_extents method using the GeoAxes
        set_extent method to project the extents to the
        Elements coordinate reference system.
        """
        ax = self.handles['axis']
        extents = super(GeoPlot, self).get_extents(element, ranges)
        x0, y0, x1, y1 = extents
        if not self.geographic:
            return extents

        # If extent can't be determined autoscale, otherwise use
        # set_extent to convert coordinates to native coordinate
        # system
        if (None in extents or any(not np.isfinite(e) for e in extents) or
            x0 == x1 or y0 == y1):
            extents = None
        else:
            try:
                extents = project_extents((x0, y0, x1, y1), element.crs,
                                          self.projection)
            except:
                extents = (np.NaN,)*4

        if extents:
            l, b, r, t = extents
        else:
            ax.autoscale_view()
            (l, r), (b, t) = ax.get_xlim(), ax.get_ylim()

        return l, b, r, t

    def _finalize_axis(self, *args, **kwargs):
        ret = super(GeoPlot, self)._finalize_axis(*args, **kwargs)
        axis = self.handles['axis']
        if self.show_grid:
            axis.gridlines()
        if self.global_extent:
            axis.set_global()
        return ret


    def get_data(self, element, ranges, style):
        if self._project_operation and self.geographic and element.crs != self.projection:
            element = self._project_operation(element, projection=self.projection)
        return super(GeoPlot, self).get_data(element, ranges, style)


    def teardown_handles(self):
        """
        Delete artist handle so it can be redrawn.
        """
        try:
            self.handles['artist'].remove()
        except ValueError:
            pass


class LineContourPlot(GeoPlot, ColorbarPlot):
    """
    Draws a contour plot.
    """

    colorbar = param.Boolean(default=True)

    levels = param.ClassSelector(default=5, class_=(int, list), doc="""
        The levels of the contour as a number or list.""")

    style_opts = ['antialiased', 'alpha', 'cmap', 'linewidths', 'colors']

    _plot_methods = dict(single='contour')

    def get_data(self, element, ranges, style):
        args = geo_mesh(element)
        style.pop('label', None)
        if isinstance(self.levels, int):
            args += (self.levels,)
        else:
            style['levels'] = self.levels
        style['transform'] = element.crs
        return args, style, {}


    def teardown_handles(self):
        """
        Iterate over the artists in the collection and remove
        them individually.
        """
        if 'artist' in self.handles:
            for coll in self.handles['artist'].collections:
                try:
                    coll.remove()
                except ValueError:
                    pass


class FilledContourPlot(LineContourPlot):
    """
    Draws a filled contour plot.
    """

    style_opts = ['antialiased', 'alpha', 'cmap', 'linewidths']

    _plot_methods = dict(single='contourf')



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
            return super(GeometryPlot, self).init_artist(ax, plot_args, plot_kwargs)


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


class GeoShapePlot(GeometryPlot, PolygonPlot):
    """
    Draws a scatter plot from the data in a Points Element.
    """

    apply_ranges = param.Boolean(default=True)

    def get_data(self, element, ranges, style):
        if self.geographic:
            vdim = element.vdims[0] if element.vdims else None
            value = element.level
            if vdim is not None and (value is not None and np.isfinite(value)):
                self._norm_kwargs(element, ranges, style, vdim)
                style['clim'] = style.pop('vmin'), style.pop('vmax')
                style['array'] = np.array([value])
            return ([element.data], element.crs), style, {}
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
        if isinstance(element.data, util.basestring):
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
