import pyviz_comms as comms
from holoviews.plotting.bokeh.element import ElementPlot
from param import concrete_descendents

from geoviews import Store

bokeh_renderer = Store.renderers['bokeh']


class TestBokehPlot:

    def setup_method(self):
        self.previous_backend = Store.current_backend
        self.comm_manager = bokeh_renderer.comm_manager
        bokeh_renderer.comm_manager = comms.CommManager
        Store.set_current_backend('bokeh')
        self._padding = {}
        for plot in concrete_descendents(ElementPlot).values():
            self._padding[plot] = plot.padding
            plot.padding = 0

    def teardown_method(self):
        Store.current_backend = self.previous_backend
        bokeh_renderer.comm_manager = self.comm_manager
        for plot, padding in self._padding.items():
            plot.padding = padding
