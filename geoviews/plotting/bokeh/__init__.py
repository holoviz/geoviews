import copy

import param
import numpy as np
import shapely.geometry
from cartopy.crs import GOOGLE_MERCATOR
from bokeh.models import WMTSTileSource, BBoxTileSource, QUADKEYTileSource

from holoviews import Store, Overlay, NdOverlay
from holoviews.core import util
from holoviews.core.options import SkipRendering, Options, Compositor
from holoviews.plotting.bokeh.annotation import TextPlot, LabelsPlot
from holoviews.plotting.bokeh.chart import PointPlot, VectorFieldPlot
from holoviews.plotting.bokeh.graphs import TriMeshPlot, GraphPlot
from holoviews.plotting.bokeh.hex_tiles import hex_binning, HexTilesPlot
from holoviews.plotting.bokeh.path import PolygonPlot, PathPlot, ContourPlot
from holoviews.plotting.bokeh.raster import RasterPlot, RGBPlot, QuadMeshPlot
from holoviews.plotting.bokeh.util import mpl_to_bokeh

from ...element import (WMTS, Points, Polygons, Path, Contours, Shape,
                        Image, Feature, Text, RGB, Nodes, EdgePaths,
                        Graph, TriMesh, QuadMesh, VectorField, Labels,
                        HexTiles)
from ...operation import (project_image, project_shape, project_points,
                          project_path, project_graph, project_quadmesh)
from ...tile_sources import _ATTRIBUTIONS
from ...util import geom_to_array
from .plot import GeoPlot, GeoOverlayPlot
from . import callbacks # noqa

line_types = (shapely.geometry.MultiLineString, shapely.geometry.LineString)
poly_types = (shapely.geometry.MultiPolygon, shapely.geometry.Polygon)

class TilePlot(GeoPlot):

    style_opts = ['alpha', 'render_parents', 'level', 'min_zoom', 'max_zoom']

    def get_extents(self, element, ranges):
        extents = super(TilePlot, self).get_extents(element, ranges)
        if not self.overlaid and all(e is None or not np.isfinite(e) for e in extents):
            (x0, x1), (y0, y1) = GOOGLE_MERCATOR.x_limits, GOOGLE_MERCATOR.y_limits
            global_extent = (x0, y0, x1, y1)
            return global_extent
        return extents

    def get_data(self, element, ranges, style):
        if not isinstance(element.data, util.basestring):
            SkipRendering("WMTS element data must be a URL string, "
                          "bokeh cannot render %r" % element.data)
        if '{Q}' in element.data:
            tile_source = QUADKEYTileSource
        elif all(kw in element.data for kw in ('{XMIN}', '{XMAX}', '{YMIN}', '{YMAX}')):
            tile_source = BBoxTileSource
        elif all(kw in element.data for kw in ('{X}', '{Y}', '{Z}')):
            tile_source = WMTSTileSource
        else:
            raise ValueError('Tile source URL format not recognized. '
                             'Must contain {X}/{Y}/{Z}, {XMIN}/{XMAX}/{YMIN}/{YMAX} '
                             'or {Q} template strings.')
        params = {'url': element.data}
        for zoom in ('min_zoom', 'max_zoom'):
            if zoom in style:
                params[zoom] = style[zoom]
        for key, attribution in _ATTRIBUTIONS.items():
            if all(k in element.data for k in key):
                params['attribution'] = attribution
        return {}, {'tile_source': tile_source(**params)}, style

    def _update_glyph(self, renderer, properties, mapping, glyph):
        allowed_properties = glyph.properties()
        mapping['url'] = mapping.pop('tile_source').url
        merged = dict(properties, **mapping)
        glyph.update(**{k: v for k, v in merged.items()
                        if k in allowed_properties})

    def _init_glyph(self, plot, mapping, properties):
        """
        Returns a Bokeh glyph object.
        """
        level = properties.pop('level', 'underlay')
        renderer = plot.add_tile(mapping['tile_source'], level=level)
        renderer.alpha = properties.get('alpha', 1)
        return renderer, renderer


