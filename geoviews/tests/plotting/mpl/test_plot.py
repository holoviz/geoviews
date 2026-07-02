import cartopy.crs as ccrs
import cartopy.feature as cf
import matplotlib.pyplot as plt
import numpy as np
import pytest
import pyviz_comms as comms
from param import concrete_descendents
from shapely.geometry import LineString, MultiPolygon, Polygon

import geoviews as gv
from geoviews.plotting.mpl import ElementPlot

mpl_renderer = gv.Store.renderers["matplotlib"]


class TestMPLPlot:
    def setup_method(self):
        self.previous_backend = gv.Store.current_backend
        self.comm_manager = mpl_renderer.comm_manager
        mpl_renderer.comm_manager = comms.CommManager
        gv.Store.set_current_backend("matplotlib")
        self._padding = {}
        for plot in concrete_descendents(ElementPlot).values():
            self._padding[plot] = plot.padding
            plot.padding = 0

    def teardown_method(self):
        gv.Store.current_backend = self.previous_backend
        mpl_renderer.comm_manager = self.comm_manager
        plt.close(plt.gcf())
        for plot, padding in self._padding.items():
            plot.padding = padding

    def test_polygons_categorical_color_with_geopandas(self):
        # Test for https://github.com/holoviz/holoviews/pull/6762

        pytest.importorskip("holoviews", minversion="1.23.0a1")
        gpd = pytest.importorskip("geopandas")

        data = {
            "state": ["Texas", "Hawaii", "Michigan", "Florida"],
            "bea_region": ["Southwest", "Far West", "Great Lakes", "Southeast"],
            "geometry": [
                Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]),
                MultiPolygon(
                    [
                        Polygon([(3, 0), (3.5, 0), (3.5, 0.5), (3, 0.5)]),
                        Polygon([(4, 0), (4.5, 0), (4.5, 0.5), (4, 0.5)]),
                        Polygon([(5, 0), (5.5, 0), (5.5, 0.5), (5, 0.5)]),
                    ]
                ),
                MultiPolygon(
                    [
                        Polygon([(0, 3), (1.5, 3), (1.5, 4.5), (0, 4.5)]),
                        Polygon([(2, 3), (3, 3), (3, 4), (2, 4)]),
                    ]
                ),
                Polygon([(6, 0), (8, 0), (8, 2), (6, 2)]),
            ],
        }

        gdf = gpd.GeoDataFrame(data)

        # Verify test data is structured correctly
        expected_geom_types = {
            "Texas": "Polygon",
            "Hawaii": "MultiPolygon",
            "Michigan": "MultiPolygon",
            "Florida": "Polygon",
        }

        for state, expected_type in expected_geom_types.items():
            actual_type = gdf.loc[gdf["state"] == state, "geometry"].iloc[0].geom_type
            assert actual_type == expected_type

        polygons = gv.Polygons(gdf, vdims=["bea_region"]).opts(c="bea_region")

        plot = mpl_renderer.get_plot(polygons)
        array = plot.handles["artist"].get_array()

        assert array.dtype.kind == "i"
        assert len(np.unique(array)) == len(gdf["bea_region"].values)

        # CRITICAL TEST: Verify multi-polygon handling
        # Without the fix: len(array) = len(gdf) (4, one color value per state)
        # With the fix: len(array) = total_subpolygons (7, one color value per sub-polygon)
        total_subpolygons = sum(
            len(geom.geoms) if geom.geom_type == "MultiPolygon" else 1 for geom in gdf.geometry
        )

        assert len(array) == total_subpolygons


def test_feature_line_geometry_facecolor_default():
    # test for https://github.com/holoviz/geoviews/issues/845

    class _LineFeature(cf.Feature):
        def geometries(self):
            yield LineString([(0, 0), (1, 1)])

    feature = gv.Feature(_LineFeature(ccrs.PlateCarree())).opts(projection=ccrs.Orthographic())

    plot = mpl_renderer.get_plot(feature)
    artist = plot.handles["artist"]
    assert len(artist.get_facecolor()) == 0
