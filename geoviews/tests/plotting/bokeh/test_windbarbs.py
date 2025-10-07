"""Tests for Bokeh WindBarbsPlot."""
import numpy as np
import pytest

import geoviews as gv
from geoviews import Store
from geoviews.element import WindBarbs

try:
    from bokeh.plotting import figure
    bokeh_renderer = Store.renderers['bokeh']
except ImportError:
    pytestmark = pytest.mark.skip('Bokeh not available')


class TestWindBarbsPlot:
    def test_windbarbs_simple(self):
        """Test basic wind barbs rendering."""
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 5 * Y

        angle = np.pi / 2 - np.arctan2(-V, -U)
        mag = np.hypot(U, V)

        gv_barbs = WindBarbs((X, Y, angle, mag))
        
        # Should be able to render without error
        plot = bokeh_renderer.get_plot(gv_barbs)
        assert plot is not None
        assert plot.state is not None

    def test_windbarbs_from_uv(self):
        """Test wind barbs created from U/V components."""
        x = np.linspace(-1, 1, 4)
        X, Y = np.meshgrid(x, x)
        U, V = 10 * X, 2 * Y

        gv_barbs = WindBarbs.from_uv((X, Y, U, V))
        
        # Should be able to render without error
        plot = bokeh_renderer.get_plot(gv_barbs)
        assert plot is not None
        assert plot.state is not None

    def test_windbarbs_scale(self):
        """Test wind barbs with custom scale."""
        x = np.array([0, 1, 2])
        y = np.array([0, 1, 2])
        angles = np.array([0, np.pi/4, np.pi/2])
        mags = np.array([10, 20, 30])

        gv_barbs = WindBarbs((x, y, angles, mags)).opts(scale=0.5)
        
        # Should be able to render without error
        plot = bokeh_renderer.get_plot(gv_barbs)
        assert plot is not None
        assert plot.state is not None

    def test_windbarbs_convention(self):
        """Test wind barbs with 'to' convention."""
        x = np.array([0, 1])
        y = np.array([0, 1])
        angles = np.array([0, np.pi/2])
        mags = np.array([15, 25])

        # Create plot with 'to' convention
        plot_class = bokeh_renderer.plotting_class(WindBarbs)
        plot = plot_class(WindBarbs((x, y, angles, mags)), convention='to')
        
        # Should be able to get data without error
        data, mapping, style = plot.get_data(WindBarbs((x, y, angles, mags)), {}, {})
        assert 'angle' in data
        assert 'magnitude' in data
