import warnings

import pytest
from holoviews.core import HoloMap
from holoviews.element import Curve
from holoviews.testing import assert_element_equal

import geoviews as gv
from geoviews.element import is_geographic


class TestConversions:
    def setup_method(self):
        try:
            import iris  # noqa: F401
        except ModuleNotFoundError:
            pytest.skip("iris is not installed")

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            from iris.tests.stock import lat_lon_cube

        self.cube = lat_lon_cube()

    def test_is_geographic_2d(self):
        assert is_geographic(
            gv.Dataset(self.cube, kdims=["longitude", "latitude"]), ["longitude", "latitude"]
        )

    def test_geographic_conversion(self):
        assert_element_equal(
            gv.Dataset(self.cube, kdims=["longitude", "latitude"]).to.image(),
            gv.Image(self.cube, kdims=["longitude", "latitude"]),
        )

    def test_nongeographic_conversion(self):
        converted = gv.Dataset(self.cube, kdims=["longitude", "latitude"]).to.curve(["longitude"])
        assert isinstance(converted, HoloMap)
        assert converted.kdims == ["latitude"]
        assert isinstance(converted.last, Curve)
