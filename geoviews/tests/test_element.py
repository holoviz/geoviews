"""
Unit tests of Path types.
"""
import numpy as np

from holoviews.element.comparison import ComparisonTestCase
from shapely.geometry import (
    GeometryCollection, Polygon, Point, LineString, LinearRing,
    MultiPolygon, MultiLineString, MultiPoint
)

from geoviews.element import Rectangles, Path, Polygons, Points, Segments



class TestRectangles(ComparisonTestCase):

    def test_empty_geom_conversion(self):
        rects = Rectangles([])
        self.assertEqual(rects.geom(), GeometryCollection())

    def test_single_geom_conversion(self):
        rects = Rectangles([(0, 0, 1, 1)])
        geom = rects.geom()
        self.assertIsInstance(geom, Polygon)
        self.assertEqual(
            np.array(geom.exterior.coords),
            np.array([
                [1., 0.],
                [1., 1.],
                [0., 1.],
                [0., 0.],
                [1., 0.]
            ])
        )

    def test_multi_geom_conversion(self):
        rects = Rectangles([(0, 0, 1, 1), (3, 2, 2.5, 1.5)])
        geom = rects.geom()
        self.assertIsInstance(geom, MultiPolygon)
        self.assertEqual(len(geom.geoms), 2)
        self.assertEqual(
            np.array(geom.geoms[0].exterior.coords),
            np.array([
                [1., 0.],
                [1., 1.],
                [0., 1.],
                [0., 0.],
                [1., 0.]
            ])
        )
        self.assertEqual(
            np.array(geom.geoms[1].exterior.coords),
            np.array([
                [2.5, 2],
                [2.5, 1.5],
                [3, 1.5],
                [3, 2],
                [2.5, 2]
            ])
        )

    def test_geom_union(self):
        rects = Rectangles([(0, 0, 1, 1), (1, 0, 2, 1)])
        geom = rects.geom(union=True)
        self.assertIsInstance(geom, Polygon)
        array = np.array(geom.exterior.coords)
        try:
            self.assertEqual(
                array,
                np.array([
                    [0, 0],
                    [0, 1],
                    [1, 1],
                    [2, 1],
                    [2, 0],
                    [1, 0],
                    [0, 0]
                ])
            )
        except Exception:
            self.assertEqual(
                array,
                np.array([
                    [1, 0],
                    [0, 0],
                    [0, 1],
                    [1, 1],
                    [2, 1],
                    [2, 0],
                    [1, 0]
                ])
            )

class TestPath(ComparisonTestCase):

    def test_empty_geom_conversion(self):
        path = Path([])
        self.assertEqual(path.geom(), GeometryCollection())

    def test_single_geom_conversion(self):
        path = Path([[(0, 0), (1, 1), (2, 0)]])
        geom = path.geom()
        self.assertIsInstance(geom, LineString)
        self.assertEqual(
            np.array(geom.coords),
            np.array([
                [0, 0],
                [1, 1],
                [2, 0]
            ])
        )

    def test_multi_geom_conversion(self):
        path = Path([[(0, 0), (1, 1), (2, 0)], [(3, 2), (2.5, 1.5)]])
        geom = path.geom()
        self.assertIsInstance(geom, MultiLineString)
        self.assertEqual(len(geom.geoms), 2)
        self.assertEqual(
            np.array(geom.geoms[0].coords),
            np.array([
                [0, 0],
                [1, 1],
                [2, 0]
            ])
        )
        self.assertEqual(
            np.array(geom.geoms[1].coords),
            np.array([
                [3, 2],
                [2.5, 1.5]
            ])
        )


