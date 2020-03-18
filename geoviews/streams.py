import os

from bokeh.models import CustomJS, CustomAction, PolyEditTool

from holoviews.core.ndmapping import UniformNdMapping
from holoviews.streams import Stream, PolyEdit, PolyDraw, CDSStream


class PolyVertexEdit(PolyEdit):
    """
    Attaches a PolyVertexEditTool and syncs the datasource.

    shared: boolean
        Whether PolyEditTools should be shared between multiple elements

    node_style: dict
        A dictionary specifying the style options for the intermediate nodes.

    feature_style: dict
        A dictionary specifying the style options for the intermediate nodes.
    """

    def __init__(self, node_style={}, feature_style={}, **params):
        self.node_style = node_style
        self.feature_style = feature_style
        super(PolyVertexEdit, self).__init__(**params)


class PolyVertexDraw(PolyDraw):
    """
    Attaches a PolyVertexDrawTool and syncs the datasource.

    shared: boolean
        Whether PolyEditTools should be shared between multiple elements

    node_style: dict
        A dictionary specifying the style options for the intermediate nodes.

    feature_style: dict
        A dictionary specifying the style options for the intermediate nodes.
    """

    def __init__(self, node_style={}, feature_style={}, **params):
        self.node_style = node_style
        self.feature_style = feature_style
        super(PolyVertexDraw, self).__init__(**params)


class TriMeshEdit(CDSStream):
    
    @property
    def element(self):
        source = self.source
        if isinstance(source, UniformNdMapping):
            source = source.last
        if not self.data:
            return source.nodes.clone([], id=None)
        return source.nodes.clone(self.data, id=None)
