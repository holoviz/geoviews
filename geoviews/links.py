import param

from holoviews.plotting.links import Link, RectanglesTableLink as HvRectanglesTableLink
try:
    from holoviews.plotting.bokeh.links import (
        LinkCallback, RectanglesTableLinkCallback as HvRectanglesTableLinkCallback
    )
except:
    from holoviews.plotting.bokeh.callbacks import (
        LinkCallback, RectanglesTableLinkCallback as HvRectanglesTableLinkCallback
)
from holoviews.core.util import dimension_sanitizer


class PointTableLink(Link):
    """
    Defines a Link between a Points type and a Table which will
    display the projected coordinates.
    """

    point_columns = param.List(default=[])

    _requires_target = True

    def __init__(self, source, target, **params):
        if 'point_columns' not in params:
            dimensions = [dimension_sanitizer(d.name) for d in target.dimensions()[:2]]
            params['point_columns'] = dimensions
        super(PointTableLink, self).__init__(source, target, **params)


class VertexTableLink(Link):
    """
    Defines a Link between a Path type and a Table which will
    display the vertices of selected path.
    """

    vertex_columns = param.List(default=[])

    _requires_target = True

    def __init__(self, source, target, **params):
        if 'vertex_columns' not in params:
            dimensions = [dimension_sanitizer(d.name) for d in target.dimensions()[:2]]
            params['vertex_columns'] = dimensions
        super(VertexTableLink, self).__init__(source, target, **params)


class RectanglesTableLink(HvRectanglesTableLink):
    """
    Links a Rectangles element to a Table.
    """


class PointTableLinkCallback(LinkCallback):

    source_model = 'cds'
    target_model = 'cds'

    on_source_changes = ['data', 'patching']
    on_target_changes = ['data', 'patching']

    source_code = """
    const projections = Bokeh.require("core/util/projections");
    const [x, y] = point_columns
    const xs_column = source_cds.data[x];
    const ys_column = source_cds.data[y];
    const projected_xs = []
    const projected_ys = []
    for (let i = 0; i < xs_column.length; i++) {
      const  xv = xs_column[i]
      const yv = ys_column[i]
      const p = projections.wgs84_mercator.inverse([xv, yv])
      projected_xs.push(p[0])
      projected_ys.push(p[1])
    }
    target_cds.data[x] = projected_xs;
    target_cds.data[y] = projected_ys;
    for (const col of source_cds.columns()) {
       if ((col != x) && (col != y)) {
         target_cds.data[col] = source_cds.data[col]
       }
    }
    target_cds.change.emit()
    target_cds.data = target_cds.data
    """

    target_code = """
    var projections = Bokeh.require("core/util/projections");
    const [x, y] = point_columns
    const xs_column = target_cds.data[x];
    const ys_column = target_cds.data[y];
    const projected_xs = []
    const projected_ys = []
    const empty = []
    for (let i = 0; i < xs_column.length; i++) {
      const xv = xs_column[i]
      const yv = ys_column[i]
      const p = projections.wgs84_mercator.forward([xv, yv])
      projected_xs.push(p[0])
      projected_ys.push(p[1])
    }
    source_cds.data[x] = projected_xs;
    source_cds.data[y] = projected_ys;
    for (const col of target_cds.columns()) {
       if ((col != x) && (col != y)) {
         source_cds.data[col] = target_cds.data[col]
       }
    }
    source_cds.change.emit()
    source_cds.properties.data.change.emit()
    source_cds.data = source_cds.data
    """


