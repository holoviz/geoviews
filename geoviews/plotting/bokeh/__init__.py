import copy
import itertools

import param
import numpy as np
import shapely.geometry
from cartopy.crs import GOOGLE_MERCATOR
from bokeh.models import WMTSTileSource

from holoviews import Store
from holoviews.core import util
from holoviews.core.options import SkipRendering, Options
from holoviews.plotting.bokeh.annotation import TextPlot
from holoviews.plotting.bokeh.element import ElementPlot
from holoviews.plotting.bokeh.chart import PointPlot
from holoviews.plotting.bokeh.path import PolygonPlot, PathPlot
from holoviews.plotting.bokeh.raster import RasterPlot

from ...element import (WMTS, Points, Polygons, Path, Shape, Image,
                        Feature, is_geographic, Text)
from ...operation import project_image
from ...util import project_extents, geom_to_array

DEFAULT_PROJ = GOOGLE_MERCATOR

line_types = (shapely.geometry.MultiLineString, shapely.geometry.LineString)
poly_types = (shapely.geometry.MultiPolygon, shapely.geometry.Polygon)


class GeoPlot(ElementPlot):
    """
    Plotting baseclass for geographic plots with a cartopy projection.
    """

    show_grid = param.Boolean(default=False)

    def __init__(self, element, **params):
        super(GeoPlot, self).__init__(element, **params)
        self.geographic = is_geographic(self.hmap.last)

    def get_extents(self, element, ranges):
        """
        Subclasses the get_extents method using the GeoAxes
        set_extent method to project the extents to the
        Elements coordinate reference system.
        """
        extents = super(GeoPlot, self).get_extents(element, ranges)
        if not getattr(element, 'crs', None):
            return extents
        elif any(e is None or not np.isfinite(e) for e in extents):
            extents = None
        else:
            try:
                extents = project_extents(extents, element.crs, DEFAULT_PROJ)
            except:
                extents = None
        return (np.NaN,)*4 if not extents else extents


class TilePlot(GeoPlot):

    styl_opts = ['alpha', 'render_parents']

    def get_data(self, element, ranges=None, empty=False):
        tile_sources = [ts for ts in element.data
                        if isinstance(ts, WMTSTileSource)]
        if not tile_sources:
            raise SkipRendering("No valid WMTSTileSource found in WMTS "
                                "Element, rendering skipped.")
        return {}, {'tile_source': tile_sources[0]}

    def _init_glyph(self, plot, mapping, properties):
        """
        Returns a Bokeh glyph object.
        """
        renderer = plot.add_tile(mapping['tile_source'])
        return renderer, renderer


class GeoPointPlot(GeoPlot, PointPlot):

    def get_data(self, *args, **kwargs):
        data, mapping = super(GeoPointPlot, self).get_data(*args, **kwargs)
        element = args[0]
        xdim, ydim = element.dimensions('key', label=True)
        if len(data[xdim]) and element.crs not in [DEFAULT_PROJ, None]:
            points = DEFAULT_PROJ.transform_points(element.crs, data[xdim],
                                                   data[ydim])
            data[xdim] = points[:, 0]
            data[ydim] = points[:, 1]
        return data, mapping


class GeoRasterPlot(GeoPlot, RasterPlot):

    def get_data(self, element, ranges=None, empty=False):
        l, b, r, t = self.get_extents(element, ranges)
        if self.geographic:
            element = project_image(element, projection=DEFAULT_PROJ)
        img = element.dimension_values(2, flat=False)
        mapping = dict(image='image', x='x', y='y', dw='dw', dh='dh')
        if empty:
            data = dict(image=[], x=[], y=[], dw=[], dh=[])
        else:
            dh = t-b
            data = dict(image=[img], x=[l],
                        y=[b], dw=[r-l], dh=[dh])
        return (data, mapping)


class GeometryPlot(GeoPlot):
    """
    Geometry projects a geometry to the destination coordinate
    reference system before creating the glyph.
    """

    def get_data(self, element, ranges=None, empty=False):
        data, mapping = super(GeometryPlot, self).get_data(element, ranges, empty)
        if not self.geographic:
            return data, mapping
        geoms = element.geom()
        if element.crs:
            geoms = DEFAULT_PROJ.project_geometry(geoms, element.crs)
        xs, ys = geom_to_array(geoms)
        data['xs'] = xs
        data['ys'] = ys
        return data, mapping


class GeoPolygonPlot(GeometryPlot, PolygonPlot):
    pass


class GeoPathPlot(GeometryPlot, PathPlot):
    pass


class GeoShapePlot(GeoPolygonPlot):

    def get_data(self, element, ranges=None, empty=False):
        geoms = element.geom()
        if self.geographic and element.crs != DEFAULT_PROJ:
            try:
                geoms = DEFAULT_PROJ.project_geometry(geoms, element.crs)
            except:
                empty = True
        xs, ys = ([], []) if empty else geom_to_array(geoms)
        data = dict(xs=xs, ys=ys)

        style = self.style[self.cyclic_index]
        cmap = style.get('palette', style.get('cmap', None))
        mapping = dict(self._mapping)
        dim = element.vdims[0].name if element.vdims else None
        if cmap and dim and element.level is not None:
            cdim = element.vdims[0]
            cmapper = self._get_colormapper(cdim, element, ranges, style)
            data[cdim.name] = [] if empty else element.dimension_values(2)
            mapping['fill_color'] = {'field': cdim.name,
                                     'transform': cmapper}

        if 'hover' in self.tools+self.default_tools:
            if dim:
                dim_name = util.dimension_sanitizer(dim)
                data[dim_name] = [element.level for _ in range(len(xs))]
            for k, v in self.overlay_dims.items():
                dim = util.dimension_sanitizer(k.name)
                data[dim] = [v for _ in range(len(xs))]
        return data, mapping


class FeaturePlot(GeoPolygonPlot):

    scale = param.ObjectSelector(default='110m',
                                 objects=['10m', '50m', '110m'],
                                 doc="The scale of the Feature in meters.")

    def get_data(self, element, ranges, empty=[]):
        feature = copy.copy(element.data)
        feature.scale = self.scale
        geoms = list(feature.geometries())
        if isinstance(geoms[0], line_types):
            self._plot_methods = dict(single='multi_line')
        else:
            self._plot_methods = dict(single='patches', batched='patches')
        geoms = [DEFAULT_PROJ.project_geometry(geom, element.crs)
                 for geom in geoms]
        arrays = [geom_to_array(geom) for geom in geoms]
        xs = [arr[0] for arr in arrays]
        ys = [arr[1] for arr in arrays]
        data = dict(xs=list(itertools.chain(*xs)),
                    ys=list(itertools.chain(*ys)))
        return data, dict(self._mapping)


class GeoTextPlot(GeoPlot, TextPlot):

    def get_data(self, element, ranges=None, empty=False):
        mapping = dict(x='x', y='y', text='text')
        if empty or not self.geographic:
            return super(GeoTextPlot, self).get_data(element, ranges, empty)
        if element.crs:
            x, y = DEFAULT_PROJ.transform_point(element.x, element.y,
                                                element.crs)
        return (dict(x=[x], y=[y], text=[element.text]), mapping)

    def get_extents(self, element, ranges=None):
        return None, None, None, None



Store.register({WMTS: TilePlot,
                Points: GeoPointPlot,
                Polygons: GeoPolygonPlot,
                Path: GeoPathPlot,
                Shape: GeoShapePlot,
                Image: GeoRasterPlot,
                Feature: FeaturePlot,
                Text: GeoTextPlot}, 'bokeh')

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

