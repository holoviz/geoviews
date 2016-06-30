import numpy as np
from cartopy.crs import GOOGLE_MERCATOR

from holoviews import Store
from holoviews.plotting.util import map_colors
from holoviews.plotting.bokeh.element import ElementPlot
from holoviews.plotting.bokeh.chart import PointPlot
from holoviews.plotting.bokeh.path import PolygonPlot, PathPlot
from holoviews.plotting.bokeh.util import get_cmap

from ...element import (WMTS, Points, Polygons, Path, Shape, is_geographic)
from ..util import project_extents, path_to_geom, polygon_to_geom, geom_to_array

DEFAULT_PROJ = GOOGLE_MERCATOR

class GeoPlot(ElementPlot):
    """
    Plotting baseclass for geographic plots with a cartopy projection.
    """

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
            return (np.NaN,)*4
        return project_extents(extents, element.crs, DEFAULT_PROJ)


class TilePlot(GeoPlot):

    styl_opts = ['alpha', 'render_parents']
    
    def get_data(self, element, ranges=None, empty=False):
        return {}, {'tile_source': element.data}
    
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
        dims = element.dimensions(label=True)
        points = DEFAULT_PROJ.transform_points(element.crs, data[dims[0]],
                                               data[dims[1]])
        data[dims[0]] = points[:, 0]
        data[dims[1]] = points[:, 1]
        return data, mapping


class GeometryPlot(GeoPlot):
    """
    Geometry projects a geometry to the destination coordinate
    reference system before creating the glyph.
    """

    def get_data(self, element, ranges=None, empty=False):
        data, mapping = super(GeometryPlot, self).get_data(element, ranges, empty)
        if not self.geographic:
            return data, mapping
        geoms = DEFAULT_PROJ.project_geometry(element.geom(), element.crs)
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
        if getattr(element, 'crs', None):
            geoms = DEFAULT_PROJ.project_geometry(geoms, element.crs)
        xs, ys = ([], []) if empty else geom_to_array(geoms)
        data = dict(xs=xs, ys=ys)

        style = self.style[self.cyclic_index]
        cmap = style.get('palette', style.get('cmap', None))
        mapping = dict(self._mapping)
        if cmap and element.level is not None:
            cmap = get_cmap(cmap)
            colors = map_colors(np.array([element.level]),
                                ranges[element.vdims[0].name], cmap)
            mapping['color'] = 'color'
            data['color'] = [] if empty else list(colors)*len(element.data)

        return data, mapping



Store.register({WMTS: TilePlot,
                Points: GeoPointPlot,
                Polygons: GeoPolygonPlot,
                Path: GeoPathPlot,
                Shape: GeoShapePlot}, 'bokeh')
