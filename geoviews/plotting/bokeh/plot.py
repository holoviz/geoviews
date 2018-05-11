"""
Module for geographic bokeh plot baseclasses.
"""

import param
import numpy as np

from cartopy.crs import GOOGLE_MERCATOR
from bokeh.models.tools import BoxZoomTool, WheelZoomTool
from bokeh.models import MercatorTickFormatter, MercatorTicker
from holoviews.plotting.bokeh.element import ElementPlot, OverlayPlot as HvOverlayPlot
from holoviews.plotting.bokeh.util import bokeh_version
from holoviews.core.util import dimension_sanitizer, basestring

from ...element import is_geographic, _Element
from ...util import project_extents

DEFAULT_PROJ = GOOGLE_MERCATOR

class GeoPlot(ElementPlot):
    """
    Plotting baseclass for geographic plots with a cartopy projection.
    """

    default_tools = param.List(default=['save', 'pan',
                                        WheelZoomTool(**({} if bokeh_version < '0.12.16' else
                                                         {'zoom_on_axis': False})),
                                        BoxZoomTool(match_aspect=True), 'reset'],
        doc="A list of plugin tools to use on the plot.")

    show_grid = param.Boolean(default=False, doc="""
        Whether to show gridlines on the plot.""")

    # Project operation to apply to the element
    _project_operation = None

    _hover_code = """
        var projections = require("core/util/projections");
        var x = special_vars.data_x
        var y = special_vars.data_y
        var coords = projections.wgs84_mercator.inverse([x, y])
        return "" + (coords[%d]).toFixed(4)
    """

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


    def _postprocess_hover(self, renderer, source):
        super(GeoPlot, self)._postprocess_hover(renderer, source)
        hover = self.handles.get('hover')
        try:
            from bokeh.models import CustomJSHover
        except:
            CustomJSHover = None
        if (not self.geographic or None in (hover, CustomJSHover) or
            isinstance(hover.tooltips, basestring)):
            return
        element = self.current_frame
        xdim, ydim = [dimension_sanitizer(kd.name) for kd in element.kdims]
        formatters, tooltips = {}, []
        xhover = CustomJSHover(code=self._hover_code % 0)
        yhover = CustomJSHover(code=self._hover_code % 1)
        for name, formatter in hover.tooltips:
            customjs = None
            if formatter in ('@{%s}' % xdim, '$x'):
                dim = xdim
                customjs = xhover
            elif formatter in ('@{%s}' % ydim, '$y'):
                dim = ydim
                customjs = yhover
            if customjs:
                key = formatter if formatter in ('$x', '$y') else dim
                formatters[key] = customjs
                formatter += '{custom}'
            tooltips.append((name, formatter))
        hover.tooltips = tooltips
        hover.formatters = formatters


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
