import copy

import param
import numpy as np
import shapely.geometry
from cartopy.crs import GOOGLE_MERCATOR
from bokeh.models import WMTSTileSource, MercatorTickFormatter, MercatorTicker
from bokeh.models.tools import BoxZoomTool

from holoviews import Store, Overlay, NdOverlay
from holoviews.core import util
from holoviews.core.options import SkipRendering, Options
from holoviews.plotting.bokeh.annotation import TextPlot
from holoviews.plotting.bokeh.element import ElementPlot, OverlayPlot as HvOverlayPlot
from holoviews.plotting.bokeh.chart import PointPlot
from holoviews.plotting.bokeh.path import PolygonPlot, PathPlot, ContourPlot
from holoviews.plotting.bokeh.raster import RasterPlot

from ...element import (WMTS, Points, Polygons, Path, Contours, Shape, Image,
                        Feature, is_geographic, Text, _Element)
from ...operation import project_image, project_shape, project_points, project_path
from ...util import project_extents, geom_to_array

DEFAULT_PROJ = GOOGLE_MERCATOR

try:
    # Handle updating of ticker and formatter in holoviews<1.9.0
    from holoviews.plotting.bokeh.util import IGNORED_MODELS
    IGNORED_MODELS += ['MercatorTicker', 'MercatorTickFormatter']
except:
    pass

line_types = (shapely.geometry.MultiLineString, shapely.geometry.LineString)
poly_types = (shapely.geometry.MultiPolygon, shapely.geometry.Polygon)


class GeoPlot(ElementPlot):
    """
    Plotting baseclass for geographic plots with a cartopy projection.
    """

    default_tools = param.List(default=['save', 'pan', 'wheel_zoom',
                                        BoxZoomTool(match_aspect=True), 'reset'],
        doc="A list of plugin tools to use on the plot.")

    show_grid = param.Boolean(default=False, doc="""
        Whether to show gridlines on the plot.""")

    # Project operation to apply to the element
    _project_operation = None

    def __init__(self, element, **params):
        super(GeoPlot, self).__init__(element, **params)
        self.geographic = is_geographic(self.hmap.last)


    def _axis_properties(self, axis, key, plot, dimension=None,
                         ax_mapping={'x': 0, 'y': 1}):
        axis_props = super(GeoPlot, self)._axis_properties(axis, key, plot,
                                                           dimension, ax_mapping)
        if self.geographic:
            dimension = 'lon' if axis == 'x' else 'lat'
            axis_props['ticker'] = MercatorTicker(dimension=dimension)
            axis_props['formatter'] = MercatorTickFormatter(dimension=dimension)
        return axis_props


    def get_extents(self, element, ranges):
        """
        Subclasses the get_extents method using the GeoAxes
        set_extent method to project the extents to the
        Elements coordinate reference system.
        """
        extents = super(GeoPlot, self).get_extents(element, ranges)
        if not getattr(element, 'crs', None) or not self.geographic:
            return extents
        elif any(e is None or not np.isfinite(e) for e in extents):
            extents = None
        else:
            try:
                extents = project_extents(extents, element.crs, DEFAULT_PROJ)
            except:
                extents = None
        return (np.NaN,)*4 if not extents else extents


    def get_data(self, element, ranges, style):
        if self._project_operation and self.geographic and element.crs != DEFAULT_PROJ:
            element = self._project_operation(element)
        return super(GeoPlot, self).get_data(element, ranges, style)


class OverlayPlot(GeoPlot, HvOverlayPlot):
    """
    Subclasses the HoloViews OverlayPlot to add custom behavior
    for geographic plots.
    """

    def __init__(self, element, **params):
        super(OverlayPlot, self).__init__(element, **params)
        self.geographic = any(element.traverse(is_geographic, [_Element]))
        if self.geographic:
            self.show_grid = False


class TilePlot(GeoPlot):

    style_opts = ['alpha', 'render_parents', 'level']

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

    _project_operation = project_image


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
            xs, ys = geom_to_array(project_shape(element).geom()).T
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
