import param
import iris.plot as iplt
from cartopy import crs
from holoviews.core import Store, HoloMap
from holoviews.plotting.mpl import (ElementPlot, ColorbarPlot, PointPlot,
                                    OverlayPlot)

from ..element import (GeoContour, GeoImage, GeoPoints, GeoFeature,
                       WMTS, GeoTiles)


class GeoPlot(ElementPlot):
    """
    Plotting baseclass for geographic plots with a cartopy projection.
    """

    projection = param.Parameter(default=crs.PlateCarree())
    
    def __init__(self, element, **params):
        if 'projection' not in params:
            el = element.last if isinstance(element, HoloMap) else element
            params['projection'] = el.crs
        super(GeoPlot, self).__init__(element, **params)
        self.aspect = 'equal'
        self.apply_ranges = False

    def teardown_handles(self):
        if self.zorder == 0:
            self.handles['axis'].cla()
    
    
class GeoContoursPlot(GeoPlot, ColorbarPlot):
    
    style_opts = ['antialiased', 'alpha', 'cmap']
    
    def get_data(self, element, ranges, style):
        args = (element.data,)
        if isinstance(element.levels, int):
            args += (element.levels,)
        else:
            style['levels'] = element.levels
        return args, style, {}
    
    def init_artists(self, ax, plot_args, plot_kwargs):
        artists = {'artist': iplt.contourf(*plot_args, axes=ax, **plot_kwargs)}
        return artists
    

class GeoImagePlot(GeoPlot, ColorbarPlot):

    style_opts = ['alpha', 'cmap', 'interpolation', 'visible',
                  'filterrad', 'clims', 'norm']

    def get_data(self, element, ranges, style):
        self._norm_kwargs(element, ranges, style, element.vdims[0])
        return (element.data,), style, {}
    
    def init_artists(self, ax, plot_args, plot_kwargs):
        return {'artist': iplt.pcolormesh(*plot_args, axes=ax, **plot_kwargs)}


class GeoPointPlot(GeoPlot, PointPlot):
    
    def get_data(self, element, ranges, style):
        args, style, axis_kwargs = super(GeoPointPlot, self).get_data(element, ranges, style)
        style['transform'] = element.crs
        return args, style, axis_kwargs


########################################
#  Geographic features and annotations #
########################################

    
class GeoFeaturePlot(GeoPlot):
    
    def get_data(self, element, ranges, style):
        return (element.data,), style, {}

    def init_artists(self, ax, plot_args, plot_kwargs):
        return {'artist': ax.add_feature(*plot_args)}


class WMTSPlot(GeoPlot):
    
    def get_data(self, element, ranges, style):
        return element.data, style, {}

    def init_artists(self, ax, plot_args, plot_kwargs):
        return {'artist': ax.add_wmts(*plot_args)}    
    

class GeoTilePlot(GeoPlot):
    
    def get_data(self, element, ranges, style):
        return (element.data, element.zoom), style, {}

    def init_artists(self, ax, plot_args, plot_kwargs):
        return {'artist': ax.add_image(*plot_args)}
    

# Register plots with HoloViews
Store.register({GeoContour: GeoContoursPlot,
                GeoImage: GeoImagePlot,
                GeoFeature: GeoFeaturePlot,
                WMTS: WMTSPlot,
                GeoTiles: GeoTilePlot,
                GeoPoints: GeoPointPlot}, 'matplotlib')


# Define plot and style options
opts = Store.options(backend='matplotlib')
OverlayPlot.aspect = 'equal'
