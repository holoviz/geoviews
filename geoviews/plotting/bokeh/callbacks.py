import os

import numpy as np

from bokeh.models import GraphRenderer, PointDrawTool, CustomJS
from holoviews.core.ndmapping import UniformNdMapping
from holoviews.plotting.bokeh.callbacks import (
    RangeXYCallback, BoundsCallback, BoundsXCallback, BoundsYCallback,
    PointerXYCallback, PointerXCallback, PointerYCallback, TapCallback,
    SingleTapCallback, DoubleTapCallback, MouseEnterCallback,
    MouseLeaveCallback, RangeXCallback, RangeYCallback, PolyDrawCallback,
    PointDrawCallback, BoxEditCallback, PolyEditCallback, CDSCallback
)
from holoviews.streams import (
    Stream, PointerXY, RangeXY, RangeX, RangeY, PointerX, PointerY,
    BoundsX, BoundsY, Tap, SingleTap, DoubleTap, MouseEnter, MouseLeave,
    BoundsXY, PolyDraw, PolyEdit, PointDraw, BoxEdit
)

from ...element.geo import _Element, Shape
from ...models.custom_tools import PolyVertexEditTool, PolyVertexDrawTool
from ...operation import project
from ...streams import PolyVertexEdit, PolyVertexDraw, TriMeshEdit
from ...util import project_extents
from .plot import GeoOverlayPlot


def get_cb_plot(cb, plot=None):
    """
    Finds the subplot with the corresponding stream.
    """
    plot = plot or cb.plot
    if isinstance(plot, GeoOverlayPlot):
        plots = [get_cb_plot(cb, p) for p in plot.subplots.values()]
        plots = [p for p in plots if any(s in cb.streams and getattr(s, '_triggering', False)
                                         for s in p.streams)]
        if plots:
            plot = plots[0]
    return plot


def skip(cb, msg, attributes):
    """
    Skips applying transforms if data is not geographic.
    """
    if not all(a in msg for a in attributes):
        return True
    plot = get_cb_plot(cb)
    return (not getattr(plot, 'geographic', False) or
            not hasattr(plot.current_frame, 'crs'))


def project_ranges(cb, msg, attributes):
    """
    Projects ranges supplied by a callback.
    """
    if skip(cb, msg, attributes):
        return msg

    plot = get_cb_plot(cb)
    x0, x1 = msg.get('x_range', (0, 1000))
    y0, y1 = msg.get('y_range', (0, 1000))
    extents = x0, y0, x1, y1
    x0, y0, x1, y1 = project_extents(extents, plot.projection,
                                     plot.current_frame.crs)
    coords = {'x_range': (x0, x1), 'y_range': (y0, y1)}
    return {k: v for k, v in coords.items() if k in attributes}


def project_point(cb, msg, attributes=('x', 'y')):
    """
    Projects a single point supplied by a callback
    """
    if skip(cb, msg, attributes): return msg
    plot = get_cb_plot(cb)
    x, y = msg.get('x', 0), msg.get('y', 0)
    crs = plot.current_frame.crs
    coordinates = crs.transform_points(plot.projection, np.array([x]), np.array([y]))
    msg['x'], msg['y'] = coordinates[0, :2]
    return {k: v for k, v in msg.items() if k in attributes}


def project_drawn(cb, msg):
    """
    Projects a drawn element to the declared coordinate system
    """
    stream = cb.streams[0]
    old_data = stream.data
    stream.update(data=msg['data'])
    element = stream.element
    stream.update(data=old_data)
    proj = cb.plot.projection
    if not isinstance(element, _Element) or element.crs == proj:
        return None
    crs = element.crs
    element.crs = proj
    return project(element, projection=crs)


def project_poly(cb, msg):
    if not msg['data']:
        return msg
    projected = project_drawn(cb, msg)
    if projected is None:
        return msg
    split = projected.split()
    data = {d.name: [el.dimension_values(d) for el in split]
            for d in projected.dimensions()}
    xd, yd = projected.kdims
    data['xs'] = data.pop(xd.name)
    data['ys'] = data.pop(yd.name)
    return {'data': data}



class GeoRangeXYCallback(RangeXYCallback):

    def _process_msg(self, msg):
        msg = super(GeoRangeXYCallback, self)._process_msg(msg)
        return project_ranges(self, msg, ('x_range', 'y_range'))

class GeoRangeXCallback(RangeXCallback):

    def _process_msg(self, msg):
        msg = super(GeoRangeXCallback, self)._process_msg(msg)
        return project_ranges(self, msg, ('x_range',))