class TestPolygons(ComparisonTestCase):

    def test_empty_geom_conversion(self):
        polys = Polygons([])
        self.assertEqual(polys.geom(), GeometryCollection())

    def test_single_geom_conversion(self):
        path = Polygons([[(0, 0), (1, 1), (2, 0)]])
        geom = path.geom()
        self.assertIsInstance(geom, Polygon)
        self.assertEqual(
            np.array(geom.exterior.coords),
            np.array([
                [0, 0],
                [1, 1],
                [2, 0],
                [0, 0]
            ])
        )

    def test_single_geom_with_hole_conversion(self):
        holes = [[((0.5, 0.2), (1, 0.8), (1.5, 0.2))]]
        path = Polygons([{'x': [0, 1, 2], 'y': [0, 1, 0], 'holes': holes}], ['x', 'y'])
        geom = path.geom()
        self.assertIsInstance(geom, Polygon)
        self.assertEqual(
            np.array(geom.exterior.coords),
            np.array([
                [0, 0],
                [1, 1],
                [2, 0],
                [0, 0]
            ])
        )
        self.assertEqual(len(geom.interiors), 1)
        self.assertIsInstance(geom.interiors[0], LinearRing)
        self.assertEqual(
            np.array(geom.interiors[0].coords),
            np.array([
                [0.5, 0.2],
                [1, 0.8],
                [1.5, 0.2],
                [0.5, 0.2]
            ])
        )

    def test_multi_geom_conversion(self):
        holes = [[((0.5, 0.2), (1, 0.8), (1.5, 0.2))]]
        path = Polygons([{'x': [0, 1, 2], 'y': [0, 1, 0], 'holes': holes},
                         {'x': [5, 6, 7], 'y': [2, 1, 2]}], ['x', 'y'])
        geom = path.geom()
        self.assertIsInstance(geom, MultiPolygon)
        self.assertEqual(len(geom.geoms), 2)
        self.assertEqual(
            np.array(geom.geoms[0].exterior.coords),
            np.array([
                [0, 0],
                [1, 1],
                [2, 0],
                [0, 0]
            ])
        )
        self.assertEqual(len(geom.geoms[0].interiors), 1)
        self.assertIsInstance(geom.geoms[0].interiors[0], LinearRing)
        self.assertEqual(
            np.array(geom.geoms[0].interiors[0].coords),
            np.array([
                [0.5, 0.2],
                [1, 0.8],
                [1.5, 0.2],
                [0.5, 0.2]
            ])
        )
        self.assertEqual(
            np.array(geom.geoms[1].exterior.coords),
            np.array([
                [5, 2],
                [6, 1],
                [7, 2],
                [5, 2]
            ])
        )
        self.assertEqual(len(geom.geoms[1].interiors), 0)



class TestPoints(ComparisonTestCase):

    def test_empty_geom_conversion(self):
        points = Points([])
        self.assertEqual(points.geom(), GeometryCollection())

    def test_single_geom_conversion(self):
        points = Points([(0, 0)])
        geom = points.geom()
        self.assertIsInstance(geom, Point)
        self.assertEqual(np.column_stack(geom.xy), np.array([[0, 0]]))

    def test_multi_geom_conversion(self):
        points = Points([(0, 0), (1, 2.5)])
        geom = points.geom()
        self.assertIsInstance(geom, MultiPoint)
        self.assertEqual(len(geom.geoms), 2)
        self.assertEqual(np.column_stack(geom.geoms[0].xy), np.array([[0, 0]]))
        self.assertEqual(np.column_stack(geom.geoms[1].xy), np.array([[1, 2.5]]))


class TestSegments(ComparisonTestCase):

    def test_empty_geom_conversion(self):
        segs = Segments([])
        self.assertEqual(segs.geom(), GeometryCollection())

    def test_single_geom_conversion(self):
        segs = Segments([(0, 0, 1, 1)])
        geom = segs.geom()
        self.assertIsInstance(geom, LineString)
        self.assertEqual(
            np.array(geom.coords),
            np.array([
                [0, 0],
                [1, 1]
            ])
        )

    def test_multi_geom_conversion(self):
        segs = Segments([(0, 0, 1, 1), (1.5, 2, 3, 1)])
        geom = segs.geom()
        self.assertIsInstance(geom, MultiLineString)
        self.assertEqual(len(geom.geoms), 2)
        self.assertEqual(
            np.array(geom.geoms[0].coords),
            np.array([
                [0, 0],
                [1, 1]
            ])
        )
        self.assertEqual(
            np.array(geom.geoms[1].coords),
            np.array([[
                1.5, 2],
                [3, 1]
            ])
        )
