import cartopy.crs as ccrs
import numpy as np
import pytest

from geoviews.element import Image, VectorField, WindBarbs
from geoviews.element.comparison import ComparisonTestCase
from geoviews.operation import project, project_image


class TestProjection(ComparisonTestCase):

    def test_image_latlon360_wrapping(self):
        pytest.importorskip("scipy")
        xs = np.linspace(72, 360, 5)
        ys = np.linspace(-60, 60, 3)
        img = Image((xs, ys, xs[np.newaxis, :]*ys[:, np.newaxis]))
        proj = project(img, projection=ccrs.PlateCarree())
        zs = proj.dimension_values('z', flat=False)
        self.assertEqual(zs, np.array([
            [ -4320.,  -8640., -12960., -17280., -21600.],
            [     0.,      0.,      0.,      0.,      0.],
            [  4320.,   8640.,  12960.,  17280.,  21600.]
        ]))

    def test_image_project_latlon_to_mercator(self):
        pytest.importorskip("scipy")
        xs = np.linspace(72, 360, 5)
        ys = np.linspace(-60, 60, 3)
        img = Image((xs, ys, xs[np.newaxis, :]*ys[:, np.newaxis]))
        proj = project(img)
        zs = proj.dimension_values('z', flat=False)
        self.assertEqual(zs, np.array(
            [[-12960., -17280., -21600.,  -4320.,  -8640.],
             [     0.,      0.,      0.,      0.,      0.],
             [ 12960.,  17280.,  21600.,   4320.,   8640.]]
        ))

    def test_project_vectorfield(self):
        xs = np.linspace(10, 50, 2)
        X, Y = np.meshgrid(xs, xs)
        U, V = 5 * X, 1 * Y
        A = np.arctan2(V, U)
        M = np.hypot(U, V)
        crs = ccrs.PlateCarree()
        vectorfield = VectorField((X, Y, A, M), crs=crs)
        projection = ccrs.Orthographic()
        projected = project(vectorfield, projection=projection)
        assert projected.crs == projection

        xs, ys, ang, ms = (vectorfield.dimension_values(i) for i in range(4))
        us = np.sin(ang) * -ms
        vs = np.cos(ang) * -ms
        u, v = projection.transform_vectors(crs, xs, ys, us, vs)
        a, m = np.arctan2(v, u).T, np.hypot(u, v).T

        np.testing.assert_allclose(projected.dimension_values("Angle"), a.flatten())
        np.testing.assert_allclose(projected.dimension_values("Magnitude"), m.flatten())

    def test_project_windbarbs(self):
        xs = np.linspace(10, 50, 2)
        X, Y = np.meshgrid(xs, xs)
        U, V = 5 * X, 1 * Y
        A = np.arctan2(V, U)
        M = np.hypot(U, V)
        crs = ccrs.PlateCarree()
        windbarbs = WindBarbs((X, Y, A, M), crs=crs)
        projection = ccrs.Orthographic()
        projected = project(windbarbs, projection=projection)
        assert projected.crs == projection

        xs, ys, ang, ms = (windbarbs.dimension_values(i) for i in range(4))
        us = np.sin(ang) * -ms
        vs = np.cos(ang) * -ms
        u, v = projection.transform_vectors(crs, xs, ys, us, vs)
        a, m = np.pi / 2 - np.arctan2(-v, -u).T, np.hypot(u, v).T

        np.testing.assert_allclose(projected.dimension_values("Angle"), a.flatten())
        np.testing.assert_allclose(projected.dimension_values("Magnitude"), m.flatten())

    def test_project_image_default_not_mask_extrapolated(self):
        """
        Test that mask_extrapolated can be set to False.
        """
        pytest.importorskip("scipy")
        proj_op = project_image.instance(projection=ccrs.Mercator(), mask_extrapolated=False)
        assert proj_op.mask_extrapolated is False, "mask_extrapolated should default to False"

    def test_image_mask_extrapolated_longitude_wrapping(self):
        """Test mask_extrapolated behavior with longitude data outside [-180, 180] range."""
        pytest.importorskip("scipy")

        # Create image with longitude data from 200 to 330 (outside standard range)
        xs = np.linspace(200, 330, 5)
        ys = np.linspace(-60, 60, 3)
        zs = np.ones((3, 5))  # Fill with constant value
        img = Image((xs, ys, zs), crs=ccrs.PlateCarree())

        # Test with mask_extrapolated=True (default)
        proj_op_masked = project_image.instance(projection=ccrs.PlateCarree())
        proj_op_masked.mask_extrapolated = True
        projected_masked = proj_op_masked(img)

        new_data = projected_masked.dimension_values('z', flat=False)
        # Should be all valid even with extrapolation
        assert not hasattr(new_data, "mask"), "Expected all values when mask_extrapolated=True with longitude 200-330 because auto-wrapping of lons"
        assert np.all(new_data == 1), "Expected all values to be valid when mask_extrapolated=True with longitude 200-330"

        # Test with mask_extrapolated=False
        proj_op_unmasked = project_image.instance(projection=ccrs.PlateCarree())
        proj_op_unmasked.mask_extrapolated = False
        projected_unmasked = proj_op_unmasked(img)

        # With mask_extrapolated=False, should get valid values via extrapolation
        unmasked_data = projected_unmasked.dimension_values('z', flat=False)
        # Should have valid values when extrapolation is allowed
        assert np.all(np.isfinite(unmasked_data)), "Expected all finite values when mask_extrapolated=False with longitude 200-330"

        # Now test with converted longitude range [-180, 180]
        # Convert longitude: ((lon + 180) % 360) - 180
        xs_converted = ((xs + 180) % 360) - 180  # Convert 200-330 to -160 to -30
        img_converted = Image((xs_converted, ys, zs), crs=ccrs.PlateCarree())

        # With converted coordinates, even mask_extrapolated=True should work
        projected_converted = proj_op_masked(img_converted)
        converted_data = projected_converted.dimension_values('z', flat=False)

        # Should have valid values because no extrapolation is needed
        assert np.all(np.isfinite(converted_data)), "Expected all finite values with converted longitude range [-180, 180]"

        # The converted data should match the unmasked extrapolated data (approximately)
        # since both should contain the same valid values
        assert np.allclose(unmasked_data, converted_data, equal_nan=True), "Extrapolated and converted data should be similar"
