import holoviews as hv
import pytest
from holoviews.tests.ui import expect, wait_until

from geoviews.annotators import Annotator, initialize_tools
from geoviews.streams import PolyVertexDraw, PolyVertexEdit

pytestmark = [pytest.mark.ui, pytest.mark.usefixtures("bokeh_backend")]

OPTS = dict(xlim=(0, 10), ylim=(0, 10), padding=0, frame_width=400, frame_height=400)

FIND_PLOT_JS = "Bokeh.index.query_one((v) => v.model.type == 'Figure')"


def screen(page, x, y):
    sx, sy = page.evaluate(
        f"""([x, y]) => {{
          const view = {FIND_PLOT_JS}
          return [view.frame.x_scale.compute(x), view.frame.y_scale.compute(y)]
        }}""",
        [x, y],
    )
    bbox = page.locator(".bk-events").bounding_box()
    return bbox["x"] + sx, bbox["y"] + sy


def press(page, x, y):
    page.mouse.move(x, y)
    page.mouse.down()
    page.wait_for_timeout(400)
    page.mouse.up()


def source_paths(page):
    return page.evaluate(
        f"""() => {{
          const view = {FIND_PLOT_JS}
          const renderer = view.model.renderers.find((r) => r.glyph.xs != null)
          const source = renderer.data_source
          const xs = source.get_array(renderer.glyph.xs.field)
          const ys = source.get_array(renderer.glyph.ys.field)
          return Array.from(xs, (x, i) => Array.from(x, (v, j) => [v, ys[i][j]]))
        }}"""
    )


def serve(serve_hv, element):
    page = serve_hv(element)
    expect(page.locator(".bk-events")).to_have_count(1)
    wait_until(lambda: page.evaluate(f"() => {FIND_PLOT_JS} != null"), page)
    return page


def test_checkpoint_restore_clear(serve_hv):
    path = hv.Path([[(1, 1), (5, 5), (9, 1)]]).opts(
        tools=[tool() for tool in Annotator._tools], hooks=[initialize_tools], **OPTS
    )
    page = serve(serve_hv, path)
    original = [[[1, 1], [5, 5], [9, 1]]]
    assert source_paths(page) == original

    page.get_by_title("Checkpoint").click()
    page.get_by_title("Clear data").click()
    wait_until(lambda: source_paths(page) == [], page)

    page.get_by_title("Restore").click()
    wait_until(lambda: source_paths(page) == original, page)


def test_poly_vertex_draw_split_on_snap(serve_hv):
    path = hv.Path([[(1, 5), (5, 5), (9, 5)]]).opts(**OPTS)
    stream = PolyVertexDraw(source=path, show_vertices=True)
    page = serve(serve_hv, path)
    page.get_by_title("Path Draw Tool").click()

    press(page, *screen(page, 5, 1))
    page.mouse.click(*screen(page, 5, 5))
    press(page, *screen(page, 5, 9))

    expected = [
        [[1, 5], [5, 5]],
        [[5, 5], [9, 5]],
        [[5, 1], [5, 5], [5, 9]],
    ]

    def check():
        paths = [[[round(x), round(y)] for x, y in p] for p in source_paths(page)]
        return paths == expected

    wait_until(check, page)
    wait_until(lambda: len(stream.data["xs"]) == 3, page)


@pytest.mark.parametrize("shift", [False, True])
def test_poly_vertex_edit_moves_linked_vertices(serve_hv, shift):
    path = hv.Path([[(1, 5), (5, 5)], [(5, 5), (9, 5)]]).opts(**OPTS)
    PolyVertexEdit(source=path)
    page = serve(serve_hv, path)
    page.get_by_title("Path Edit Tool").click()

    press(page, *screen(page, 3, 5))
    page.wait_for_timeout(200)

    if shift:
        page.keyboard.down("Shift")
    page.mouse.move(*screen(page, 5, 5))
    page.mouse.down()
    page.mouse.move(*screen(page, 5, 6.5), steps=5)
    page.mouse.move(*screen(page, 5, 8), steps=5)
    page.mouse.up()
    if shift:
        page.keyboard.up("Shift")

    moved = [5, 8]
    linked = [5, 5] if shift else moved
    expected = [[[1, 5], moved], [linked, [9, 5]]]

    def check():
        paths = [[[round(x), round(y)] for x, y in p] for p in source_paths(page)]
        return paths == expected

    wait_until(check, page)


def test_poly_vertex_styles(serve_hv):
    path = hv.Path([[(1, 5), (5, 5), (9, 5)]]).opts(**OPTS)
    PolyVertexDraw(
        source=path,
        show_vertices=True,
        node_style={"fill_color": "red"},
        feature_style={"fill_color": "blue"},
    )
    page = serve(serve_hv, path)
    page.get_by_title("Path Draw Tool").click()

    def colors():
        return page.evaluate(
            f"""() => {{
              const view = {FIND_PLOT_JS}
              const tool = view.model.toolbar.tools.find((t) => t.vertex_renderer != null)
              const rview = view.renderer_views.get(tool.vertex_renderer)
              const n = tool.vertex_renderer.data_source.get_length()
              const color = rview.glyph.fill_color
              return Array.from({{length: n}}, (_, i) => color.get(i))
            }}"""
        )

    blue, red = 0x0000FFFF, 0xFF0000FF
    wait_until(lambda: colors() == [blue, red, blue], page)
