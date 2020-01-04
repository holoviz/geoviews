import os

from bokeh.models import CustomJS, CustomAction, PolyEditTool

from holoviews.streams import Stream, PolyEdit, PolyDraw
from holoviews.plotting.bokeh.callbacks import CDSCallback
from geoviews.plotting.bokeh.callbacks import  GeoPolyEditCallback, GeoPolyDrawCallback

from .models.custom_tools import PolyVertexEditTool, PolyVertexDrawTool


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


class PolyVertexEditCallback(GeoPolyEditCallback):

    split_code = """
    var vcds = vertex.data_source
    var vertices = vcds.selected.indices;
    var pcds = poly.data_source;
    var index = null;
    for (i = 0; i < pcds.data.xs.length; i++) {
        if (pcds.data.xs[i] === vcds.data.x) {
            index = i;
        }
    }
    if ((index == null) || !vertices.length) {return}
    var vertex = vertices[0];
    for (col of poly.data_source.columns()) {
        var data = pcds.data[col][index];
        var first = data.slice(0, vertex+1)
        var second = data.slice(vertex)
        pcds.data[col][index] = first
        pcds.data[col].splice(index+1, 0, second)
    }
    for (c of vcds.columns()) {
      vcds.data[c] = [];
    }
    pcds.change.emit()
    pcds.properties.data.change.emit()
    pcds.selection_manager.clear();
    vcds.change.emit()
    vcds.properties.data.change.emit()
    vcds.selection_manager.clear();
    """

    icon = os.path.join(os.path.dirname(__file__), 'icons', 'PolyBreak.png')

    def _create_vertex_split_link(self, action, poly_renderer,
                                  vertex_renderer, vertex_tool):
        cb = CustomJS(code=self.split_code, args={
            'poly': poly_renderer, 'vertex': vertex_renderer, 'tool': vertex_tool})
        action.callback = cb

    def initialize(self, plot_id=None):
        plot = self.plot
        stream = self.streams[0]
        element = self.plot.current_frame
        vertex_tool = None
        if all(s.shared for s in self.streams):
            tools = [tool for tool in plot.state.tools if isinstance(tool, PolyEditTool)]
            vertex_tool = tools[0] if tools else None
        renderer = plot.handles['glyph_renderer']
        if vertex_tool is None:
            vertex_style = dict({'size': 10, 'alpha': 0.8}, **stream.vertex_style)
            r1 = plot.state.scatter([], [], **vertex_style)
            tooltip = '%s Edit Tool' % type(element).__name__
            vertex_tool = PolyVertexEditTool(
                vertex_renderer=r1, custom_tooltip=tooltip, node_style=stream.node_style,
                end_style=stream.feature_style)
            action = CustomAction(action_tooltip='Split path', icon=self.icon)
            plot.state.add_tools(vertex_tool, action)
            self._create_vertex_split_link(action, renderer, r1, vertex_tool)
        vertex_tool.renderers.append(renderer)
        self._update_cds_vdims()
        CDSCallback.initialize(self, plot_id)



class PolyVertexDrawCallback(GeoPolyDrawCallback):

    def initialize(self, plot_id=None):
        plot = self.plot
        stream = self.streams[0]
        element = self.plot.current_frame
        kwargs = {}
        if stream.num_objects:
            kwargs['num_objects'] = stream.num_objects
        if stream.show_vertices:
            vertex_style = dict({'size': 10}, **stream.vertex_style)
            r1 = plot.state.scatter([], [], **vertex_style)
            kwargs['vertex_renderer'] = r1
        tooltip = '%s Draw Tool' % type(element).__name__
        poly_tool = PolyVertexDrawTool(
            drag=all(s.drag for s in self.streams),
            empty_value=stream.empty_value,
            renderers=[plot.handles['glyph_renderer']],
            node_style=stream.node_style,
            end_style=stream.feature_style,
            custom_tooltip=tooltip,
            **kwargs)
        plot.state.tools.append(poly_tool)
        self._update_cds_vdims()
        CDSCallback.initialize(self, plot_id)


callbacks = Stream._callbacks['bokeh']
callbacks[PolyVertexEdit] = PolyVertexEditCallback
callbacks[PolyVertexDraw] = PolyVertexDrawCallback
