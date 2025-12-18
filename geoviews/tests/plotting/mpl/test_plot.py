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

        geometries = [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            Polygon([(2, 0), (3, 0), (3, 1), (2, 1)]),
            MultiPolygon([
                Polygon([(4, 0), (4.5, 0), (4.5, 0.5), (4, 0.5)]),
                Polygon([(5, 0), (5.5, 0), (5.5, 0.5), (5, 0.5)]),
                Polygon([(6, 0), (6.5, 0), (6.5, 0.5), (6, 0.5)]),
            ]),
            Polygon([(0, 2), (1, 2), (1, 3), (0, 3)]),
            MultiPolygon([
                Polygon([(2, 2), (2.5, 2), (2.5, 2.5), (2, 2.5)]),
                Polygon([(3, 2), (3.5, 2), (3.5, 2.5), (3, 2.5)]),
            ]),
        ]

        # Assign regions - states in same region should get same color
        regions = ['East', 'West', 'West', 'East', 'North']

        gdf = gpd.GeoDataFrame({'geometry': geometries, 'region': regions})
        polygons = Polygons(gdf, vdims=["region"]).opts(c="region")

        plot = mpl_renderer.get_plot(polygons)
        artist = plot.handles["artist"]
        array = np.asarray(artist.get_array())

        unique_regions = np.unique(gdf["region"].values)

        assert array.dtype.kind in "uif"
        assert len(np.unique(array)) == len(unique_regions)

        # CRITICAL TEST: Verify multi-polygon handling
        # Without the fix, multi-geometries only get scalar color values (one per state)
        # With the fix, each sub-polygon gets its own color value
        num_states = len(gdf)

        # The array should have MORE elements than states
        # Without fix: len(array) = num_states (5)
        # With fix: len(array) = 8 (one per sub-polygon)
        assert len(array) > num_states
