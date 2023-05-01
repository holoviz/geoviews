"""
Test for the MultiInterface and GeomDictInterface
"""
from unittest import SkipTest

import numpy as np
import pandas as pd

from holoviews.core.data import Dataset, MultiInterface
from holoviews.core.data.interface import DataError
from holoviews.element import Polygons, Path
from holoviews.element.comparison import ComparisonTestCase
from holoviews.tests.core.data.test_multiinterface import MultiBaseInterfaceTest

try:
    from shapely import geometry as sgeom
except ImportError:
    sgeom = None

try:
    import spatialpandas
except ImportError:
    spatialpandas = None

from geoviews.data.geom_dict import GeomDictInterface


class GeomInterfaceTest(ComparisonTestCase):
    """
    Test for the MultiInterface and GeomDictInterface.
    """

    __test__ = False

    def setUp(self):
        if sgeom is None:
            raise SkipTest('GeomInterfaceTest requires shapely, skipping tests')
        super().setUp()

    def test_multi_geom_dataset_geom_list_constructor(self):
        geoms = [sgeom.Polygon([(0, 0), (3, 3), (6, 0)])]
        Dataset(geoms, kdims=['x', 'y'], datatype=[self.datatype])

    def test_multi_geom_dataset_geom_dict_constructor(self):
        geoms = [{'geometry': sgeom.Polygon([(0, 0), (3, 3), (6, 0)])}]
        Dataset(geoms, kdims=['x', 'y'], datatype=[self.datatype])

    def test_multi_geom_dataset_geom_dict_constructor_extra_kdim(self):
        geoms = [{'geometry': sgeom.Polygon([(0, 0), (3, 3), (6, 0)]), 'z': 1}]
        Dataset(geoms, kdims=['x', 'y', 'z'], datatype=[self.datatype])

    def test_multi_geom_dataset_poly_coord_values(self):
        geoms = [sgeom.Polygon([(0, 0), (6, 6), (3, 3)])]
        mds = Dataset(geoms, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertEqual(mds.dimension_values('x'), np.array([0, 6, 3, 0]))
        self.assertEqual(mds.dimension_values('y'), np.array([0, 6, 3, 0]))

    def test_multi_geom_dataset_poly_scalar_values(self):
        geoms = [{'geometry': sgeom.Polygon([(0, 0), (3, 3), (6, 0)]), 'z': 1}]
        mds = Dataset(geoms, kdims=['x', 'y', 'z'], datatype=[self.datatype])
        self.assertEqual(mds.dimension_values('z'), np.array([1, 1, 1, 1]))
        self.assertEqual(mds.dimension_values('z', expanded=False), np.array([1]))

    def test_multi_geom_poly_length(self):
        geoms = [{'geometry': sgeom.Polygon([(0, 0), (3, 3), (6, 0)])},
                 {'geometry': sgeom.Polygon([(3, 3), (9, 3), (6, 0)])}]
        mds = Dataset(geoms, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertEqual(len(mds), 2)

    def test_multi_geom_poly_range(self):
        geoms = [{'geometry': sgeom.Polygon([(0, 0), (3, 3), (6, 0)])},
                 {'geometry': sgeom.Polygon([(3, 3), (9, 3), (6, 0)])}]
        mds = Dataset(geoms, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertEqual(mds.range('x'), (0, 9))
        self.assertEqual(mds.range('y'), (0, 3))

    def test_multi_geom_dataset_line_string_coord_values(self):
        geoms = [sgeom.LineString([(0, 0), (3, 3), (6, 0)])]
        mds = Dataset(geoms, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertEqual(mds.dimension_values('x'), np.array([0, 3, 6]))
        self.assertEqual(mds.dimension_values('y'), np.array([0, 3, 0]))

    def test_multi_geom_dataset_line_string_scalar_values(self):
        geoms = [{'geometry': sgeom.LineString([(0, 0), (3, 3), (6, 0)]), 'z': 1}]
        mds = Dataset(geoms, kdims=['x', 'y', 'z'], datatype=[self.datatype])
        self.assertEqual(mds.dimension_values('z'), np.array([1, 1, 1]))
        self.assertEqual(mds.dimension_values('z', expanded=False), np.array([1]))

    def test_multi_geom_line_string_length(self):
        geoms = [{'geometry': sgeom.LineString([(0, 0), (3, 3), (6, 0)])},
                 {'geometry': sgeom.LineString([(3, 3), (9, 3), (6, 0)])}]
        mds = Dataset(geoms, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertEqual(len(mds), 2)

    def test_multi_geom_point_length(self):
        geoms = [{'geometry': sgeom.Point([(0, 0)])},
                 {'geometry': sgeom.Point([(3, 3)])}]
        mds = Dataset(geoms, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertEqual(len(mds), 2)

    def test_multi_geom_point_coord_values(self):
        geoms = [{'geometry': sgeom.Point([(0, 1)])},
                 {'geometry': sgeom.Point([(3, 5)])}]
        mds = Dataset(geoms, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertEqual(mds.dimension_values('x'), np.array([0, 3]))
        self.assertEqual(mds.dimension_values('y'), np.array([1, 5]))

    def test_multi_geom_point_coord_range(self):
        geoms = [{'geometry': sgeom.Point([(0, 1)])},
                 {'geometry': sgeom.Point([(3, 5)])}]
        mds = Dataset(geoms, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertEqual(mds.range('x'), (0, 3))
        self.assertEqual(mds.range('y'), (1, 5))

    def test_multi_dict_groupby(self):
        geoms = [{'geometry': sgeom.Polygon([(2, 0), (1, 2), (0, 0)]), 'z': 1},
                 {'geometry': sgeom.Polygon([(3, 3), (3, 3), (6, 0)]), 'z': 2}]
        mds = Dataset(geoms, kdims=['x', 'y', 'z'], datatype=[self.datatype])
        for i, (k, ds) in enumerate(mds.groupby('z').items()):
            self.assertEqual(k, geoms[i]['z'])
            self.assertEqual(ds.clone(vdims=[]), Dataset([geoms[i]], kdims=['x', 'y']))


class MultiGeomInterfaceTest(GeomInterfaceTest):

    datatype = 'multitabular'
    interface = GeomDictInterface

    __test__ = True


class SpatialPandasGeomInterfaceTest(GeomInterfaceTest):

    datatype = 'spatialpandas'

    __test__ = True

    def setUp(self):
        if spatialpandas is None:
            raise SkipTest('SpatialPandasInterface requires spatialpandas, skipping tests')
        super().setUp()


class MultiGeomDictInterfaceTest(MultiBaseInterfaceTest):

    datatype = 'multitabular'
    interface = MultiInterface
    subtype = 'geom_dictionary'

    __test__ = True

    def test_dict_dataset(self):
        dicts = [{'x': np.arange(i, i+2), 'y': np.arange(i, i+2)} for i in range(2)]
        mds = Path(dicts, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertIs(mds.interface, self.interface)
        for i, cols in enumerate(mds.split(datatype='columns')):
            self.assertEqual(dict(cols), dict(dicts[i], geom_type='Line',
                                              geometry=mds.data[i]['geometry']))

    def test_polygon_dtype(self):
        poly = Polygons([{'x': [1, 2, 3], 'y': [2, 0, 7]}], datatype=[self.datatype])
        self.assertIs(poly.interface, self.interface)
        self.assertEqual(poly.interface.dtype(poly, 'x'),
                         'float64')

    def test_array_points_iloc_index_rows_index_cols(self):
        arrays = [np.array([(1+i, i), (2+i, i), (3+i, i)]) for i in range(2)]
        mds = Dataset(arrays, kdims=['x', 'y'], datatype=[self.datatype])
        self.assertIs(mds.interface, self.interface)
        with self.assertRaises(DataError):
            mds.iloc[3, 0]

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
