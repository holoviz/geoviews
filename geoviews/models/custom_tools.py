from bokeh.core.properties import Instance, List, Dict, String, Any
from bokeh.models import Tool, ColumnDataSource, PolyEditTool, PolyDrawTool


class CheckpointTool(Tool):
    """
    Checkpoints the data on the supplied ColumnDataSources, allowing
    the RestoreTool to restore the data to a previous state.
    """

    sources = List(Instance(ColumnDataSource))


class RestoreTool(Tool):
    """
    Restores the data on the supplied ColumnDataSources to a previous
    checkpoint created by the CheckpointTool
    """

    sources = List(Instance(ColumnDataSource))


class ClearTool(Tool):
    """
    Clears the data on the supplied ColumnDataSources.
    """

    sources = List(Instance(ColumnDataSource))


class PolyVertexEditTool(PolyEditTool):

    node_style = Dict(String, Any, help="""
    Custom styling to apply to the intermediate nodes of a patch or line glyph.""")

    end_style = Dict(String, Any, help="""
    Custom styling to apply to the start and nodes of a patch or line glyph.""")


class PolyVertexDrawTool(PolyDrawTool):

    node_style = Dict(String, Any, help="""
    Custom styling to apply to the intermediate nodes of a patch or line glyph.""")

    end_style = Dict(String, Any, help="""
    Custom styling to apply to the start and nodes of a patch or line glyph.""")
