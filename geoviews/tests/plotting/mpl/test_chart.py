import numpy as np
import pytest
from holoviews.tests.plotting.utils import ParamLogStream
from test_plot import TestMPLPlot

import geoviews as gv
from geoviews import Store
from geoviews.element import WindBarbs

try:
    import datashader
except ImportError:
    datashader = None

mpl_renderer = Store.renderers["matplotlib"]


class TestWindBarbsPlot(TestMPLPlot):
    def test_windbarbs(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 5 * Y

        angle = np.pi/2 - np.arctan2(-V, -U)  # meteorological convention
        mag = np.hypot(U, V)

        gv_barbs = WindBarbs((X, Y, angle, mag))

        fig = gv.render(gv_barbs)
        mpl_barbs = fig.axes[0].get_children()[0]
        np.testing.assert_almost_equal(mpl_barbs.u.data, U.T.flatten())
        np.testing.assert_almost_equal(mpl_barbs.v.data, V.T.flatten())

    def test_windbarbs_dataset(self):
        xr = pytest.importorskip("xarray")

        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 1 * Y

        angle = np.pi/2 - np.arctan2(-V, -U)  # meteorological convention
        mag = np.hypot(U, V)
        ds = xr.Dataset(
            {
                "u": (["y", "x"], U),
                "v": (["y", "x"], V),
                "a": (["y", "x"], angle),
                "m": (["y", "x"], mag),
            },
            coords={"x": x, "y": x},
        )

        gv_barbs = gv.WindBarbs(ds, ["x", "y"], ["a", "m"])

        fig = gv.render(gv_barbs)
        mpl_barbs = fig.axes[0].get_children()[0]
        np.testing.assert_almost_equal(mpl_barbs.u.data, U.T.flatten())
        np.testing.assert_almost_equal(mpl_barbs.v.data, V.T.flatten())

    def test_windbarbs_from_uv(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 2 * Y

        angle = np.pi/2 - np.arctan2(-V, -U)  # meteorological convention
        mag = np.hypot(U, V)

        gv_barbs = WindBarbs((X, Y, angle, mag))
        gv_barbs_uv = WindBarbs.from_uv((X, Y, U, V))

        np.testing.assert_almost_equal(gv_barbs.data["Angle"].T.flatten(), gv_barbs_uv.data["Angle"])
        np.testing.assert_almost_equal(gv_barbs.data["Magnitude"].T.flatten(), gv_barbs_uv.data["Magnitude"])

    def test_windbarbs_dataset_from_uv_other_dim(self):
        xr = pytest.importorskip("xarray")

        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 3 * Y

        angle = np.pi/2 - np.arctan2(-V, -U)  # meteorological (not used by from_uv)
        mag = np.hypot(U, V)
        ds = xr.Dataset(
            {
                "u": (["y", "x"], U),
                "v": (["y", "x"], V),
                "a": (["y", "x"], angle),
                "m": (["y", "x"], mag),
                "other": (["y", "x"], np.ones_like(mag)),
            },
            coords={"x": x, "y": -x},
        )

        gv_barbs = WindBarbs.from_uv(ds, ["x", "y"], ["u", "v", "other"])
        assert "other" in gv_barbs.data

    def test_windbarbs_color_op(self):
        barbs = WindBarbs(
            [(0, 0, 0, 1, "#000000"), (0, 1, 0, 1, "#FF0000"), (0, 2, 0, 1, "#00FF00")],
            vdims=["A", "M", "color"],
        ).opts(color="color")
        plot = mpl_renderer.get_plot(barbs)
        artist = plot.handles["artist"]
        self.assertEqual(
            artist.get_facecolors(),
            np.array([[0, 0, 0, 1], [1, 0, 0, 1], [0, 1, 0, 1]]),
        )

    def test_windbarbs_both_flagcolor_barbcolor(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 4 * Y

        angle = np.pi/2 - np.arctan2(-V, -U)  # meteorological convention
        mag = np.hypot(U, V)

        barbs = gv.WindBarbs((X, Y, angle, mag)).opts(
            colorbar=True, clim=(0, 50), flagcolor="red", barbcolor="blue"
        )
        plot = mpl_renderer.get_plot(barbs)
        artist = plot.handles["artist"]
        np.testing.assert_almost_equal(
            # red
            artist.get_facecolor(),
            np.array([[1.0, 0.0, 0.0, 1.0]]),
        )
        np.testing.assert_almost_equal(
            # blue
            artist.get_edgecolor(),
            np.array([[0.0, 0.0, 1.0, 1.0]]),
        )

    def test_windbarbs_flagcolor(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 5 * Y

        angle = np.pi/2 - np.arctan2(-V, -U)  # meteorological convention
        mag = np.hypot(U, V)

        barbs = gv.WindBarbs((X, Y, angle, mag)).opts(
            colorbar=True, clim=(0, 50), flagcolor="red"
        )
        plot = mpl_renderer.get_plot(barbs)
        artist = plot.handles["artist"]
        np.testing.assert_almost_equal(
            # red (RGBA)
            artist.get_facecolor(),
            np.array([[1.0, 0.0, 0.0, 1.0]]),
        )
        np.testing.assert_almost_equal(
            # red
            artist.get_edgecolor(),
            np.array([[1.0, 0.0, 0.0, 1.0]]),
        )

    def test_windbarbs_barbcolor(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 6 * Y

        angle = np.arctan2(V, U)
        mag = np.hypot(U, V)

        barbs = gv.WindBarbs((X, Y, angle, mag)).opts(
            colorbar=True, clim=(0, 50), barbcolor="red"
        )
        plot = mpl_renderer.get_plot(barbs)
        artist = plot.handles["artist"]
        np.testing.assert_almost_equal(
            # red (RGBA)
            artist.get_facecolor(),
            np.array([[1.0, 0.0, 0.0, 1.0]]),
        )
        np.testing.assert_almost_equal(
            # red
            artist.get_edgecolor(),
            np.array([[1.0, 0.0, 0.0, 1.0]]),
        )

    def test_windbarbs_color_warning(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 7 * Y

        angle = np.arctan2(V, U)
        mag = np.hypot(U, V)

        barbs = gv.WindBarbs((X, Y, angle, mag)).opts(
            colorbar=True,
            clim=(0, 50),
            color="Magnitude",
            flagcolor="black",
            barbcolor="black",
        )
        with ParamLogStream() as log:
            mpl_renderer.get_plot(barbs)
        log_msg = log.stream.read()
        warning = (
            "Cannot declare style mapping for 'color' option and either "
            "'flagcolor' and 'barbcolor'; ignoring 'flagcolor' and 'barbcolor'.\n"
        )
        self.assertEqual(log_msg, warning)


class TestImageStackPlot(TestMPLPlot):

    @pytest.mark.skipif(datashader is None, reason="Needs datashader to be installed")
    def test_image_stack_crs(self):
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

        fig = gv.render(img_stack)
        mpl_img = fig.axes[0].get_children()[0]
        np.testing.assert_almost_equal(mpl_img.get_extent(), (-120.5, -115.5, 39.5, 42.5))
        assert np.sum(mpl_img.get_array()) > 0