class GeoRangeYCallback(RangeYCallback):

    def _process_msg(self, msg):
        msg = super(GeoRangeYCallback, self)._process_msg(msg)
        return project_ranges(self, msg, ('y_range',))


class GeoBoundsXYCallback(BoundsCallback):

    def _process_msg(self, msg):
        msg = super(GeoBoundsXYCallback, self)._process_msg(msg)
        if skip(self, msg, ('bounds',)): return msg
        plot = get_cb_plot(self)
        msg['bounds'] = project_extents(msg['bounds'], plot.projection,
                                        plot.current_frame.crs)
        return msg


class GeoBoundsXCallback(BoundsXCallback):

    def _process_msg(self, msg):
        msg = super(GeoBoundsXCallback, self)._process_msg(msg)
        if skip(self, msg, ('boundsx',)): return msg
        x0, x1 = msg['boundsx']
        plot = get_cb_plot(self)
        x0, _, x1, _ = project_extents((x0, 0, x1, 0), plot.projection,
                                        plot.current_frame.crs)
        return {'boundsx': (x0, x1)}


class GeoBoundsYCallback(BoundsYCallback):

    def _process_msg(self, msg):
        msg = super(GeoBoundsYCallback, self)._process_msg(msg)
        if skip(self, msg, ('boundsy',)): return msg
        y0, y1 = msg['boundsy']
        plot = get_cb_plot(self)
        _, y0, _, y1 = project_extents((0, y0, 0, y1), plot.projection,
                                        plot.current_frame.crs)
        return {'boundsy': (y0, y1)}


class GeoPointerXYCallback(PointerXYCallback):

    def _process_msg(self, msg):
        msg = super(GeoPointerXYCallback, self)._process_msg(msg)
        return project_point(self, msg)


class GeoPointerXCallback(PointerXCallback):

    def _process_msg(self, msg):
        msg = super(GeoPointerXCallback, self)._process_msg(msg)
        return project_point(self, msg, ('x',))


class GeoPointerYCallback(PointerYCallback):

    def _process_msg(self, msg):
        msg = super(GeoPointerYCallback, self)._process_msg(msg)
        return project_point(self, msg, ('y',))


class GeoTapCallback(TapCallback):

    def _process_msg(self, msg):
        msg = super(GeoTapCallback, self)._process_msg(msg)
        return project_point(self, msg)


class GeoSingleTapCallback(SingleTapCallback):

    def _process_msg(self, msg):
        msg = super(GeoSingleTapCallback, self)._process_msg(msg)
        return project_point(self, msg)


class GeoDoubleTapCallback(DoubleTapCallback):

    def _process_msg(self, msg):
        msg = super(GeoDoubleTapCallback, self)._process_msg(msg)
        return project_point(self, msg)


class GeoMouseEnterCallback(MouseEnterCallback):

    def _process_msg(self, msg):
        msg = super(GeoMouseEnterCallback, self)._process_msg(msg)
        return project_point(self, msg)


class GeoMouseLeaveCallback(MouseLeaveCallback):

    def _process_msg(self, msg):
        msg = super(GeoMouseLeaveCallback, self)._process_msg(msg)
        return project_point(self, msg)


class GeoPolyDrawCallback(PolyDrawCallback):

    def _process_msg(self, msg):
        msg = super(GeoPolyDrawCallback, self)._process_msg(msg)
        return project_poly(self, msg)

    def _update_cds_vdims(self):
        if isinstance(self.source, Shape):
            return
        super(GeoPolyDrawCallback, self)._update_cds_vdims()


class GeoPolyEditCallback(PolyEditCallback):

    def _update_cds_vdims(self):
        if isinstance(self.source, Shape):
            return
        super(GeoPolyEditCallback, self)._update_cds_vdims()


class GeoBoxEditCallback(BoxEditCallback):

    def _process_msg(self, msg):
        msg = super(GeoBoxEditCallback, self)._process_msg(msg)
        proj = self.plot.projection
        element = self.source
        if isinstance(element, UniformNdMapping):
            element = element.last

        if not isinstance(element, _Element) or element.crs == proj:
            return msg

        boxes = msg['data']
        data = dict(boxes, x0=[], y0=[], x1=[], y1=[])
        for extent in zip(boxes['x0'], boxes['y0'], boxes['x1'], boxes['y1']):
            x0, y0, x1, y1 = project_extents(extent, proj, element.crs)
            data['x0'].append(x0)
            data['y0'].append(y0)
            data['x1'].append(x1)
            data['y1'].append(y1)
        return {'data': data}


