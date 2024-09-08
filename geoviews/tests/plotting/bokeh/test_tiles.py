
import pytest
from holoviews.tests.plotting.bokeh.test_plot import TestBokehPlot, bokeh_renderer

from geoviews.element import WMTS
from geoviews.tile_sources import OSM


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

    def test_max_zoom_default(self):
        assert OSM.opts["max_zoom"] == 19
