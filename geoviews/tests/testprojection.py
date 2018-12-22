import numpy as np
import cartopy.crs as ccrs

from geoviews.element import Image
from geoviews.element.comparison import ComparisonTestCase
from geoviews.operation import project


class TestProjection(ComparisonTestCase):

    def test_image_latlon360_wrapping(self):
        xs = np.linspace(0, 360, 5)
        ys = np.linspace(-90, 90, 3)
        img = Image((xs, ys, xs[np.newaxis, :]*ys[:, np.newaxis]))
        proj = project(img, projection=ccrs.PlateCarree())
        zs = proj.dimension_values('z', flat=False)
        self.assertEqual(zs, np.array([
            [-24300.,     -0.,  -8100.],
            [     0.,      0.,      0.],
            [     0.,      0.,      0.],
            [     0.,      0.,      0.],
            [ 24300.,      0.,   8100.]
        ]))

    def test_image_project_latlon_to_mercator(self):
        xs = np.linspace(0, 360, 5)
        ys = np.linspace(-90, 90, 3)
        img = Image((xs, ys, xs[np.newaxis, :]*ys[:, np.newaxis]))
        proj = project(img)
        zs = proj.dimension_values('z', flat=False)
        self.assertEqual(zs, np.array([
            [-24300.,     -0.,  -8100.],
            [-24300.,     -0.,  -8100.],
            [     0.,      0.,      0.],
            [ 24300.,      0.,   8100.],
            [ 24300.,      0.,   8100.]
        ]))
