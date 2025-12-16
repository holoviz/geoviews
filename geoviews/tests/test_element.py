"""
Unit tests of Path types.
"""
import numpy as np
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

from geoviews.element import Path, Points, Polygons, Rectangles, Segments


class TestRectangles:

    def test_empty_geom_conversion(self):
        rects = Rectangles([])
        assert rects.geom() == GeometryCollection()

    def test_single_geom_conversion(self):
        rects = Rectangles([(0, 0, 1, 1)])
        geom = rects.geom()
        assert isinstance(geom, Polygon)
        np.testing.assert_array_equal(
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
        assert isinstance(geom, MultiPolygon)
        assert len(geom.geoms) == 2
        np.testing.assert_array_equal(
            np.array(geom.geoms[0].exterior.coords),
            np.array([
                [1., 0.],
                [1., 1.],
                [0., 1.],
                [0., 0.],
                [1., 0.]
            ])
        )
        np.testing.assert_array_equal(
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
        assert isinstance(geom, Polygon)
        array = np.array(geom.exterior.coords)
        try:
            np.testing.assert_array_equal(
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
            np.testing.assert_array_equal(
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

class TestPath:

    def test_empty_geom_conversion(self):
        path = Path([])
        assert path.geom() == GeometryCollection()

    def test_single_geom_conversion(self):
        path = Path([[(0, 0), (1, 1), (2, 0)]])
        geom = path.geom()
        assert isinstance(geom, LineString)
        np.testing.assert_array_equal(
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
        assert isinstance(geom, MultiLineString)
        assert len(geom.geoms) == 2
        np.testing.assert_array_equal(
            np.array(geom.geoms[0].coords),
            np.array([
                [0, 0],
                [1, 1],
                [2, 0]
            ])
        )
        np.testing.assert_array_equal(
            np.array(geom.geoms[1].coords),
            np.array([
                [3, 2],
                [2.5, 1.5]
            ])
        )


class TestPolygons:

    def test_empty_geom_conversion(self):
        polys = Polygons([])
        assert polys.geom() == GeometryCollection()

    def test_single_geom_conversion(self):
        path = Polygons([[(0, 0), (1, 1), (2, 0)]])
        geom = path.geom()
        assert isinstance(geom, Polygon)
        np.testing.assert_array_equal(
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
        assert isinstance(geom, Polygon)
        np.testing.assert_array_equal(
            np.array(geom.exterior.coords),
            np.array([
                [0, 0],
                [1, 1],
                [2, 0],
                [0, 0]
            ])
        )
        assert len(geom.interiors) == 1
        assert isinstance(geom.interiors[0], LinearRing)
        np.testing.assert_array_equal(
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
        assert isinstance(geom, MultiPolygon)
        assert len(geom.geoms) == 2
        np.testing.assert_array_equal(
            np.array(geom.geoms[0].exterior.coords),
            np.array([
                [0, 0],
                [1, 1],
                [2, 0],
                [0, 0]
            ])
        )
        assert len(geom.geoms[0].interiors) == 1
        assert isinstance(geom.geoms[0].interiors[0], LinearRing)
        np.testing.assert_array_equal(
            np.array(geom.geoms[0].interiors[0].coords),
            np.array([
                [0.5, 0.2],
                [1, 0.8],
                [1.5, 0.2],
                [0.5, 0.2]
            ])
        )
        np.testing.assert_array_equal(
            np.array(geom.geoms[1].exterior.coords),
            np.array([
                [5, 2],
                [6, 1],
                [7, 2],
                [5, 2]
            ])
        )
        assert len(geom.geoms[1].interiors) == 0



class TestPoints:

    def test_empty_geom_conversion(self):
        points = Points([])
        assert points.geom() == GeometryCollection()

    def test_single_geom_conversion(self):
        points = Points([(0, 0)])
        geom = points.geom()
        assert isinstance(geom, Point)
        np.testing.assert_array_equal(np.column_stack(geom.xy), np.array([[0, 0]]))

    def test_multi_geom_conversion(self):
        points = Points([(0, 0), (1, 2.5)])
        geom = points.geom()
        assert isinstance(geom, MultiPoint)
        assert len(geom.geoms) == 2
        np.testing.assert_array_equal(np.column_stack(geom.geoms[0].xy), np.array([[0, 0]]))
        np.testing.assert_array_equal(np.column_stack(geom.geoms[1].xy), np.array([[1, 2.5]]))


class TestSegments:

    def test_empty_geom_conversion(self):
        segs = Segments([])
        assert segs.geom() == GeometryCollection()

    def test_single_geom_conversion(self):
        segs = Segments([(0, 0, 1, 1)])
        geom = segs.geom()
        assert isinstance(geom, LineString)
        np.testing.assert_array_equal(
            np.array(geom.coords),
            np.array([
                [0, 0],
                [1, 1]
            ])
        )

    def test_multi_geom_conversion(self):
        segs = Segments([(0, 0, 1, 1), (1.5, 2, 3, 1)])
        geom = segs.geom()
        assert isinstance(geom, MultiLineString)
        assert len(geom.geoms) == 2
        np.testing.assert_array_equal(
            np.array(geom.geoms[0].coords),
            np.array([
                [0, 0],
                [1, 1]
            ])
        )
        np.testing.assert_array_equal(
            np.array(geom.geoms[1].coords),
            np.array([[
                1.5, 2],
                [3, 1]
            ])
        )
