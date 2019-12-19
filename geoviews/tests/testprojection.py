import numpy as np
import cartopy.crs as ccrs

from geoviews.element import Image
from geoviews.element.comparison import ComparisonTestCase
from geoviews.operation import project


class TestProjection(ComparisonTestCase):

    def test_image_latlon360_wrapping(self):
        xs = np.linspace(72, 360, 5)
        ys = np.linspace(-60, 60, 3)
        img = Image((xs, ys, xs[np.newaxis, :]*ys[:, np.newaxis]))
        proj = project(img, projection=ccrs.PlateCarree())
        zs = proj.dimension_values('z', flat=False)
        self.assertEqual(zs, np.array([
            [-12960., -17280., -21600.,  -4320.,  -8640.],
            [     0.,      0.,      0.,      0.,      0.],
            [ 12960.,  17280.,  21600.,   4320.,   8640.]
        ]))

        # Check dataset property did not propagate
        self.assertNotEqual(proj.dataset, img.dataset)
        self.assertEqual(proj.dataset.data, proj.data)

    def test_image_project_latlon_to_mercator(self):
        xs = np.linspace(72, 360, 5)
        ys = np.linspace(-60, 60, 3)
        img = Image((xs, ys, xs[np.newaxis, :]*ys[:, np.newaxis]))
        proj = project(img)
        zs = proj.dimension_values('z', flat=False)
        self.assertEqual(zs, np.array([
            [-12960., -17280., -21600.,  -4320.,  -8640.],
            [     0.,      0.,      0.,      0.,      0.],
            [ 12960.,  17280.,  21600.,   4320.,   8640.]
        ]))

        # Check dataset property did not propagate
        self.assertNotEqual(proj.dataset, img.dataset)
        self.assertEqual(proj.dataset.data, proj.data)
