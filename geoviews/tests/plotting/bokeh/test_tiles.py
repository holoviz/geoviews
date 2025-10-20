
import pytest

from geoviews.element import WMTS
from geoviews.plotting.bokeh import TilePlot
from geoviews.tile_sources import OSM

from .test_bokeh_plot import TestBokehPlot, bokeh_renderer


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
        tile_source = TilePlot(OSM).get_data(OSM, (0, 0, 0, 0), {})[1]["tile_source"]
        assert tile_source.max_zoom == 19
