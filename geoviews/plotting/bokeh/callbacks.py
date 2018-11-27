import numpy as np

from holoviews.core.ndmapping import UniformNdMapping
from holoviews.plotting.bokeh.callbacks import (
    RangeXYCallback, BoundsCallback, BoundsXCallback, BoundsYCallback,
    PointerXYCallback, PointerXCallback, PointerYCallback, TapCallback,
    SingleTapCallback, DoubleTapCallback, MouseEnterCallback,
    MouseLeaveCallback, RangeXCallback, RangeYCallback, PolyDrawCallback,
    PointDrawCallback, BoxEditCallback, PolyEditCallback
)
from holoviews.streams import (
    Stream, PointerXY, RangeXY, RangeX, RangeY, PointerX, PointerY,
    BoundsX, BoundsY, Tap, SingleTap, DoubleTap, MouseEnter, MouseLeave,
    BoundsXY, PolyDraw, PolyEdit, PointDraw, BoxEdit
)

from ...element.geo import _Element, Shape
from ...util import project_extents
from ...operation import project
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
        data = {'x0': [], 'y0': [], 'x1': [], 'y1': []}
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
