import copy

import param
import shapely.geometry
from bokeh.models import WMTSTileSource

from holoviews import Store, Overlay, NdOverlay
from holoviews.core import util
from holoviews.core.options import SkipRendering, Options
from holoviews.plotting.bokeh.annotation import TextPlot
from holoviews.plotting.bokeh.chart import PointPlot
from holoviews.plotting.bokeh.path import PolygonPlot, PathPlot, ContourPlot
from holoviews.plotting.bokeh.raster import RasterPlot, RGBPlot

from ...element import (WMTS, Points, Polygons, Path, Contours, Shape,
                        Image, Feature, Text, RGB)
from ...operation import project_image, project_shape, project_points, project_path
from ...util import geom_to_array
from .plot import GeoPlot, OverlayPlot, DEFAULT_PROJ
from . import callbacks # noqa

line_types = (shapely.geometry.MultiLineString, shapely.geometry.LineString)
poly_types = (shapely.geometry.MultiPolygon, shapely.geometry.Polygon)

class TilePlot(GeoPlot):

    style_opts = ['alpha', 'render_parents', 'level']

    def get_extents(self, element, ranges):
        extents = super(TilePlot, self).get_extents(element, ranges)
        if not self.overlaid:
            global_extent = (-20026376.39, -20048966.10, 20026376.39, 20048966.10)
            return util.max_extents([extents, global_extent])
        return extents

    def get_data(self, element, ranges, style):
        tile_source = None
        for url in element.data:
            if isinstance(url, util.basestring) and not url.endswith('cgi'):
                try:
                    tile_source = WMTSTileSource(url=url)
                    break
                except:
                    pass
            elif isinstance(url, WMTSTileSource):
                tile_source = url
                break

        if tile_source is None:
            raise SkipRendering("No valid tile source URL found in WMTS "
                                "Element, rendering skipped.")
        return {}, {'tile_source': tile_source}, style

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


class GeoRasterPlot(GeoPlot, RasterPlot):

    clipping_colors = param.Dict(default={'NaN': (0, 0, 0, 0)}, doc="""
        Dictionary to specify colors for clipped values, allows
        setting color for NaN values and for values above and below
        the min and max value. The min, max or NaN color may specify
        an RGB(A) color as a color hex string of the form #FFFFFF or
        #FFFFFFFF or a length 3 or length 4 tuple specifying values in
        the range 0-1 or a named HTML color.""")

    _project_operation = project_image.instance(fast=False)


class GeoRGBPlot(GeoPlot, RGBPlot):

    _project_operation = project_image.instance(fast=False)


class GeoPolygonPlot(GeoPlot, PolygonPlot):

    _project_operation = project_path


class GeoContourPlot(GeoPlot, ContourPlot):

    _project_operation = project_path


class GeoPathPlot(GeoPlot, PathPlot):

    _project_operation = project_path


class GeoShapePlot(GeoPolygonPlot):

    def get_data(self, element, ranges, style):
        if self.static_source:
            data = {}
        else:
            if self.geographic and element.crs != DEFAULT_PROJ:
                element = project_shape(element)
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


class FeaturePlot(GeoPolygonPlot):

    scale = param.ObjectSelector(default='110m',
                                 objects=['10m', '50m', '110m'],
                                 doc="The scale of the Feature in meters.")

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
        geoms = [DEFAULT_PROJ.project_geometry(geom, element.crs)
                 for geom in geoms]
        xs, ys = zip(*(geom_to_array(geom).T for geom in geoms))
        data = dict(xs=list(xs), ys=list(ys))
        return data, mapping, style


class GeoTextPlot(GeoPlot, TextPlot):

    def get_data(self, element, ranges, style):
        mapping = dict(x='x', y='y', text='text')
        if not self.geographic:
            return super(GeoTextPlot, self).get_data(element, ranges, style)
        if element.crs:
            x, y = DEFAULT_PROJ.transform_point(element.x, element.y,
                                                element.crs)
        return (dict(x=[x], y=[y], text=[element.text]), mapping, style)

    def get_extents(self, element, ranges=None):
        return None, None, None, None



Store.register({WMTS: TilePlot,
                Points: GeoPointPlot,
                Polygons: GeoPolygonPlot,
                Contours: GeoContourPlot,
                Path: GeoPathPlot,
                Shape: GeoShapePlot,
                Image: GeoRasterPlot,
                RGB: GeoRGBPlot,
                Feature: FeaturePlot,
                Text: GeoTextPlot,
                Overlay: OverlayPlot,
                NdOverlay: OverlayPlot}, 'bokeh')

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
