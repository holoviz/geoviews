from iris.tests.stock import lat_lon_cube
from holoviews.core import HoloMap
from holoviews.element import Curve

from geoviews.element import is_geographic, Image, Dataset
from geoviews.element.comparison import ComparisonTestCase

class TestConversions(ComparisonTestCase):

    def setUp(self):
        self.cube = lat_lon_cube()

    def test_is_geographic_1d(self):
        self.assertFalse(is_geographic(Dataset(self.cube), ['longitude']))
        
    def test_is_geographic_2d(self):
        self.assertTrue(is_geographic(Dataset(self.cube), ['longitude', 'latitude']))

    def test_geographic_conversion(self):
        self.assertEqual(Dataset(self.cube).to.image(), Image(self.cube))
        
    def test_nongeographic_conversion(self):
        converted = Dataset(self.cube).to.curve(['longitude'])
        self.assertTrue(isinstance(converted, HoloMap))
        self.assertEqual(converted.kdims, ['latitude'])
        self.assertTrue(isinstance(converted.last, Curve))
