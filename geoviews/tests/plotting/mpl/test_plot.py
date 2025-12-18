import matplotlib.pyplot as plt
import pyviz_comms as comms
from param import concrete_descendents

from geoviews import Store
from geoviews.plotting.mpl import ElementPlot

mpl_renderer = Store.renderers['matplotlib']


class TestMPLPlot:

    def setup_method(self):
        self.previous_backend = Store.current_backend
        self.comm_manager = mpl_renderer.comm_manager
        mpl_renderer.comm_manager = comms.CommManager
        Store.set_current_backend('matplotlib')
        self._padding = {}
        for plot in concrete_descendents(ElementPlot).values():
            self._padding[plot] = plot.padding
            plot.padding = 0

    def teardown_method(self):
        Store.current_backend = self.previous_backend
        mpl_renderer.comm_manager = self.comm_manager
        plt.close(plt.gcf())
        for plot, padding in self._padding.items():
            plot.padding = padding

    # Regression test for https://github.com/holoviz/holoviews/pull/6762
    def test_polygons_categorical_color_with_geopandas(self):
        import numpy as np

        import geoviews as gv

        try:
            import hvsampledata as hvsd
        except ImportError:
            self.skipTest("hvsampledata not available")

        us_states = hvsd.us_states(engine="geopandas")
        polygons = gv.Polygons(us_states, vdims=["bea_region"]).opts(c="bea_region")

        plot = mpl_renderer.get_plot(polygons)
        artist = plot.handles["artist"]
        array = np.asarray(artist.get_array())

        unique_regions = [r for r in np.unique(us_states["bea_region"].values)]

        assert array.dtype.kind in "uif"
        assert len(np.unique(array)) == len(unique_regions)

        # CRITICAL TEST
        # This is the key regression - without the fix, multi-geometries only get
        # scalar color values instead of one color per sub-polygon
        # Before fix: len(array) = 49 (one value per state)
        # After fix:  len(array) = 66 (one value per sub-polygon)
        assert len(array) == 66