class GeoPointPlot(GeoPlot, PointPlot):

    _project_operation = project_points


class GeoVectorFieldPlot(GeoPlot, VectorFieldPlot):

    _project_operation = project_points


class GeoQuadMeshPlot(GeoPlot, QuadMeshPlot):

    _project_operation = project_quadmesh


class GeoRasterPlot(GeoPlot, RasterPlot):

    clipping_colors = param.Dict(default={'NaN': (0, 0, 0, 0)}, doc="""
        Dictionary to specify colors for clipped values, allows
        setting color for NaN values and for values above and below
        the min and max value. The min, max or NaN color may specify
        an RGB(A) color as a color hex string of the form #FFFFFF or
        #FFFFFFFF or a length 3 or length 4 tuple specifying values in
        the range 0-1 or a named HTML color.""")

    _project_operation = project_image.instance(fast=False)

    _hover_code = """
        var projections = require("core/util/projections");
        var x = special_vars.x
        var y = special_vars.y
        var coords = projections.wgs84_mercator.inverse([x, y])
        return "" + (coords[%d]).toFixed(4)
    """


class GeoRGBPlot(GeoPlot, RGBPlot):

    _project_operation = project_image.instance(fast=False)


class GeoPolygonPlot(GeoPlot, PolygonPlot):

    _project_operation = project_path


class GeoContourPlot(GeoPlot, ContourPlot):

    _project_operation = project_path


class GeoPathPlot(GeoPlot, PathPlot):

    _project_operation = project_path


class GeoGraphPlot(GeoPlot, GraphPlot):

    _project_operation = project_graph


class GeoTriMeshPlot(GeoPlot, TriMeshPlot):

    _project_operation = project_graph


class GeoShapePlot(GeoPolygonPlot):

    def get_data(self, element, ranges, style):
        if self.static_source:
            data = {}
        else:
            if self.geographic and element.crs != self.projection:
                element = project_shape(element, projection=self.projection)
            xs, ys = geom_to_array(element.geom()).T
            if self.invert_axes: xs, ys = ys, xs
            data = dict(xs=[xs], ys=[ys])

        mapping = dict(self._mapping)
        dim = element.vdims[0].name if element.vdims else None
        if element.level is not None:
            cmap = style.get('palette', style.get('cmap', None))
            if cmap and dim:
                cdim = element.vdims[0]
                dim_name = util.dimension_sanitizer(cdim.name)
                cmapper = self._get_colormapper(cdim, element, ranges, style)
                data[dim_name] = [element.level]
                mapping['fill_color'] = {'field': dim_name,
                                         'transform': cmapper}

        if 'hover' in self.tools+self.default_tools:
            if dim:
                dim_name = util.dimension_sanitizer(dim)
                data[dim_name] = [element.level]
            for k, v in self.overlay_dims.items():
                dim = util.dimension_sanitizer(k.name)
                data[dim] = [v for _ in range(len(xs))]
        return data, mapping, style

    def _init_glyph(self, plot, mapping, properties):
        """
        Returns a Bokeh glyph object.
        """
        properties = mpl_to_bokeh(properties)
        if isinstance(self.current_frame.data, line_types):
            properties = {k: v for k, v in properties.items()
                          if 'fill_' not in k}
            plot_method = plot.multi_line
        else:
            plot_method = plot.patches
        renderer = plot_method(**dict(properties, **mapping))
        return renderer, renderer.glyph



