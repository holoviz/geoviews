import matplotlib.pyplot as plt
import numpy as np
import pytest
import pyviz_comms as comms
from param import concrete_descendents

from geoviews import Polygons, Store
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

    def test_polygons_categorical_color_with_geopandas(self):
        # Test for https://github.com/holoviz/holoviews/pull/6762

        gpd = pytest.importorskip("geopandas")
        from shapely.geometry import MultiPolygon, Polygon

        data = {
            'state': ['Texas', 'Hawaii', 'Michigan', 'Florida'],
            'bea_region': ['Southwest', 'Far West', 'Great Lakes', 'Southeast'],
            'geometry': [
                Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]),
                MultiPolygon([
                    Polygon([(3, 0), (3.5, 0), (3.5, 0.5), (3, 0.5)]),
                    Polygon([(4, 0), (4.5, 0), (4.5, 0.5), (4, 0.5)]),
                    Polygon([(5, 0), (5.5, 0), (5.5, 0.5), (5, 0.5)]),
                ]),
                MultiPolygon([
                    Polygon([(0, 3), (1.5, 3), (1.5, 4.5), (0, 4.5)]),
                    Polygon([(2, 3), (3, 3), (3, 4), (2, 4)]),
                ]),
                Polygon([(6, 0), (8, 0), (8, 2), (6, 2)]),
            ]
        }

        gdf = gpd.GeoDataFrame(data)
        polygons = Polygons(gdf, vdims=["bea_region"]).opts(c="bea_region")

        plot = mpl_renderer.get_plot(polygons)
        artist = plot.handles["artist"]
        array = np.asarray(artist.get_array())

        unique_regions = np.unique(gdf["bea_region"].values)

        assert array.dtype.kind in "uif"
        assert len(np.unique(array)) == len(unique_regions)

        # CRITICAL TEST: Verify multi-polygon handling
        # Without the fix: len(array) = 4 (one color value per state)
        # With the fix: len(array) = 7 (one color value per sub-polygon)
        assert len(array) == 7
