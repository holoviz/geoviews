import param

import cartopy.crs as ccrs

from holoviews.annotators import (
    annotate, Annotator, PathAnnotator, PolyAnnotator, PointAnnotator,
    RectangleAnnotator
)
from holoviews.plotting.links import DataLink, VertexTableLink as hvVertexTableLink
from panel.util import param_name

from .element import Path
from .models.custom_tools import CheckpointTool, RestoreTool, ClearTool
from .links import VertexTableLink, PointTableLink, HvRectanglesTableLink, RectanglesTableLink
from .operation import project
from .streams import PolyVertexDraw, PolyVertexEdit

Annotator._tools = [CheckpointTool, RestoreTool, ClearTool]
Annotator.table_transforms.append(project.instance(projection=ccrs.PlateCarree()))

def get_point_table_link(self, source, target):
    if hasattr(source.callback.inputs[0], 'crs'):
        return PointTableLink(source, target)
    else:
        return DataLink(source, target)

PointAnnotator._link_type = get_point_table_link

def get_rectangles_table_link(self, source, target):
    if hasattr(source.callback.inputs[0], 'crs'):
        return RectanglesTableLink(source, target)
    else:
        return HvRectanglesTableLink(source, target)

RectangleAnnotator._link_type = get_rectangles_table_link

def get_vertex_table_link(self, source, target):
    if hasattr(source.callback.inputs[0], 'crs'):
        return VertexTableLink(source, target)
    else:
        return hvVertexTableLink(source, target)

PathAnnotator._vertex_table_link = get_vertex_table_link
PolyAnnotator._vertex_table_link = get_vertex_table_link

def initialize_tools(plot, element):
    """
    Initializes the Checkpoint and Restore tools.
    """
    cds = plot.handles['source']
    checkpoint = plot.state.select(type=CheckpointTool)
    restore = plot.state.select(type=RestoreTool)
    clear = plot.state.select(type=ClearTool)
    if checkpoint:
        checkpoint[0].sources.append(cds)
    if restore:
        restore[0].sources.append(cds)
    if clear:
        clear[0].sources.append(cds)

Annotator._extra_opts['hooks'] = [initialize_tools]


class PathBreakingAnnotator(PathAnnotator):

    feature_style = param.Dict(default={'fill_color': 'blue', 'size': 10}, doc="""
         Styling to apply to the feature vertices.""")

    node_style = param.Dict(default={'fill_color': 'indianred', 'size': 6}, doc="""
         Styling to apply to the node vertices.""")

    def _init_stream(self):
        name = param_name(self.name)
        style_kwargs = dict(node_style=self.node_style, feature_style=self.feature_style)
        self._stream = PolyVertexDraw(
            source=self.plot, data={}, num_objects=self.num_objects,
            show_vertices=self.show_vertices, tooltip='%s Tool' % name,
            **style_kwargs
        )
        if self.edit_vertices:
            self._vertex_stream = PolyVertexEdit(
                source=self.plot, tooltip='%s Edit Tool' % name,
                **style_kwargs
            )

annotate._annotator_types[Path] = PathBreakingAnnotator
