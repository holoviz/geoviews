import numpy as np
import xarray as xr
import geoviews as gv

from geoviews.element import WindBarbs

from holoviews.tests.plotting.matplotlib.test_plot import TestMPLPlot
from holoviews.tests.plotting.utils import ParamLogStream

from geoviews import Store

gv.extension("matplotlib")
mpl_renderer = Store.renderers["matplotlib"]


class TestWindBarbsPlot(TestMPLPlot):
    def test_windbarbs(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 0 * Y

        mag = np.sqrt(U**2 + V**2)
        angle = (np.pi / 2.0) - np.arctan2(U / mag, V / mag)

        gv_barbs = WindBarbs((X, Y, angle, mag))

        fig = gv.render(gv_barbs)
        mpl_barbs = fig.axes[0].get_children()[0]
        np.testing.assert_almost_equal(mpl_barbs.u.data, U.T.flatten())
        np.testing.assert_almost_equal(mpl_barbs.v.data, V.flatten())

    def test_windbarbs_dataset(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 0 * Y

        mag = np.sqrt(U**2 + V**2)
        angle = (np.pi / 2.0) - np.arctan2(U / mag, V / mag)

        xr.Dataset(
            {
                "u": (["y", "x"], U),
                "v": (["y", "x"], V),
                "ang": (["x", "y"], angle),
                "mag": (["x", "y"], mag),
            },
            coords={"x": X[:, 0], "y": Y[0, :]},
        )

        gv_barbs = WindBarbs((X, Y, angle, mag))
        fig = gv.render(gv_barbs)
        mpl_barbs = fig.axes[0].get_children()[0]
        np.testing.assert_almost_equal(mpl_barbs.u.data, U.T.flatten())
        np.testing.assert_almost_equal(mpl_barbs.v.data, V.flatten())

    def test_windbarbs_from_uv_components(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 0 * Y

        gv_barbs = WindBarbs((X, Y, U, V)).opts(from_uv_components=True)

        fig = gv.render(gv_barbs)
        mpl_barbs = fig.axes[0].get_children()[0]
        np.testing.assert_almost_equal(mpl_barbs.u.data, U.flatten())
        np.testing.assert_almost_equal(mpl_barbs.v.data, V.flatten())

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
        U, V = 10 * X, 0 * Y

        mag = np.sqrt(U**2 + V**2)
        angle = (np.pi / 2.0) - np.arctan2(U / mag, V / mag)

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
        U, V = 10 * X, 0 * Y

        mag = np.sqrt(U**2 + V**2)
        angle = (np.pi / 2.0) - np.arctan2(U / mag, V / mag)

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
        U, V = 10 * X, 0 * Y

        mag = np.sqrt(U**2 + V**2)
        angle = (np.pi / 2.0) - np.arctan2(U / mag, V / mag)

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
        U, V = 10 * X, 0 * Y

        mag = np.sqrt(U**2 + V**2)
        angle = (np.pi / 2.0) - np.arctan2(U / mag, V / mag)

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
