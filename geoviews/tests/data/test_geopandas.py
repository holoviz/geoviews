"""
Test for the GeoPandasInterface
"""
from unittest import SkipTest

import numpy as np
import pandas as pd

from shapely import geometry as sgeom

try:
    import geopandas
    from geopandas.array import GeometryDtype
except ImportError:
    geopandas = None

from holoviews.core.data import Dataset
from holoviews.core.data.interface import DataError
from holoviews.element import Polygons, Path, Points
from holoviews.element.comparison import ComparisonTestCase
from holoviews.tests.core.data.test_multiinterface import GeomTests

from geoviews.data import GeoPandasInterface

from .test_multigeometry import GeomInterfaceTest


class RoundTripTests(ComparisonTestCase):

    datatype = None

    interface = None

    __test__ = False

    def test_point_roundtrip(self):
        points = Points([{'x': 0, 'y': 1, 'z': 0},
                         {'x': 1, 'y': 0, 'z': 1}], ['x', 'y'],
                        'z', datatype=[self.datatype])
        self.assertIsInstance(points.data.geometry.dtype, GeometryDtype)
        roundtrip = points.clone(datatype=['multitabular'])
        self.assertEqual(roundtrip.interface.datatype, 'multitabular')
        expected = Points([{'x': 0, 'y': 1, 'z': 0},
                           {'x': 1, 'y': 0, 'z': 1}], ['x', 'y'],
                          'z', datatype=['multitabular'])
        self.assertEqual(roundtrip, expected)

    def test_multi_point_roundtrip(self):
        xs = [1, 2, 3, 2]
        ys = [2, 0, 7, 4]
        points = Points([{'x': xs, 'y': ys, 'z': 0},
                         {'x': xs[::-1], 'y': ys[::-1], 'z': 1}],
                        ['x', 'y'], 'z', datatype=[self.datatype])
        self.assertIsInstance(points.data.geometry.dtype, GeometryDtype)
        roundtrip = points.clone(datatype=['multitabular'])
        self.assertEqual(roundtrip.interface.datatype, 'multitabular')
        expected = Points([{'x': xs, 'y': ys, 'z': 0},
                           {'x': xs[::-1], 'y': ys[::-1], 'z': 1}],
                          ['x', 'y'], 'z', datatype=['multitabular'])
        self.assertEqual(roundtrip, expected)

    def test_line_roundtrip(self):
        xs = [1, 2, 3]
        ys = [2, 0, 7]
        path = Path([{'x': xs, 'y': ys, 'z': 1},
                     {'x': xs[::-1], 'y': ys[::-1], 'z': 2}],
                    ['x', 'y'], 'z', datatype=[self.datatype])
        self.assertIsInstance(path.data.geometry.dtype, GeometryDtype)
        roundtrip = path.clone(datatype=['multitabular'])
        self.assertEqual(roundtrip.interface.datatype, 'multitabular')
        expected = Path([{'x': xs, 'y': ys, 'z': 1},
                         {'x': xs[::-1], 'y': ys[::-1], 'z': 2}],
                        ['x', 'y'], 'z', datatype=['multitabular'])
        self.assertEqual(roundtrip, expected)

    def test_multi_line_roundtrip(self):
        xs = [1, 2, 3, np.nan, 6, 7, 3]
        ys = [2, 0, 7, np.nan, 7, 5, 2]
        path = Path([{'x': xs, 'y': ys, 'z': 0},
                     {'x': xs[::-1], 'y': ys[::-1], 'z': 1}],
                    ['x', 'y'], 'z', datatype=[self.datatype])
        self.assertIsInstance(path.data.geometry.dtype, GeometryDtype)
        roundtrip = path.clone(datatype=['multitabular'])
        self.assertEqual(roundtrip.interface.datatype, 'multitabular')
        expected = Path([{'x': xs, 'y': ys, 'z': 0},
                         {'x': xs[::-1], 'y': ys[::-1], 'z': 1}],
                        ['x', 'y'], 'z', datatype=['multitabular'])
        self.assertEqual(roundtrip, expected)

    def test_polygon_roundtrip(self):
        xs = [1, 2, 3]
        ys = [2, 0, 7]
        poly = Polygons([{'x': xs, 'y': ys, 'z': 0},
                         {'x': xs[::-1], 'y': ys[::-1], 'z': 1}],
                        ['x', 'y'], 'z', datatype=[self.datatype])
        self.assertIsInstance(poly.data.geometry.dtype, GeometryDtype)
        roundtrip = poly.clone(datatype=['multitabular'])
        self.assertEqual(roundtrip.interface.datatype, 'multitabular')
        expected = Polygons([{'x': xs+[1], 'y': ys+[2], 'z': 0},
                             {'x': xs[::-1]+[3], 'y': ys[::-1]+[7], 'z': 1}],
                            ['x', 'y'], 'z', datatype=['multitabular'])
        self.assertEqual(roundtrip, expected)

    def test_multi_polygon_roundtrip(self):
        xs = [1, 2, 3, np.nan, 6, 7, 3]
        ys = [2, 0, 7, np.nan, 7, 5, 2]
        holes = [
            [[(1.5, 2), (2, 3), (1.6, 1.6)], [(2.1, 4.5), (2.5, 5), (2.3, 3.5)]],
            []
        ]
        poly = Polygons([{'x': xs, 'y': ys, 'holes': holes, 'z': 1},
                         {'x': xs[::-1], 'y': ys[::-1], 'z': 2}],
                        ['x', 'y'], 'z', datatype=[self.datatype])
        self.assertIsInstance(poly.data.geometry.dtype, GeometryDtype)
        roundtrip = poly.clone(datatype=['multitabular'])
        self.assertEqual(roundtrip.interface.datatype, 'multitabular')
        expected = Polygons([{'x': [1, 2, 3, 1, np.nan, 6, 7, 3, 6],
                              'y': [2, 0, 7, 2, np.nan, 7, 5, 2, 7], 'holes': holes, 'z': 1},
                             {'x': [3, 7, 6, 3, np.nan, 3, 2, 1, 3],
                              'y': [2, 5, 7, 2, np.nan, 7, 0, 2, 7], 'z': 2}],
                            ['x', 'y'], 'z', datatype=['multitabular'])
        self.assertEqual(roundtrip, expected)



