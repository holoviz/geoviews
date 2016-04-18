import copy

import param
import iris.plot as iplt
from cartopy import crs as ccrs
from holoviews.core import (Store, HoloMap, Layout, Overlay,
                            CompositeOverlay, Element)
from holoviews.plotting.mpl import (ElementPlot, ColorbarPlot, PointPlot,
                                    AnnotationPlot, TextPlot,
                                    LayoutPlot as HvLayoutPlot,
                                    OverlayPlot as HvOverlayPlot)

from ..element import (Contours, Image, Points, GeoFeature,
                       WMTS, GeoTiles, Text, util)


def _get_projection(el):
    """
    Get coordinate reference system from non-auxiliary elements.
    Return value is a tuple of a precedence integer and the projection,
    to allow non-auxiliary components to take precedence.
    """
    return (int(el._auxiliary_component), el.crs) if hasattr(el, 'crs') else None


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
                              if p is not None])
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


class GeoPlot(ProjectionPlot, ElementPlot):
    """
    Plotting baseclass for geographic plots with a cartopy projection.
    """

    projection = param.Parameter(default=ccrs.PlateCarree())

    def __init__(self, element, **params):
        if 'projection' not in params:
            el = element.last if isinstance(element, HoloMap) else element
            params['projection'] = el.crs
        super(GeoPlot, self).__init__(element, **params)
        self.aspect = 'equal'
        self.apply_ranges = False

    def teardown_handles(self):
        """
        Delete artist handle so it can be redrawn.
        """
        try:
            self.handles['artist'].remove()
        except ValueError:
            pass


class GeoContourPlot(GeoPlot, ColorbarPlot):
    """
    Draws a contour or contourf plot from the data in
    a Contours.
    """

    filled = param.Boolean(default=True, doc="""
        Whether to draw filled or unfilled contours""")

    levels = param.ClassSelector(default=5, class_=(int, list))

    style_opts = ['antialiased', 'alpha', 'cmap']
    
    def get_data(self, element, ranges, style):
        args = (element.data.copy(),)
        if isinstance(self.levels, int):
            args += (self.levels,)
        else:
            style['levels'] = self.levels
        return args, style, {}

    def init_artists(self, ax, plot_args, plot_kwargs):
        plotfn = iplt.contourf if self.filled else iplt.contour
        artists = {'artist': plotfn(*plot_args, axes=ax, **plot_kwargs)}
        return artists

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
    

class GeoImagePlot(GeoPlot, ColorbarPlot):

    """
    Draws a pcolormesh plot from the data in a Image Element.
    """

    style_opts = ['alpha', 'cmap', 'visible', 'filterrad', 'clims', 'norm']

    def get_data(self, element, ranges, style):
        self._norm_kwargs(element, ranges, style, element.vdims[0])
        style.pop('interpolation')
        return (element.data.copy(),), style, {}

    def init_artists(self, ax, plot_args, plot_kwargs):
        return {'artist': iplt.pcolormesh(*plot_args, axes=ax, **plot_kwargs)}



class GeoPointPlot(GeoPlot, PointPlot):
    """
    Draws a scatter plot from the data in a Points Element.
    """
    
    def get_data(self, element, ranges, style):
        data = super(GeoPointPlot, self).get_data(element, ranges, style)
        args, style, axis_kwargs = data
        style['transform'] = element.crs
        return args, style, axis_kwargs


########################################
#  Geographic features and annotations #
########################################

    
class GeoFeaturePlot(GeoPlot):
    """
    Draws a feature from a GeoFeatures Element.
    """

    scale = param.ObjectSelector(default='110m', objects=['10m', '50m', '110m'],
                                 doc="The scale of the GeoFeature in meters.")

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
    

class GeoTilePlot(GeoPlot):
    """
    Draws image tiles specified by a GeoTiles Element.
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
        handles = self.draw_annotation(axis, annotation.data, annotation.crs, opts)
        self.handles['annotations'] = handles
        return self._finalize_axis(key, ranges=ranges)

    def update_handles(self, key, axis, annotation, ranges, style):
        # Clear all existing annotations
        for element in self.handles['annotations']:
            element.remove()

        self.handles['annotations'] = self.draw_annotation(axis,
                                                           annotation.data,
                                                           annotation.crs, style)


class GeoTextPlot(GeoAnnotationPlot, TextPlot):
    "Draw the Text annotation object"

    def draw_annotation(self, axis, data, crs, opts):
        (x,y, text, fontsize,
         horizontalalignment, verticalalignment, rotation) = data
        opts['fontsize'] = fontsize
        x, y = axis.projection.transform_point(x, y, src_crs=crs)
        return [axis.text(x, y, text,
                          horizontalalignment=horizontalalignment,
                          verticalalignment=verticalalignment,
                          rotation=rotation, **opts)]



# Register plots with HoloViews
Store.register({Contours: GeoContourPlot,
                Image: GeoImagePlot,
                GeoFeature: GeoFeaturePlot,
                WMTS: WMTSPlot,
                GeoTiles: GeoTilePlot,
                Points: GeoPointPlot,
                Text: GeoTextPlot,
                Layout: LayoutPlot,
                Overlay: OverlayPlot}, 'matplotlib')


# Define plot and style options
opts = Store.options(backend='matplotlib')
OverlayPlot.aspect = 'equal'
