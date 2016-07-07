import copy

import numpy as np
import param
import iris.plot as iplt
from cartopy import crs as ccrs
from holoviews.core import (Store, HoloMap, Layout, Overlay,
                            CompositeOverlay, Element)
from holoviews.core import util
from holoviews.core.options import SkipRendering
from holoviews.plotting.mpl import (ElementPlot, ColorbarPlot, PointPlot,
                                    AnnotationPlot, TextPlot,
                                    LayoutPlot as HvLayoutPlot,
                                    OverlayPlot as HvOverlayPlot,
                                    PathPlot, PolygonPlot)


from ...element import (Image, Points, Feature, WMTS, Tiles, Text,
                        LineContours, FilledContours, is_geographic,
                        Path, Polygons, Shape)
from ...util import path_to_geom, polygon_to_geom


def _get_projection(el):
    """
    Get coordinate reference system from non-auxiliary elements.
    Return value is a tuple of a precedence integer and the projection,
    to allow non-auxiliary components to take precedence.
    """
    result = None
    if hasattr(el, 'crs'):
        result = (int(el._auxiliary_component), el.crs)
    return result


class ProjectionPlot(object):
    """
    Implements custom _get_projection method to make the coordinate
    reference system available to HoloViews plots as a projection.
    """

    def _get_projection(cls, obj):
        # Look up custom projection in options
        isoverlay = lambda x: isinstance(x, CompositeOverlay)
        opts = cls._traverse_options(obj, 'plot', ['projection'],
                                     [CompositeOverlay, Element],
                                     keyfn=isoverlay, defaults=False)
        from_overlay = not all(p is None for p in opts[True]['projection'])
        projections = opts[from_overlay]['projection']
        custom_projs = [p for p in projections if p is not None]
        if len(set([type(p) for p in custom_projs])) > 1:
            raise Exception("An axis may only be assigned one projection type")
        elif custom_projs:
            return custom_projs[0]

        # If no custom projection is supplied traverse object to get
        # the custom projections and sort by precedence
        projections = sorted([p for p in obj.traverse(_get_projection, [Element])
                              if p is not None and p[1] is not None])
        if projections:
            return projections[0][1]
        else:
            return None


class LayoutPlot(ProjectionPlot, HvLayoutPlot):
    """
    Extends HoloViews LayoutPlot with functionality to determine
    the correct projection for each axis.
    """


class OverlayPlot(ProjectionPlot, HvOverlayPlot):
    """
    Extends HoloViews OverlayPlot with functionality to determine
    the correct projection for each axis.
    """

    def __init__(self, element, **params):
        super(OverlayPlot, self).__init__(element, **params)
        plot_opts = self.lookup_options(self.hmap.last, 'plot').options
        self.geographic = any(self.hmap.traverse(is_geographic, [Element]))
        if 'aspect' not in plot_opts and self.geographic:
            self.aspect = 'equal'



class GeoPlot(ProjectionPlot, ElementPlot):
    """
    Plotting baseclass for geographic plots with a cartopy projection.
    """

    apply_ranges = param.Boolean(default=False, doc="""
        Do not use ranges to compute plot extents by default.""")

    projection = param.Parameter(default=ccrs.PlateCarree())

    def __init__(self, element, **params):
        if 'projection' not in params:
            el = element.last if isinstance(element, HoloMap) else element
            params['projection'] = el.crs
        super(GeoPlot, self).__init__(element, **params)
        plot_opts = self.lookup_options(self.hmap.last, 'plot').options
        self.geographic = is_geographic(self.hmap.last)
        if 'aspect' not in plot_opts and self.geographic:
            self.aspect = 'equal'


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
            ax.autoscale_view()
        else:
            x0, x1, y0, y1 = extents
            ax.set_extent((x0, y0, x1, y1), element.crs)
        (l, r), (b, t) = ax.get_xlim(), ax.get_ylim()
        return l, b, r, t


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

    def get_data(self, element, ranges, style):
        args = (element.data.copy(),)
        if isinstance(self.levels, int):
            args += (self.levels,)
        else:
            style['levels'] = self.levels
        return args, style, {}

    def init_artists(self, ax, plot_args, plot_kwargs):
        return {'artist': iplt.contour(*plot_args, axes=ax, **plot_kwargs)}

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

    def init_artists(self, ax, plot_args, plot_kwargs):
        artists = {'artist': iplt.contourf(*plot_args, axes=ax, **plot_kwargs)}
        return artists


