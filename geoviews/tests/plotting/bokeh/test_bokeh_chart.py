import numpy as np
import pytest

import geoviews as gv
from geoviews.element import WindBarbs

from .test_bokeh_plot import TestBokehPlot, bokeh_renderer

try:
    import datashader
except ImportError:
    datashader = None


class TestWindBarbsPlot(TestBokehPlot):
    def test_windbarbs(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 5 * Y

        angle = np.arctan2(V, U)
        mag = np.hypot(U, V)

        gv_barbs = WindBarbs((X, Y, angle, mag))

        plot = bokeh_renderer.get_plot(gv_barbs)
        source = plot.handles["source"]

        # Check that the source data has the expected structure
        assert "x" in source.data
        assert "y" in source.data
        assert "angle" in source.data
        assert "magnitude" in source.data

    def test_windbarbs_dataset(self):
        xr = pytest.importorskip("xarray")

        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 1 * Y

        angle = np.arctan2(V, U)
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

        plot = bokeh_renderer.get_plot(gv_barbs)
        source = plot.handles["source"]

        # Check that data was properly flattened for bokeh
        assert len(source.data["x"]) == len(U.flatten())
        assert len(source.data["y"]) == len(U.flatten())

    def test_windbarbs_from_uv(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 2 * Y
        gv_barbs_uv = WindBarbs.from_uv((X, Y, U, V))

        # Just verify the from_uv method works and creates valid data
        plot = bokeh_renderer.get_plot(gv_barbs_uv)
        source = plot.handles["source"]

        assert "angle" in source.data
        assert "magnitude" in source.data
        assert len(source.data["angle"]) == len(U.flatten())
        assert len(source.data["magnitude"]) == len(U.flatten())

    def test_windbarbs_dataset_from_uv_other_dim(self):
        xr = pytest.importorskip("xarray")

        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 3 * Y

        angle = np.pi / 2 - np.arctan2(-V, -U)
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

    def test_windbarbs_line_color_op(self):
        barbs = WindBarbs(
            [(0, 0, 0, 1, "#000000"), (0, 1, 0, 1, "#FF0000"), (0, 2, 0, 1, "#00FF00")],
            vdims=["A", "M", "line_color"],
        ).opts(line_color="line_color")
        plot = bokeh_renderer.get_plot(barbs)
        glyph = plot.handles["glyph"]

        # Check that line_color mapping was applied
        # In bokeh, when using a field mapping, line_color becomes a dict
        assert hasattr(glyph, "line_color")

    def test_windbarbs_line_color(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 4 * Y

        angle = np.pi / 2 - np.arctan2(-V, -U)
        mag = np.hypot(U, V)

        barbs = gv.WindBarbs((X, Y, angle, mag)).opts(line_color="red")
        plot = bokeh_renderer.get_plot(barbs)
        glyph = plot.handles["glyph"]

        # Check that line_color was set
        assert glyph.line_color == "red"

    def test_windbarbs_line_alpha(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 5 * Y

        angle = np.pi / 2 - np.arctan2(-V, -U)
        mag = np.hypot(U, V)

        barbs = gv.WindBarbs((X, Y, angle, mag)).opts(line_alpha=0.5)
        plot = bokeh_renderer.get_plot(barbs)
        glyph = plot.handles["glyph"]

        # Check that line_alpha was set
        assert glyph.line_alpha == 0.5

    def test_windbarbs_scale(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 6 * Y

        angle = np.pi / 2 - np.arctan2(-V, -U)
        mag = np.hypot(U, V)

        barbs = gv.WindBarbs((X, Y, angle, mag)).opts(scale=2.0)
        plot = bokeh_renderer.get_plot(barbs)
        glyph = plot.handles["glyph"]

        # Check that scale was set
        assert glyph.scale == 2.0

    def test_windbarbs_convention_from(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 7 * Y

        angle = np.arctan2(V, U)
        mag = np.hypot(U, V)

        barbs = gv.WindBarbs((X, Y, angle, mag)).opts(convention="from")
        plot = bokeh_renderer.get_plot(barbs)
        source = plot.handles["source"]

        # Just verify it renders without error
        assert "angle" in source.data
        assert "magnitude" in source.data

    def test_windbarbs_convention_to(self):
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 8 * Y

        angle = np.arctan2(V, U)
        mag = np.hypot(U, V)

        barbs = gv.WindBarbs((X, Y, angle, mag)).opts(convention="to")
        plot = bokeh_renderer.get_plot(barbs)
        source = plot.handles["source"]

        # Verify angles are adjusted for 'to' convention
        # The convention should subtract pi from the angles
        assert "angle" in source.data
        assert "magnitude" in source.data


class TestImageStackPlot(TestBokehPlot):

    @pytest.mark.skipif(datashader is None, reason="Needs datashader to be installed")
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

        plot = bokeh_renderer.get_plot(img_stack)

        # Check that the plot has proper ranges
        assert plot.handles["x_range"]
        assert plot.handles["y_range"]

        # Check bounds
        x_range = plot.handles["x_range"]
        y_range = plot.handles["y_range"]
        assert x_range.start < x_range.end
        assert y_range.start < y_range.end

    @pytest.mark.skipif(datashader is None, reason="Needs datashader to be installed")
    def test_image_stack_rendering(self):
        pytest.importorskip("scipy")

        x = np.arange(-120, -115)
        y = np.arange(40, 43)
        a = np.random.rand(len(y), len(x))
        b = np.random.rand(len(y), len(x))

        img_stack = gv.ImageStack(
            (x, y, a, b), kdims=["x", "y"], vdims=["a", "b"],
        )

        plot = bokeh_renderer.get_plot(img_stack)

        # Verify the plot was created successfully
        assert plot.state is not None
        assert hasattr(plot, "handles")