class FeaturePlot(GeoPolygonPlot):

    scale = param.ObjectSelector(default='110m',
                                 objects=['10m', '50m', '110m'],
                                 doc="The scale of the Feature in meters.")

    def get_extents(self, element, ranges):
        """
        Subclasses the get_extents method using the GeoAxes
        set_extent method to project the extents to the
        Elements coordinate reference system.
        """
        proj = self.projection
        if self.global_extent:
            (x0, x1), (y0, y1) = proj.x_limits, proj.y_limits
            return (x0, y0, x1, y1)
        elif self.overlaid:
            return (np.NaN,)*4
        return super(FeaturePlot, self).get_extents(element, ranges)


    def get_data(self, element, ranges, style):
        mapping = dict(self._mapping)
        if self.static_source: return {}, mapping, style

        feature = copy.copy(element.data)
        feature.scale = self.scale
        geoms = list(feature.geometries())
        if isinstance(geoms[0], line_types):
            self._plot_methods = dict(single='multi_line')
        else:
            self._plot_methods = dict(single='patches', batched='patches')
        geoms = [self.projection.project_geometry(geom, element.crs)
                 for geom in geoms]

        arrays = []
        for geom in geoms:
            if geom == []:
                continue
            arrays.append(geom_to_array(geom).T)
        xs, ys = zip(*arrays) if arrays else ([], [])
        data = dict(xs=list(xs), ys=list(ys))
        return data, mapping, style


class GeoTextPlot(GeoPlot, TextPlot):

    def get_data(self, element, ranges, style):
        mapping = dict(x='x', y='y', text='text')
        if not self.geographic:
            return super(GeoTextPlot, self).get_data(element, ranges, style)
        if element.crs:
            x, y = self.projection.transform_point(element.x, element.y,
                                                   element.crs)
        return (dict(x=[x], y=[y], text=[element.text]), mapping, style)

    def get_extents(self, element, ranges=None):
        return None, None, None, None


class GeoLabelsPlot(GeoPlot, LabelsPlot):

    _project_operation = project_points


class geo_hex_binning(hex_binning, project_points):
    """
    Applies hex binning by computing aggregates on a hexagonal grid.

    Should not be user facing as the returned element is not directly
    useable.
    """

    def _process(self, element, key=None):
        if isinstance(element, HexTiles):
            element = project_points._process(self, element)
        return hex_binning._process(self, element)

compositor = Compositor(
    "HexTiles", geo_hex_binning, None, 'data', output_type=HexTiles,
    transfer_options=True, transfer_parameters=True, backends=['bokeh']
)
Compositor.register(compositor)


Store.register({WMTS: TilePlot,
                Points: GeoPointPlot,
                Labels: GeoLabelsPlot,
                VectorField: GeoVectorFieldPlot,
                Polygons: GeoPolygonPlot,
                Contours: GeoContourPlot,
                Path: GeoPathPlot,
                Shape: GeoShapePlot,
                Image: GeoRasterPlot,
                RGB: GeoRGBPlot,
                Feature: FeaturePlot,
                HexTiles: HexTilesPlot,
                Text: GeoTextPlot,
                Overlay: GeoOverlayPlot,
                NdOverlay: GeoOverlayPlot,
                Graph: GeoGraphPlot,
                TriMesh: GeoTriMeshPlot,
                Nodes: GeoPointPlot,
                EdgePaths: GeoPathPlot,
                QuadMesh: GeoQuadMeshPlot}, 'bokeh')

options = Store.options(backend='bokeh')

options.Feature = Options('style', line_color='black')
options.Feature.Coastline = Options('style', line_width=0.5)
options.Feature.Borders = Options('style', line_width=0.5)
options.Feature.Rivers = Options('style', line_color='blue')
options.Feature.Land   = Options('style', fill_color='#efefdb', line_color='#efefdb')
options.Feature.Ocean  = Options('style', fill_color='#97b6e1', line_color='#97b6e1')
options.Feature.Lakes  = Options('style', fill_color='#97b6e1', line_color='#97b6e1')
options.Feature.Rivers = Options('style', line_color='#97b6e1')
options.Shape = Options('style', line_color='black', fill_color='#30A2DA')
