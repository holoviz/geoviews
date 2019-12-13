"""
Test for the GeoPandasInterface
"""

import numpy as np
from shapely import geometry as sgeom

try:
    import geopandas
except:
    geopandas = None

from geoviews.data import GeoPandasInterface

from holoviews.core.data import Dataset
from holoviews.core.data.interface import DataError
from holoviews.element import Polygons
from holoviews.tests.core.data.testmultiinterface import GeomTests

from .testmultigeominterface import GeomInterfaceTest


class GeoPandasInterfaceTest(GeomInterfaceTest, GeomTests):
    """
    Test of the MultiInterface and GeomDictInterface.
    """

    datatype = 'geodataframe'
    interface = GeoPandasInterface

    __test__ = True

    def test_multi_geom_point_coord_values(self):
        geoms = [{'geometry': sgeom.Point([(0, 1)])},
                 {'geometry': sgeom.Point([(3, 5)])}]
        mds = Dataset(geoms, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertEqual(mds.dimension_values('x'), np.array([0, 3]))
        self.assertEqual(mds.dimension_values('y'), np.array([1, 5]))

    def test_multi_geom_point_length(self):
        geoms = [{'geometry': sgeom.Point([(0, 0)])},
                 {'geometry': sgeom.Point([(3, 3)])}]
        mds = Dataset(geoms, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertEqual(len(mds), 2)

    def test_multi_dict_groupby(self):
        arrays = [{'x': np.arange(i, i+2), 'y': i} for i in range(2)]
        mds = Dataset(arrays, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertIs(mds.interface, self.interface)
        with self.assertRaises(DataError):
            mds.groupby('y')

    def test_multi_array_groupby(self):
        arrays = [np.array([(1+i, i), (2+i, i), (3+i, i)]) for i in range(2)]
        mds = Dataset(arrays, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertIs(mds.interface, self.interface)
        with self.assertRaises(DataError):
            mds.groupby('y')

    def test_multi_array_points_iloc_index_rows_index_cols(self):
        arrays = [np.array([(1+i, i), (2+i, i), (3+i, i)]) for i in range(2)]
        mds = Dataset(arrays, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertIs(mds.interface, self.interface)
        with self.assertRaises(DataError):
            mds.iloc[3, 0]

    def test_polygon_dtype(self):
        poly = Polygons([{'x': [1, 2, 3], 'y': [2, 0, 7]}], datatype=[self.datatype])
        self.assertIs(poly.interface, self.interface)
        self.assertEqual(poly.interface.dtype(poly, 'x'),
                         'float64')
