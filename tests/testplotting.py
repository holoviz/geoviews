from iris.tests.stock import lat_lon_cube

from geoviews.element import Image
from geoviews.element.comparison import ComparisonTestCase
from geoviews.plotting.mpl import GeoImagePlot


class TestGeoImagePlot(ComparisonTestCase):
    def test_auto_guess_bounds(self):
        # Check that the `get_data()` method automatically adds bounds
        # when they're missing.
        cube = lat_lon_cube()
        element = Image(cube.copy())
        plot = GeoImagePlot(element)
        ranges = {}
        style = {'interpolation': None}
        plot_args, style, axis_kwargs = plot.get_data(element, ranges, style)
        for name in ('latitude', 'longitude'):
            cube.coord(name).guess_bounds()
        self.assertEqual(plot_args, (cube,))
        self.assertEqual(style, {'vmax': 11, 'vmin': 0})
        self.assertEqual(axis_kwargs, {})

    def test_auto_guess_bounds_not_needed(self):
        # Check that the `get_data()` method *doesn't* try to add or
        # modify the bounds when they're already present.
        cube = lat_lon_cube()
        for name in ('latitude', 'longitude'):
            coord = cube.coord(name)
            coord.guess_bounds()
            coord.bounds = coord.bounds + 0.1
        element = Image(cube.copy())
        plot = GeoImagePlot(element)
        ranges = {}
        style = {'interpolation': None}
        plot_args, style, axis_kwargs = plot.get_data(element, ranges, style)
        self.assertEqual(plot_args, (cube,))
        self.assertEqual(style, {'vmax': 11, 'vmin': 0})
        self.assertEqual(axis_kwargs, {})


if __name__ == '__main__':
    import unittest
    unittest.main()
