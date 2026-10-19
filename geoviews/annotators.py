import cartopy.crs as ccrs
import param
from bokeh.models import CustomAction, CustomJS
from holoviews.annotators import (
    Annotator,
    PathAnnotator,
    PointAnnotator,
    PolyAnnotator,
    RectangleAnnotator,
    annotate,
)
from holoviews.plotting.links import DataLink, VertexTableLink as hvVertexTableLink
from panel.util import param_name

from .element import Path
from .links import (
    HvRectanglesTableLink,
    PointTableLink,
    RectanglesTableLink,
    VertexTableLink,
)
from .operation import project
from .streams import PolyVertexDraw, PolyVertexEdit

_CHECKPOINT_CODE_JS = """
for (const source of sources) {
  source._gv_buffer ??= []
  const entries = source.data instanceof Map ? [...source.data] : Object.entries(source.data)
  const data = {}
  for (const [key, column] of entries) {
    data[key] = Array.from(column, (v) => Array.isArray(v) || ArrayBuffer.isView(v) ? v.slice() : v)
  }
  source._gv_buffer.push(data)
}
"""

_RESTORE_CODE_JS = """
for (const source of sources) {
  const data = source._gv_buffer?.pop()
  if (data != null) {
    source.data = data
  }
}
"""

_CLEAR_CODE_JS = """
for (const source of sources) {
  source.clear()
}
"""

_CHECKPOINT_TAG = "geoviews_checkpoint"
_RESTORE_TAG = "geoviews_restore"
_CLEAR_TAG = "geoviews_clear"


def CheckpointTool():
    """Checkpoints the data on the ColumnDataSources, allowing the
    RestoreTool to restore the data to a previous state.
    """
    return CustomAction(
        icon="save",
        description="Checkpoint",
        tags=[_CHECKPOINT_TAG],
        callback=CustomJS(args={"sources": []}, code=_CHECKPOINT_CODE_JS),
    )


def RestoreTool():
    """Restores the data on the ColumnDataSources to a previous
    checkpoint created by the CheckpointTool.
    """
    return CustomAction(
        icon="undo",
        description="Restore",
        tags=[_RESTORE_TAG],
        callback=CustomJS(args={"sources": []}, code=_RESTORE_CODE_JS),
    )


def ClearTool():
    """Clears the data on the ColumnDataSources."""
    return CustomAction(
        icon="reset",
        description="Clear data",
        tags=[_CLEAR_TAG],
        callback=CustomJS(args={"sources": []}, code=_CLEAR_CODE_JS),
    )


Annotator._tools = [CheckpointTool, RestoreTool, ClearTool]
Annotator.table_transforms.append(project.instance(projection=ccrs.PlateCarree()))


def get_point_table_link(self, source, target):
    if hasattr(source.callback.inputs[0], "crs"):
        return PointTableLink(source, target)
    else:
        return DataLink(source, target)


PointAnnotator._link_type = get_point_table_link


def get_rectangles_table_link(self, source, target):
    if hasattr(source.callback.inputs[0], "crs"):
        return RectanglesTableLink(source, target)
    else:
        return HvRectanglesTableLink(source, target)


RectangleAnnotator._link_type = get_rectangles_table_link


def get_vertex_table_link(self, source, target):
    if hasattr(source.callback.inputs[0], "crs"):
        return VertexTableLink(source, target)
    else:
        return hvVertexTableLink(source, target)


PathAnnotator._vertex_table_link = get_vertex_table_link
PolyAnnotator._vertex_table_link = get_vertex_table_link


def initialize_tools(plot, element):
    """Initializes the Checkpoint and Restore tools."""
    cds = plot.handles["source"]
    for tag in (_CHECKPOINT_TAG, _RESTORE_TAG, _CLEAR_TAG):
        tools = plot.state.select(type=CustomAction, tags=[tag])
        if tools:
            tools[0].callback.args["sources"].append(cds)


Annotator._extra_opts["hooks"] = [initialize_tools]


class PathBreakingAnnotator(PathAnnotator):
    feature_style = param.Dict(
        default={"fill_color": "blue", "size": 10},
        doc="Styling to apply to the feature vertices.",
    )

    node_style = param.Dict(
        default={"fill_color": "indianred", "size": 6},
        doc="Styling to apply to the node vertices.",
    )

    def _init_stream(self):
        name = param_name(self.name)
        style_kwargs = dict(node_style=self.node_style, feature_style=self.feature_style)
        self._stream = PolyVertexDraw(
            source=self.plot,
            data={},
            num_objects=self.num_objects,
            show_vertices=self.show_vertices,
            tooltip=f"{name} Tool",
            **style_kwargs,
        )
        if self.edit_vertices:
            self._vertex_stream = PolyVertexEdit(
                source=self.plot, tooltip=f"{name} Edit Tool", **style_kwargs
            )


annotate._annotator_types[Path] = PathBreakingAnnotator
