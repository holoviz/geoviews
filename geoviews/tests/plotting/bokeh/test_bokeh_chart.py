import numpy as np
import pytest

import geoviews as gv


class TestImageStackPlot:

    def test_image_stack_crs(self):
        pytest.importorskip("scipy")

        x = np.arange(-120, -115)
        y = np.arange(40, 43)
        a = np.random.rand(len(y), len(x))
        b = np.random.rand(len(y), len(x))

        img_stack = gv.ImageStack(
            (x, y, a, b), kdims=["x", "y"], vdims=["a", "b"],
        )
        data = img_stack.data
        np.testing.assert_almost_equal(data["x"], x)
        np.testing.assert_almost_equal(data["y"], y)
        np.testing.assert_almost_equal(data["a"], a)
        np.testing.assert_almost_equal(data["b"], b)

        fig = gv.render(img_stack, backend="bokeh")
        assert fig.x_range
        assert fig.y_range
