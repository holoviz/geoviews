"""
Unit tests of Path types.
"""
import numpy as np
from holoviews.element.comparison import ComparisonTestCase
from shapely.geometry import (
    GeometryCollection,
    LinearRing,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)

from geoviews.element import Path, Points, Polygons, Rectangles, Segments, VectorField


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


class TestVectorField(ComparisonTestCase):

    def test_vectorfield_from_uv(self):
        """Test VectorField.from_uv uses mathematical convention."""
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 2 * Y

        # Mathematical convention: angle = arctan2(v, u)
        angle = np.arctan2(V, U)
        mag = np.hypot(U, V)

        gv_field = VectorField((X, Y, angle, mag))
        gv_field_uv = VectorField.from_uv((X, Y, U, V))

        np.testing.assert_almost_equal(
            gv_field.data["Angle"].T.flatten(),
            gv_field_uv.data["Angle"]
        )
        np.testing.assert_almost_equal(
            gv_field.data["Magnitude"].T.flatten(),
            gv_field_uv.data["Magnitude"]
        )

    def test_vectorfield_from_uv_horizontal(self):
        """Test VectorField.from_uv with horizontal vectors (u=10, v=0)."""
        x = np.linspace(-180, 180, 4)
        y = np.linspace(-90, 90, 4)
        X, Y = np.meshgrid(x, y)
        
        # Horizontal vectors pointing right (East)
        U = 10 * np.ones_like(X)
        V = np.zeros_like(Y)
        
        gv_field_uv = VectorField.from_uv((X, Y, U, V))
        
        # Mathematical convention: angle = arctan2(0, 10) = 0 (pointing East/Right)
        expected_angle = np.arctan2(V, U)
        expected_mag = np.hypot(U, V)
        
        np.testing.assert_almost_equal(
            gv_field_uv.data["Angle"],
            expected_angle.flatten()
        )
        np.testing.assert_almost_equal(
            gv_field_uv.data["Magnitude"],
            expected_mag.flatten()
        )

    def test_vectorfield_from_uv_vertical(self):
        """Test VectorField.from_uv with vertical vectors (u=0, v=10)."""
        x = np.linspace(-180, 180, 4)
        y = np.linspace(-90, 90, 4)
        X, Y = np.meshgrid(x, y)
        
        # Vertical vectors pointing up (North)
        U = np.zeros_like(X)
        V = 10 * np.ones_like(Y)
        
        gv_field_uv = VectorField.from_uv((X, Y, U, V))
        
        # Mathematical convention: angle = arctan2(10, 0) = π/2 (pointing North/Up)
        expected_angle = np.arctan2(V, U)
        expected_mag = np.hypot(U, V)
        
        np.testing.assert_almost_equal(
            gv_field_uv.data["Angle"],
            expected_angle.flatten()
        )
        np.testing.assert_almost_equal(
            gv_field_uv.data["Magnitude"],
            expected_mag.flatten()
        )

    def test_vectorfield_from_uv_issue_reproduction(self):
        """
        Test that reproduces the exact scenario from GitHub issue.
        
        Issue: User had u=10, v=0 and was using meteorological convention
        which gave wrong results. This test verifies the fix.
        """
        x = np.linspace(-180, 180, 20)
        y = np.linspace(-90, 90, 20)
        X, Y = np.meshgrid(x, y)
        
        # The exact scenario from the issue
        u = 10 * np.ones_like(X)
        v = np.zeros_like(Y)
        
        # Create VectorField using from_uv
        gv_field = VectorField.from_uv((X, Y, u, v))
        
        # Verify angles are correct (should be 0 for horizontal vectors pointing East)
        # Mathematical convention: angle = arctan2(0, 10) = 0
        expected_angles = np.zeros_like(u.flatten())
        np.testing.assert_almost_equal(
            gv_field.data["Angle"],
            expected_angles
        )
        
        # Verify magnitudes are correct
        expected_magnitudes = 10 * np.ones_like(u.flatten())
        np.testing.assert_almost_equal(
            gv_field.data["Magnitude"],
            expected_magnitudes
        )