class GeoPandasInterfaceTest(GeomInterfaceTest, GeomTests, RoundTripTests):
    """
    Test of the GeoPandasInterface.
    """

    datatype = 'geodataframe'
    interface = GeoPandasInterface

    __test__ = True

    def setUp(self):
        if geopandas is None:
            raise SkipTest('GeoPandasInterface requires geopandas, skipping tests')
        super().setUp()

    def test_df_dataset(self):
        if not pd:
            raise SkipTest('Pandas not available')
        dfs = [pd.DataFrame(np.column_stack([np.arange(i, i+2), np.arange(i, i+2)]), columns=['x', 'y'])
                  for i in range(2)]
        mds = Path(dfs, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertIs(mds.interface, self.interface)
        for i, ds in enumerate(mds.split(datatype='dataframe')):
            ds['x'] = ds.x.astype(int)
            ds['y'] = ds.y.astype(int)
            self.assertEqual(ds, dfs[i])

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

    def test_array_points_iloc_index_rows_index_cols(self):
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

    def test_geometry_column_not_named_geometry(self):
        # The geodataframe has its geometry column not named 'geometry'
        gdf = geopandas.GeoDataFrame(
            {
                'v': [1, 2],
                'not geometry': [sgeom.Point(0, 1), sgeom.Point(1, 2)],
            },
            geometry='not geometry',
        )
        ds = Dataset(gdf, kdims=['Longitude', 'Latitude'], datatype=[self.datatype])
        self.assertEqual(ds.dimension_values('Longitude'), np.array([0, 1]))
        self.assertEqual(ds.dimension_values('Latitude'), np.array([1, 2]))

    def test_geometry_column_not_named_geometry_and_additional_geometry_column(self):
        gdf = geopandas.GeoDataFrame(
            {
                'v': [1, 2],
                'not geometry': [sgeom.Point(0, 1), sgeom.Point(1, 2)],
            },
            geometry='not geometry',
        )
        # The geodataframe contains a column called 'geometry' that doesn't contain geometry data.
        gdf = gdf.rename(columns={'v': 'geometry'})
        ds = Dataset(gdf, kdims=['Longitude', 'Latitude'], datatype=[self.datatype])
        self.assertEqual(ds.dimension_values('Longitude'), np.array([0, 1]))
        self.assertEqual(ds.dimension_values('Latitude'), np.array([1, 2]))
