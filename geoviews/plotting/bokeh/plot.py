"""
Module for geographic bokeh plot baseclasses.
"""
import param

from cartopy.crs import GOOGLE_MERCATOR, PlateCarree, Mercator
from bokeh.models.tools import BoxZoomTool, WheelZoomTool
from bokeh.models import MercatorTickFormatter, MercatorTicker, CustomJSHover
from holoviews.core.dimension import Dimension
from holoviews.core.util import dimension_sanitizer
from holoviews.plotting.bokeh.element import ElementPlot, OverlayPlot as HvOverlayPlot

from ...element import is_geographic, _Element, Shape
from ..plot import ProjectionPlot


class GeoPlot(ProjectionPlot, ElementPlot):
    """
    Plotting baseclass for geographic plots with a cartopy projection.
    """

    default_tools = param.List(default=['save', 'pan',
                                        WheelZoomTool(zoom_on_axis=False),
                                        BoxZoomTool(match_aspect=True), 'reset'],
        doc="A list of plugin tools to use on the plot.")

    fixed_bounds = param.Boolean(default=False, doc="""
        Whether to prevent zooming beyond the projections defined bounds.""")

    global_extent = param.Boolean(default=False, doc="""
        Whether the plot should display the whole globe.""")

    infer_projection = param.Boolean(default=False, doc="""
        Whether the projection should be inferred from the element crs.""")

    show_grid = param.Boolean(default=False, doc="""
        Whether to show gridlines on the plot.""")

    show_bounds = param.Boolean(default=False, doc="""
        Whether to show gridlines on the plot.""")

    projection = param.Parameter(default=GOOGLE_MERCATOR, doc="""
        Allows supplying a custom projection to transform the axis
        coordinates during display. Defaults to GOOGLE_MERCATOR.""")

    # Project operation to apply to the element
    _project_operation = None

    _hover_code = """
        const projections = Bokeh.require("core/util/projections");
        const {snap_x, snap_y} = special_vars
        const coords = projections.wgs84_mercator.invert(snap_x, snap_y)
        return "" + (coords[%d]).toFixed(4)
    """

    def __init__(self, element, **params):
        super().__init__(element, **params)
        self.geographic = is_geographic(self.hmap.last)
        if self.geographic and not isinstance(self.projection, (PlateCarree, Mercator)):
            self.xaxis = None
            self.yaxis = None
            self.show_frame = False
            show_bounds = self._traverse_options(element, 'plot', ['show_bounds'],
                                                 defaults=False)
            self.show_bounds = not any(not sb for sb in show_bounds.get('show_bounds', []))
            if self.show_grid:
                param.main.warning(
                    f'Grid lines do not reflect {self.projection}; to do so '
                    'multiply the current element by gv.feature.grid() '
                    'and disable the show_grid option.'
                )

    def _axis_properties(self, axis, key, plot, dimension=None,
                         ax_mapping={'x': 0, 'y': 1}):
        axis_props = super()._axis_properties(axis, key, plot,
                                                           dimension, ax_mapping)
        proj = self.projection
        if self.geographic and proj is GOOGLE_MERCATOR:
            dimension = 'lon' if axis == 'x' else 'lat'
            axis_props['ticker'] = MercatorTicker(dimension=dimension)
            axis_props['formatter'] = MercatorTickFormatter(dimension=dimension)
        return axis_props

    def _update_ranges(self, element, ranges):
        super()._update_ranges(element, ranges)
        if not self.geographic:
            return
        if self.fixed_bounds:
            self.handles['x_range'].bounds = self.projection.x_limits
            self.handles['y_range'].bounds = self.projection.y_limits
        if self.projection is GOOGLE_MERCATOR:
            # Avoid zooming in beyond tile and axis resolution (causing JS errors)
            options = self._traverse_options(element, 'plot', ['default_span'], defaults=False)
            min_interval = options['default_span'][0] if options.get('default_span') else 5
            for r in ('x_range', 'y_range'):
                ax_range = self.handles[r]
                start, end = ax_range.start, ax_range.end
                if (end-start) < min_interval:
                    mid = (start+end)/2.
                    ax_range.start = mid - min_interval/2.
                    ax_range.start = mid + min_interval/2.
                ax_range.min_interval = min_interval

    def initialize_plot(self, ranges=None, plot=None, plots=None, source=None):
        opts = {} if isinstance(self, HvOverlayPlot) else {'source': source}
        fig = super().initialize_plot(ranges, plot, plots, **opts)
        if self.geographic and self.show_bounds and not self.overlaid:
            from . import GeoShapePlot
            shape = Shape(self.projection.boundary, crs=self.projection).options(fill_alpha=0)
            shapeplot = GeoShapePlot(shape, projection=self.projection,
                                     overlaid=True, renderer=self.renderer)
            shapeplot.geographic = False
            shapeplot.initialize_plot(plot=fig)
        return fig

    def _postprocess_hover(self, renderer, source):
        super()._postprocess_hover(renderer, source)
        hover = getattr(self.handles["plot"], "hover")
        hover = hover[0] if hover else None
        if (not self.geographic or hover is None or
            isinstance(hover.tooltips, str) or self.projection is not GOOGLE_MERCATOR
            or hover.tooltips is None or 'hv_created' not in hover.tags):
            return
        element = self.current_frame
        xdim, ydim = (dimension_sanitizer(kd.name) for kd in element.kdims)
        formatters, tooltips = dict(hover.formatters), []
        xhover = CustomJSHover(code=self._hover_code % 0)
        yhover = CustomJSHover(code=self._hover_code % 1)
        for name, formatter in hover.tooltips:
            customjs = None
            if formatter in ('@{%s}' % xdim, '$x'):
                dim = xdim
                formatter = '$x'
                customjs = xhover
            elif formatter in ('@{%s}' % ydim, '$y'):
                dim = ydim
                formatter = '$y'
                customjs = yhover
            if customjs:
                key = formatter if formatter in ('$x', '$y') else dim
                formatters[key] = customjs
                formatter += '{custom}'
            tooltips.append((name, formatter))
        hover.tooltips = tooltips
        hover.formatters = formatters

    def _update_hover(self, element):
        tooltips, hover_opts = self._hover_opts(element)
        hover = self.handles['hover']
        if 'hv_created' in hover.tags:
            tooltips = [(ttp.pprint_label, '@{%s}' % dimension_sanitizer(ttp.name))
                        if isinstance(ttp, Dimension) else ttp for ttp in tooltips]
            if self.geographic and tooltips[2:] == hover.tooltips[2:]:
                return
            tooltips = [(l, t+'{custom}' if t in hover.formatters else t) for l, t in tooltips]
            hover.tooltips = tooltips
        else:
            super()._update_hover(element)

    def get_data(self, element, ranges, style):
        if self._project_operation and self.geographic:
            element = self._project_operation(element, projection=self.projection)
        return super().get_data(element, ranges, style)


class GeoOverlayPlot(GeoPlot, HvOverlayPlot):
    """
    Subclasses the HoloViews OverlayPlot to add custom behavior
    for geographic plots.
    """

    global_extent = param.Boolean(default=False, doc="""
        Whether the plot should display the whole globe.""")

    _propagate_options = (HvOverlayPlot._propagate_options +
                          ['global_extent', 'show_bounds', 'infer_projection'])

    def __init__(self, element, **params):
        super().__init__(element, **params)
        self.geographic = any(element.traverse(is_geographic, [_Element]))
        if self.geographic:
            self.show_grid = False
