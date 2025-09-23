from functools import cache

from bokeh import __version__ as bokeh_version
from bokeh.core.properties import Any, Dict, Instance, List, String
from bokeh.models import ColumnDataSource, PolyDrawTool, PolyEditTool, Tool
from packaging.requirements import Requirement

from .._warnings import warn


class _BokehCheck(Tool):
    _bokeh_require_version = "bokeh ==3.8.*"
    def __init__(self, *args, **kwargs):
        self._check_bokeh_version()
        super().__init__(*args, **kwargs)

    @classmethod
    @cache
    def _check_bokeh_version(cls) -> None:
        bokeh_req = Requirement(cls._bokeh_require_version)
        if bokeh_req.specifier.contains(bokeh_version):
            return
        msg = f"{cls.__name__} only official supported with {cls._bokeh_require_version}, you have {bokeh_version} installed."
        warn(msg, RuntimeWarning)


class CheckpointTool(_BokehCheck, Tool):
    """Checkpoints the data on the supplied ColumnDataSources, allowing
    the RestoreTool to restore the data to a previous state.
    """

    sources = List(Instance(ColumnDataSource))


class RestoreTool(_BokehCheck, Tool):
    """Restores the data on the supplied ColumnDataSources to a previous
    checkpoint created by the CheckpointTool
    """

    sources = List(Instance(ColumnDataSource))


class ClearTool(_BokehCheck, Tool):
    """Clears the data on the supplied ColumnDataSources."""

    sources = List(Instance(ColumnDataSource))


class PolyVertexEditTool(_BokehCheck, PolyEditTool):

    node_style = Dict(String, Any, help="""
    Custom styling to apply to the intermediate nodes of a patch or line glyph.""")

    end_style = Dict(String, Any, help="""
    Custom styling to apply to the start and nodes of a patch or line glyph.""")


class PolyVertexDrawTool(_BokehCheck, PolyDrawTool):

    node_style = Dict(String, Any, help="""
    Custom styling to apply to the intermediate nodes of a patch or line glyph.""")

    end_style = Dict(String, Any, help="""
    Custom styling to apply to the start and nodes of a patch or line glyph.""")
