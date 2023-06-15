
import pytest

from geoviews.element import WMTS

from holoviews.tests.plotting.bokeh.test_plot import TestBokehPlot, bokeh_renderer

class TestWMTSPlot(TestBokehPlot):

    def test_xyzservices_tileprovider(self):
        xyzservices = pytest.importorskip("xyzservices")
        osm = xyzservices.providers.OpenStreetMap.Mapnik

        tiles = WMTS(osm)
        plot = bokeh_renderer.get_plot(tiles)
        glyph = plot.handles["glyph"]
        assert glyph.attribution == osm.html_attribution
        assert glyph.url == osm.build_url(scale_factor="@2x")
        assert glyph.max_zoom == osm.max_zoom
