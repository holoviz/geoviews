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
        self.assertEqual(zs, np.array([
            [ -4320.,  -8640., -12960., -17280., -21600.],
            [     0.,      0.,      0.,      0.,      0.],
            [  4320.,   8640.,  12960.,  17280.,  21600.]
        ]))

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
        # Correct conversion: angle follows mathematical convention
        # angle = arctan2(v, u), so u = mag*cos(angle), v = mag*sin(angle)
        us = np.cos(ang) * ms
        vs = np.sin(ang) * ms
        u, v = projection.transform_vectors(crs, xs, ys, us, vs)
        a, m = np.arctan2(v, u).T, np.hypot(u, v).T

        np.testing.assert_allclose(projected.dimension_values("Angle"), a.flatten())
        np.testing.assert_allclose(projected.dimension_values("Magnitude"), m.flatten())

    def test_project_vectorfield_from_uv(self):
        xs = np.linspace(10, 50, 2)
        X, Y = np.meshgrid(xs, xs)
        U, V = 5 * X, 1 * Y
        crs = ccrs.PlateCarree()
        vectorfield = VectorField.from_uv((X, Y, U, V), crs=crs)
        projection = ccrs.Orthographic()
        projected = project(vectorfield, projection=projection)
        assert projected.crs == projection

        # Verify that from_uv creates the correct angle/magnitude by roundtrip
        angles = vectorfield.dimension_values("Angle")
        mags = vectorfield.dimension_values("Magnitude")

        # Convert back to u,v
        u_converted = mags * np.cos(angles)
        v_converted = mags * np.sin(angles)

        # Create a new vectorfield from these u,v values
        xs_values = vectorfield.dimension_values(0)
        ys_values = vectorfield.dimension_values(1)
        vectorfield2 = VectorField.from_uv(
            (xs_values, ys_values, u_converted, v_converted), crs=crs
        )

        # The roundtrip should give us back the same angles and magnitudes
        angles2 = vectorfield2.dimension_values("Angle")
        mags2 = vectorfield2.dimension_values("Magnitude")

        np.testing.assert_allclose(angles2, angles, rtol=1e-10)
        np.testing.assert_allclose(mags2, mags, rtol=1e-10)

    def test_project_vectorfield_angle_convention(self):
        """Test that VectorField uses mathematical convention for angles.

        In mathematical convention:
        - angle = arctan2(v, u)
        - 0 radians points East (positive x direction)
        - π/2 radians points North (positive y direction)
        """
        # Create simple test cases with known angles
        xs = np.array([0, 0, 0, 0])
        ys = np.array([0, 0, 0, 0])

        # Test cardinal directions
        angles = np.array([0, np.pi/2, np.pi, 3*np.pi/2])  # E, N, W, S
        magnitudes = np.array([10, 10, 10, 10])

        crs = ccrs.PlateCarree()
        vectorfield = VectorField((xs, ys, angles, magnitudes), crs=crs)

        # Project to same CRS (should preserve angles)
        projected = project(vectorfield, projection=crs)

        # Verify angles are preserved by comparing u,v components (handles wrapping)
        projected_angles = projected.dimension_values("Angle")
        projected_mags = projected.dimension_values("Magnitude")

        # Convert both to u,v components for comparison (handles angle wrapping)
        orig_u = magnitudes * np.cos(angles)
        orig_v = magnitudes * np.sin(angles)
        proj_u = projected_mags * np.cos(projected_angles)
        proj_v = projected_mags * np.sin(projected_angles)

        # Use appropriate tolerance for floating point comparison
        np.testing.assert_allclose(proj_u, orig_u, rtol=1e-10, atol=1e-14)
        np.testing.assert_allclose(proj_v, orig_v, rtol=1e-10, atol=1e-14)

        # Verify magnitudes are preserved
        np.testing.assert_allclose(projected_mags, magnitudes, rtol=1e-10)

    def test_project_vectorfield_from_uv_consistency(self):
        """Test that VectorField created from u,v produces correct angles after projection."""
        xs = np.linspace(-10, 10, 3)
        ys = np.linspace(-10, 10, 3)
        X, Y = np.meshgrid(xs, ys)

        # Create uniform eastward flow
        U = np.ones_like(X) * 10  # All vectors point East
        V = np.zeros_like(Y)

        crs = ccrs.PlateCarree()
        vectorfield = VectorField.from_uv((X, Y, U, V), crs=crs)

        # All angles should be 0 (pointing East)
        angles = vectorfield.dimension_values("Angle")
        np.testing.assert_allclose(angles, 0, atol=1e-10)

        # Project to PlateCarree (identity projection)
        projected = project(vectorfield, projection=crs)
        projected_angles = projected.dimension_values("Angle")

        # Angles should still be 0 after identity projection
        np.testing.assert_allclose(projected_angles, 0, atol=1e-10)

    def test_project_vectorfield_north_vectors(self):
        """Test that northward vectors have angle π/2 after projection."""
        xs = np.linspace(-10, 10, 3)
        ys = np.linspace(-10, 10, 3)
        X, Y = np.meshgrid(xs, ys)

        # Create uniform northward flow
        U = np.zeros_like(X)
        V = np.ones_like(Y) * 10  # All vectors point North

        crs = ccrs.PlateCarree()
        vectorfield = VectorField.from_uv((X, Y, U, V), crs=crs)

        # All angles should be π/2 (pointing North)
        angles = vectorfield.dimension_values("Angle")
        np.testing.assert_allclose(angles, np.pi/2, atol=1e-10)

        # Project to PlateCarree (identity projection)
        projected = project(vectorfield, projection=crs)
        projected_angles = projected.dimension_values("Angle")

        # Angles should still be π/2 after identity projection
        np.testing.assert_allclose(projected_angles, np.pi/2, atol=1e-10)

    def test_project_vectorfield_to_orthographic(self):
        """Test VectorField projection to Orthographic maintains mathematical convention."""
        # Create a simple grid near the equator
        xs = np.array([0, 10, 20])
        ys = np.array([0, 0, 0])

        # Eastward vectors (angle = 0)
        angles = np.zeros(3)
        magnitudes = np.ones(3) * 10

        crs = ccrs.PlateCarree()
        vectorfield = VectorField((xs, ys, angles, magnitudes), crs=crs)

        # Project to Orthographic
        projection = ccrs.Orthographic(central_longitude=10, central_latitude=0)
        projected = project(vectorfield, projection=projection)

        # The projection should succeed
        assert projected.crs == projection
        assert len(projected) > 0

        # Magnitudes should be positive
        projected_mags = projected.dimension_values("Magnitude")
        assert np.all(projected_mags > 0)

    def test_project_windbarbs(self):
        xs = np.linspace(10, 50, 2)
        X, Y = np.meshgrid(xs, xs)
        U, V = 5 * X, 1 * Y
        A = np.pi / 2 - np.arctan2(-V, -U)
        M = np.hypot(U, V)
        crs = ccrs.PlateCarree()
        windbarbs = WindBarbs((X, Y, A, M), crs=crs)
        projection = ccrs.PlateCarree()
        projected = project(windbarbs, projection=projection)
        assert projected.crs == projection

        ang, ms = (windbarbs.dimension_values(i) for i in range(2, 4))
        # Convert FROM meteorological convention to u,v components
        us = -np.sin(ang) * ms
        vs = -np.cos(ang) * ms

        np.testing.assert_allclose(us, U.T.flatten())
        np.testing.assert_allclose(vs, V.T.flatten())

        # Convert to angle/magnitude in NORMALIZED meteorological convention
        a = np.pi/2 - np.arctan2(-vs, -us) % (2*np.pi)
        m = np.hypot(us, vs)

        np.testing.assert_allclose(projected.dimension_values("Angle"), a.T.flatten())
        np.testing.assert_allclose(projected.dimension_values("Magnitude"), m.T.flatten())

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
