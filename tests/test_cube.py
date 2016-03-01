import unittest

import numpy as np
from holocube.element.cube import Cube, coord_to_dimension
from iris.tests.stock import lat_lon_cube
from holoviews.element.comparison import ComparisonTestCase


class TestCube(ComparisonTestCase):

    def setUp(self):
        self.cube = lat_lon_cube()

    def test_dim_to_coord(self):
        dim = coord_to_dimension(self.cube.coords()[0])
        self.assertEqual(dim.name, 'latitude')
        self.assertEqual(dim.unit, 'degrees')

    def test_initialize_cube(self):
        cube = Cube(self.cube)
        self.assertEqual(cube.dimensions(label=True),
                         ['latitude', 'longitude', 'unknown'])

    def test_initialize_cube_with_kdims(self):
        cube = Cube(self.cube, kdims=['longitude', 'latitude'])
        self.assertEqual(cube.dimensions('key', True),
                         ['longitude', 'latitude'])

    def test_initialize_cube_with_vdims(self):
        cube = Cube(self.cube, vdims=['Quantity'])
        self.assertEqual(cube.dimensions('value', True),
                         ['Quantity'])

    def test_dimension_values_kdim(self):
        cube = Cube(self.cube, kdims=['longitude', 'latitude'])
        self.assertEqual(cube.dimension_values('longitude'),
                         np.array([-1,  0,  1, 2], dtype=np.int32))

    def test_dimension_values_vdim(self):
        cube = Cube(self.cube, kdims=['longitude', 'latitude'])
        self.assertEqual(cube.dimension_values('unknown'),
                         np.array([[ 0,  1,  2,  3],
                                   [ 4,  5,  6,  7],
                                   [ 8,  9, 10, 11]], dtype=np.int32))

    def test_range_kdim(self):
        cube = Cube(self.cube, kdims=['longitude', 'latitude'])
        self.assertEqual(cube.range('longitude'), (-1, 2))

    def test_range_vdim(self):
        cube = Cube(self.cube, kdims=['longitude', 'latitude'])
        self.assertEqual(cube.range('unknown'), (0, 11))