class GeoPointDrawCallback(PointDrawCallback):

    def _process_msg(self, msg):
        msg = super(GeoPointDrawCallback, self)._process_msg(msg)
        if not msg['data']:
            return msg
        projected = project_drawn(self, msg)
        if projected is None:
            return msg
        msg['data'] = projected.columns()
        return msg




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

    icon = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', '..', 'icons', 'PolyBreak.png'
        )
    )

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



class TriMeshEditCallback(CDSCallback):
    
    attributes = {'data': 'scatter_1_source.data'}
    models = ['scatter_1_source']
    
    on_changes = ['data']

    def initialize(self, plot_id=None):        
        super(CDSCallback, self).initialize(plot_id)
        plot = self.plot
        data = self._process_msg({'data': plot.handles['scatter_1_source'].data})['data']
        for stream in self.streams:
            stream.update(data=data)

        plot = self.plot
        element = plot.current_frame
        stream = self.streams[0]
        
        # Set up node renderer
        graph = self.plot.handles['glyph_renderer']
        graph.node_renderer.glyph.x = {'field': '_x_pos'}
        graph.node_renderer.glyph.y = {'field': '_y_pos'}
        graph.node_renderer.glyph.size = 10
        plot.state.renderers.append(graph.node_renderer)

        # Set up tool
        tool = PointDrawTool(renderers=[graph.node_renderer], add=False)
        plot.state.tools.append(tool)

        print(len(element.nodes))
        x, y, index = element.nodes.kdims
        node_indices = list(map(int, element.nodes['index']))
        cds = graph.node_renderer.data_source
        cds.add(node_indices, 'index')
        cds.add(element.nodes[y.name], '_x_pos')
        cds.add(element.nodes[x.name], '_y_pos')
        code = """
        let layout = {}
        for (let i = 0, endi = cds.data.index.length; i < endi; i++) {
           layout[cds.data.index[i]] = [cds.data._x_pos[i], cds.data._y_pos[i]]
        }
        layout_provider.graph_layout = layout;
        layout_provider.properties.graph_layout.change.emit()
        """
        js = CustomJS(args={'cds': graph.node_renderer.data_source, 'layout_provider': graph.layout_provider}, code=code)
        cds.js_on_change('data', js)
        
    def _process_msg(self, msg):
        msg = super(TriMeshEditCallback, self)._process_msg(msg)
        data = msg['data']
        plot = self.plot
        element = plot.current_frame
        x, y = element.nodes.kdims[:2]
        data[x.name] = data.pop('_x_pos')
        data[y.name] = data.pop('_y_pos')
        return self._transform(msg)



callbacks = Stream._callbacks['bokeh']

try:
    # Handle FreehandDraw (available in HoloViews 1.11.0)
    from holoviews.plotting.bokeh.callbacks import FreehandDrawCallback
    from holoviews.streams import FreehandDraw
    class GeoFreehandDrawCallback(FreehandDrawCallback):
        def _process_msg(self, msg):
            msg = super(GeoFreehandDrawCallback, self)._process_msg(msg)
            return project_poly(self, msg)

        def _update_cds_vdims(self):
            if isinstance(self.source, Shape):
                return
            super(GeoFreehandDrawCallback, self)._update_cds_vdims()
    callbacks[FreehandDraw] = GeoFreehandDrawCallback
except:
    pass

callbacks[RangeXY]     = GeoRangeXYCallback
callbacks[RangeX]      = GeoRangeXCallback
callbacks[RangeY]      = GeoRangeYCallback
callbacks[BoundsXY]    = GeoBoundsXYCallback
callbacks[BoundsX]     = GeoBoundsXCallback
callbacks[BoundsY]     = GeoBoundsYCallback
callbacks[PointerXY]   = GeoPointerXYCallback
callbacks[PointerX]    = GeoPointerXCallback
callbacks[PointerY]    = GeoPointerYCallback
callbacks[Tap]         = GeoTapCallback
callbacks[SingleTap]   = GeoSingleTapCallback
callbacks[DoubleTap]   = GeoDoubleTapCallback
callbacks[MouseEnter]  = GeoMouseEnterCallback
callbacks[MouseLeave]  = GeoMouseLeaveCallback
callbacks[PolyDraw]    = GeoPolyDrawCallback
callbacks[PolyEdit]    = GeoPolyEditCallback
callbacks[PointDraw]   = GeoPointDrawCallback
callbacks[BoxEdit]     = GeoBoxEditCallback
callbacks[PolyVertexEdit] = PolyVertexEditCallback
callbacks[PolyVertexDraw] = PolyVertexDrawCallback
callbacks[TriMeshEdit] = TriMeshEditCallback