class GeoImagePlot(GeoPlot, ColorbarPlot):

    """
    Draws a pcolormesh plot from the data in a Image Element.
    """

    style_opts = ['alpha', 'cmap', 'visible', 'filterrad', 'clims', 'norm']

    def get_data(self, element, ranges, style):
        self._norm_kwargs(element, ranges, style, element.vdims[0])
        style.pop('interpolation')
        cube = element.data.copy()
        # Make sure both coordinates have bounds to avoid iris warning.
        for coord in cube.dim_coords:
            if not coord.has_bounds():
                coord.guess_bounds()
        return (cube,), style, {}

    def init_artists(self, ax, plot_args, plot_kwargs):
        return {'artist': iplt.pcolormesh(*plot_args, axes=ax, **plot_kwargs)}


class GeoPointPlot(GeoPlot, PointPlot):
    """
    Draws a scatter plot from the data in a Points Element.
    """

    apply_ranges = param.Boolean(default=True)

    def get_data(self, element, ranges, style):
        data = super(GeoPointPlot, self).get_data(element, ranges, style)
        args, style, axis_kwargs = data
        style['transform'] = element.crs
        return args, style, axis_kwargs


class GeometryPlot(GeoPlot):

    def init_artists(self, ax, plot_args, plot_kwargs):
        if self.geographic:
            artist = ax.add_geometries(*plot_args, **plot_kwargs)
            return {'artist': artist}
        else:
            return super(GeometryPlot, self).init_artist(ax, plot_args, plot_kwargs)


class GeoPathPlot(GeometryPlot, PathPlot):
    """
    Draws a scatter plot from the data in a Points Element.
    """

    apply_ranges = param.Boolean(default=True)

    def get_data(self, element, ranges, style):
        if self.geographic:
            return ([path_to_geom(element)], element.crs), style, {}
        else:
            return super(GeoPathPlot, self).get_data(element, ranges, style)


class GeoPolygonPlot(GeometryPlot, PolygonPlot):
    """
    Draws a scatter plot from the data in a Points Element.
    """

    apply_ranges = param.Boolean(default=True)

    def get_data(self, element, ranges, style):
        if self.geographic:
            vdim = element.vdims[0] if element.vdims else None
            value = element.level
            if vdim is not None and np.isfinite(value):
                self._norm_kwargs(element, ranges, style, vdim)
                style['clim'] = style.pop('vmin'), style.pop('vmax')
                style['array'] = np.array([value]*len(element.data))
            return ([polygon_to_geom(element)], element.crs), style, {}
        else:
            return super(GeoPolygonPlot, self).get_data(element, ranges, style)


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
                style['array'] = np.array([value]*len(element.data))
            return ([element.data], element.crs), style, {}
        else:
            SkipRendering('Shape can only be plotted on geographic plot, '
                          'supply a coordinate reference system.')

        
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

    style_opts = ['alpha', 'cmap', 'interpolation', 'visible',
                  'filterrad', 'clims', 'norm']

    def get_data(self, element, ranges, style):
        return (element.data, element.layer), style, {}

    def init_artists(self, ax, plot_args, plot_kwargs):
        return {'artist': ax.add_wmts(*plot_args, **plot_kwargs)}


class TilePlot(GeoPlot):
    """
    Draws image tiles specified by a Tiles Element.
    """

    zoom = param.Integer(default=8, doc="""
        Controls the zoom level of the tile source.""")

    style_opts = ['alpha', 'cmap', 'interpolation', 'visible',
                  'filterrad', 'clims', 'norm']

    def get_data(self, element, ranges, style):
        return (element.data, self.zoom), style, {}

    def init_artists(self, ax, plot_args, plot_kwargs):
        return {'artist': ax.add_image(*plot_args, **plot_kwargs)}


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
                Tiles: TilePlot,
                Points: GeoPointPlot,
                Text: GeoTextPlot,
                Layout: LayoutPlot,
                Overlay: OverlayPlot,
                Polygons: GeoPolygonPlot,
                Path: GeoPathPlot,
                Shape: GeoShapePlot}, 'matplotlib')


# Define plot and style options
opts = Store.options(backend='matplotlib')
