import copy

import param
import numpy as np
from cartopy.crs import GOOGLE_MERCATOR
from bokeh.models import WMTSTileSource, BBoxTileSource, QUADKEYTileSource, SaveTool

from holoviews import Store, Overlay, NdOverlay
from holoviews.core import util
from holoviews.core.options import SkipRendering, Options, Compositor
from holoviews.plotting.bokeh.annotation import TextPlot, LabelsPlot
from holoviews.plotting.bokeh.chart import PointPlot, VectorFieldPlot
from holoviews.plotting.bokeh.geometry import RectanglesPlot, SegmentPlot
from holoviews.plotting.bokeh.graphs import TriMeshPlot, GraphPlot
from holoviews.plotting.bokeh.hex_tiles import hex_binning, HexTilesPlot
from holoviews.plotting.bokeh.path import PolygonPlot, PathPlot, ContourPlot
from holoviews.plotting.bokeh.raster import RasterPlot, RGBPlot, QuadMeshPlot

from ...element import (
    WMTS, Points, Polygons, Path, Contours, Shape, Image, Feature,
    Text, RGB, Nodes, EdgePaths, Graph, TriMesh, QuadMesh, VectorField,
    Labels, HexTiles, LineContours, FilledContours, Rectangles, Segments
)
from ...operation import (
    project_image, project_points, project_path, project_graph,
    project_quadmesh, project_geom
)
from ...tile_sources import _ATTRIBUTIONS
from ...util import poly_types, line_types
from .plot import GeoPlot, GeoOverlayPlot
from . import callbacks # noqa


class TilePlot(GeoPlot):

    style_opts = ['alpha', 'render_parents', 'level', 'smoothing', 'min_zoom', 'max_zoom']

    def get_extents(self, element, ranges, range_type='combined'):
        extents = super().get_extents(element, ranges, range_type)
        if (not self.overlaid and all(e is None or not np.isfinite(e) for e in extents)
            and range_type in ('combined', 'data')):
            (x0, x1), (y0, y1) = GOOGLE_MERCATOR.x_limits, GOOGLE_MERCATOR.y_limits
            global_extent = (x0, y0, x1, y1)
            return global_extent
        return extents

    def get_data(self, element, ranges, style):
        if not isinstance(element.data, str):
            SkipRendering("WMTS element data must be a URL string, "
                          "bokeh cannot render %r" % element.data)
        if '{Q}' in element.data.upper():
            tile_source = QUADKEYTileSource
        elif all(kw in element.data.upper() for kw in ('{XMIN}', '{XMAX}', '{YMIN}', '{YMAX}')):
            tile_source = BBoxTileSource
        elif all(kw in element.data.upper() for kw in ('{X}', '{Y}', '{Z}')):
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

    def _update_glyph(self, renderer, properties, mapping, glyph, source=None, data=None):
        glyph.url = mapping['tile_source'].url
        glyph.update(**{k: v for k, v in properties.items()
                           if k in glyph.properties()})
        renderer.update(**{k: v for k, v in properties.items()
                           if k in renderer.properties()})

    def _init_glyph(self, plot, mapping, properties):
        """
        Returns a Bokeh glyph object.
        """
        tile_source = mapping['tile_source']
        level = properties.pop('level', 'underlay')
        renderer = plot.add_tile(tile_source, level=level)
        renderer.alpha = properties.get('alpha', 1)

        # Remove save tool
        plot.tools = [t for t in plot.tools if not isinstance(t, SaveTool)]
        return renderer, tile_source


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
        var projections = Bokeh.require("core/util/projections");
        var x = special_vars.x
        var y = special_vars.y
        var coords = projections.wgs84_mercator.invert(x, y)
        return "" + (coords[%d]).toFixed(4)
    """


class GeoRGBPlot(GeoPlot, RGBPlot):

    _project_operation = project_image.instance(fast=False)


class GeoPolygonPlot(GeoPlot, PolygonPlot):

    _project_operation = project_path


class GeoContourPlot(GeoPlot, ContourPlot):

    _project_operation = project_path


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


class GeoPathPlot(GeoPlot, PathPlot):

    _project_operation = project_path


class GeoGraphPlot(GeoPlot, GraphPlot):

    _project_operation = project_graph


class GeoTriMeshPlot(GeoPlot, TriMeshPlot):

    _project_operation = project_graph


class GeoRectanglesPlot(GeoPlot, RectanglesPlot):

    _project_operation = project_geom


class GeoSegmentsPlot(GeoPlot, SegmentPlot):

    _project_operation = project_geom


class GeoShapePlot(GeoPolygonPlot):

    def get_data(self, element, ranges, style):
        if not isinstance(element.data['geometry'], poly_types):
            style['fill_alpha'] = 0
        if isinstance(element.data['geometry'], line_types):
            el_type = Contours
            style['plot_method'] = 'multi_line'
            style.pop('fill_color', None)
            style.pop('fill_alpha', None)
        else:
            el_type = Polygons
        polys = el_type([element.data], crs=element.crs, **util.get_param_values(element))
        return super().get_data(polys, ranges, style)


class FeaturePlot(GeoPolygonPlot):

    scale = param.ObjectSelector(default='110m',
                                 objects=['10m', '50m', '110m'],
                                 doc="The scale of the Feature in meters.")

    def get_extents(self, element, ranges, range_type='combined'):
        proj = self.projection
        if self.global_extent and range_type in ('combined', 'data'):
            (x0, x1), (y0, y1) = proj.x_limits, proj.y_limits
            return tuple(round(c, 12) for c in (x0, y0, x1, y1))
        elif self.overlaid:
            return (np.NaN,)*4
        return super().get_extents(element, ranges, range_type)

    def get_data(self, element, ranges, style):
        mapping = dict(self._mapping)
        if self.static_source: return {}, mapping, style
        if hasattr(element.data, 'with_scale'):
            feature = element.data.with_scale(self.scale)
        else:
            feature = copy.copy(element.data)
            feature.scale = self.scale
        geoms = list(feature.geometries())
        if isinstance(geoms[0], line_types):
            el_type = Contours
            style['plot_method'] = 'multi_line'
            style.pop('fill_color', None)
            style.pop('fill_alpha', None)
        else:
            el_type = Polygons
        polys = el_type(geoms, crs=element.crs, **util.get_param_values(element))
        return super().get_data(polys, ranges, style)



class GeoTextPlot(GeoPlot, TextPlot):

    def get_data(self, element, ranges, style):
        mapping = dict(x='x', y='y', text='text')
        if not self.geographic:
            return super().get_data(element, ranges, style)
        if element.crs:
            x, y = self.projection.transform_point(element.x, element.y,
                                                   element.crs)
        return (dict(x=[x], y=[y], text=[element.text]), mapping, style)


class GeoLabelsPlot(GeoPlot, LabelsPlot):

    _project_operation = project_points


class geo_hex_binning(hex_binning, project_points):
    """
    Applies hex binning by computing aggregates on a hexagonal grid.

    Should not be user facing as the returned element is not directly
    usable.
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
                Rectangles: GeoRectanglesPlot,
                Segments: GeoSegmentsPlot,
                Path: GeoPathPlot,
                Shape: GeoShapePlot,
                Image: GeoRasterPlot,
                RGB: GeoRGBPlot,
                LineContours: LineContourPlot,
                FilledContours: FilledContourPlot,
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
options.Feature.Grid = Options('style', line_width=0.5, alpha=0.5, line_color='gray')
options.Shape = Options('style', line_color='black', fill_color='#30A2DA')
