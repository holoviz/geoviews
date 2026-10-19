import pytest
from bokeh.models import CustomAction, CustomJSTransform, PolyDrawTool, PolyEditTool

import geoviews as gv
from geoviews.annotators import PathBreakingAnnotator
from geoviews.streams import PolyVertexDraw, PolyVertexEdit

from .test_bokeh_plot import bokeh_renderer

pytestmark = pytest.mark.usefixtures("bokeh_backend")


def test_annotator_action_tools():
    annotator = PathBreakingAnnotator(object=gv.Path([[(0, 0), (1, 1)]]))
    plot = bokeh_renderer.get_plot(annotator.plot)
    actions = {tuple(t.tags): t for t in plot.state.tools if isinstance(t, CustomAction)}
    source = plot.handles["source"]
    for tag, icon in [
        ("geoviews_checkpoint", "save"),
        ("geoviews_restore", "undo"),
        ("geoviews_clear", "reset"),
    ]:
        tool = actions[(tag,)]
        assert tool.icon == icon
        assert tool.callback.args["sources"] == [source]


def test_poly_vertex_draw():
    path = gv.Path([[(0, 0), (1, 1), (2, 0)]])
    PolyVertexDraw(
        source=path,
        show_vertices=True,
        node_style={"fill_color": "red"},
        feature_style={"fill_color": "blue", "size": 12},
    )
    plot = bokeh_renderer.get_plot(path)
    (tool,) = [t for t in plot.state.tools if isinstance(t, PolyDrawTool)]
    assert type(tool) is PolyDrawTool

    glyph = tool.vertex_renderer.glyph
    for key, node, end in [("fill_color", "red", "blue"), ("size", 10, 12)]:
        spec = getattr(glyph, key)
        assert spec.field == "x"
        assert isinstance(spec.transform, CustomJSTransform)
        assert spec.transform.args["tool"] is tool
        assert spec.transform.args["node"] == node
        assert spec.transform.args["end"] == end

    source = plot.handles["source"]
    (split,) = source.js_property_callbacks["change:data"]
    assert split.args["source"] is source


def test_poly_vertex_edit():
    path = gv.Path([[(0, 0), (1, 1), (2, 0)]])
    PolyVertexEdit(
        source=path, node_style={"fill_color": "red"}, feature_style={"fill_color": "blue"}
    )
    plot = bokeh_renderer.get_plot(path)
    (tool,) = [t for t in plot.state.tools if isinstance(t, PolyEditTool)]
    assert type(tool) is PolyEditTool
    source = plot.handles["source"]
    assert tool.renderers == [plot.handles["glyph_renderer"]]
    assert isinstance(tool.vertex_renderer.glyph.fill_color.transform, CustomJSTransform)

    (link,) = source.js_property_callbacks["change:data"]
    assert link.args["tool"] is tool
    (panstart,) = plot.state.js_event_callbacks["panstart"]
    assert panstart.args["source"] is source
    (snapshot,) = source.selected.js_property_callbacks["change:indices"]
    assert snapshot.args["source"] is source