class VertexTableLinkCallback(LinkCallback):

    source_model = 'cds'
    target_model = 'cds'

    on_source_changes = ['selected', 'data', 'patching']
    on_target_changes = ['data', 'patching']

    source_code = """
    const projections = Bokeh.require("core/util/projections");
    const index = source_cds.selected.indices[0];
    let xs_column, ys_column
    if (index == undefined) {
      xs_column = [];
      ys_column = [];
    } else {
      xs_column = source_cds.data['xs'][index];
      ys_column = source_cds.data['ys'][index];
    }
    if (xs_column == undefined) {
      xs_column = [];
      ys_column = [];
    }
    const projected_xs = []
    const projected_ys = []
    var empty = []
    for (let i = 0; i < xs_column.length; i++) {
      const x = xs_column[i]
      const y = ys_column[i]
      const p = projections.wgs84_mercator.inverse([x, y])
      projected_xs.push(p[0])
      projected_ys.push(p[1])
      empty.push(null)
    }
    const [x, y] = vertex_columns
    target_cds.data[x] = projected_xs
    target_cds.data[y] = projected_ys
    const length = projected_xs.length
    for (const col in target_cds.data) {
      let data;
      if (vertex_columns.indexOf(col) != -1) { continue; }
      else if (col in source_cds.data) {
        const path = source_cds.data[col][index];
        if ((path == undefined)) {
          data = empty;
        } else if (path.length == length) {
          data = source_cds.data[col][index];
        } else {
          data = empty;
        }
      } else {
        data = empty;
      }
      target_cds.data[col] = data;
    }
    target_cds.change.emit()
    target_cds.data = target_cds.data
    """

    target_code = """
    const projections = Bokeh.require("core/util/projections");
    const types = Bokeh.require("core/util/types")
    if (!source_cds.selected.indices.length) { return }
    const [x, y] = vertex_columns
    const xs_column = target_cds.data[x]
    const ys_column = target_cds.data[y]
    const projected_xs = []
    const projected_ys = []
    const points = []
    for (let i = 0; i < xs_column.length; i++) {
      const xv = xs_column[i]
      const yv = ys_column[i]
      const p = projections.wgs84_mercator.forward([xv, yv])
      projected_xs.push(p[0])
      projected_ys.push(p[1])
      points.push(i)
    }
    const index = source_cds.selected.indices[0]
    const xpaths = source_cds.data['xs']
    const ypaths = source_cds.data['ys']
    const length = source_cds.data['xs'].length
    for (const col in target_cds.data) {
      if ((col == x) || (col == y)) { continue; }
      if (!(col in source_cds.data)) {
        const empty = []
        for (i = 0; i < length; i++)
          empty.push([])
        source_cds.data[col] = empty
      }
      source_cds.data[col][index] = target_cds.data[col]
      for (const p of points) {
        for (let pindex = 0; pindex < xpaths.length; pindex++) {
          if (pindex == index) { continue }
          const xs = xpaths[pindex]
          const ys = ypaths[pindex]
          let column = source_cds.data[col][pindex]
          if (!types.isTypedArray(column))
            source_cds.data[col][pindex] = column = Array.from(column)
          if (column.length != xs.length) {
            for (let ind = 0; ind < xs.length; ind++) {
              column.push(null)
            }
          }
          for (let ind = 0; ind < xs.length; ind++) {
            if ((xs[ind] == xpaths[index][p]) && (ys[ind] == ypaths[index][p])) {
              column[ind] = target_cds.data[col][p]
              xs[ind] = projected_xs[p];
              ys[ind] = projected_ys[p];
            }
          }
        }
      }
    }
    xpaths[index] = projected_xs;
    ypaths[index] = projected_ys;
    source_cds.change.emit()
    source_cds.properties.data.change.emit();
    source_cds.data = source_cds.data
    """


class RectanglesTableLinkCallback(HvRectanglesTableLinkCallback):

    source_code = """
    const projections = Bokeh.require("core/util/projections");
    const xs = source_cds.data[source_glyph.x.field]
    const ys = source_cds.data[source_glyph.y.field]
    const ws = source_cds.data[source_glyph.width.field]
    const hs = source_cds.data[source_glyph.height.field]

    const x0 = []
    const x1 = []
    const y0 = []
    const y1 = []
    for (let i = 0; i < xs.length; i++) {
      const hw = ws[i]/2.
      const hh = hs[i]/2.
      const p1 = projections.wgs84_mercator.inverse([xs[i]-hw, ys[i]-hh])
      const p2 = projections.wgs84_mercator.inverse([xs[i]+hw, ys[i]+hh])
      x0.push(p1[0])
      x1.push(p2[0])
      y0.push(p1[1])
      y1.push(p2[1])
    }
    target_cds.data[columns[0]] = x0
    target_cds.data[columns[1]] = y0
    target_cds.data[columns[2]] = x1
    target_cds.data[columns[3]] = y1
    """

    target_code = """
    const projections = Bokeh.require("core/util/projections");
    const x0s = target_cds.data[columns[0]]
    const y0s = target_cds.data[columns[1]]
    const x1s = target_cds.data[columns[2]]
    const y1s = target_cds.data[columns[3]]

    const xs = []
    const ys = []
    const ws = []
    const hs = []
    for (let i = 0; i < x0s.length; i++) {
      const x0 = Math.min(x0s[i], x1s[i])
      const y0 = Math.min(y0s[i], y1s[i])
      const x1 = Math.max(x0s[i], x1s[i])
      const y1 = Math.max(y0s[i], y1s[i])
      const p1 = projections.wgs84_mercator.forward([x0, y0])
      const p2 = projections.wgs84_mercator.forward([x1, y1])
      xs.push((p1[0]+p2[0])/2.)
      ys.push((p1[1]+p2[1])/2.)
      ws.push(p2[0]-p1[0])
      hs.push(p2[1]-p1[1])
    }
    source_cds.data['x'] = xs
    source_cds.data['y'] = ys
    source_cds.data['width'] = ws
    source_cds.data['height'] = hs
    """

VertexTableLink.register_callback('bokeh', VertexTableLinkCallback)
PointTableLink.register_callback('bokeh', PointTableLinkCallback)
RectanglesTableLink.register_callback('bokeh', RectanglesTableLinkCallback)
