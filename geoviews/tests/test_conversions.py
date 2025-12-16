import unittest

try:
    from iris.tests.stock import lat_lon_cube
except ImportError:
    raise unittest.SkipTest("iris not available") from None

from holoviews.core import HoloMap
from holoviews.element import Curve
from holoviews.testing import assert_element_equal

from geoviews.element import Dataset, Image, is_geographic


class TestConversions:

    def setup_method(self):
        self.cube = lat_lon_cube()

    def test_is_geographic_2d(self):
        assert is_geographic(Dataset(self.cube, kdims=['longitude', 'latitude']), ['longitude', 'latitude'])

    def test_geographic_conversion(self):
        assert_element_equal(Dataset(self.cube, kdims=['longitude', 'latitude']).to.image(), Image(self.cube, kdims=['longitude', 'latitude']))

    def test_nongeographic_conversion(self):
        converted = Dataset(self.cube, kdims=['longitude', 'latitude']).to.curve(['longitude'])
        assert isinstance(converted, HoloMap)
        assert converted.kdims == ['latitude']
        assert isinstance(converted.last, Curve)
