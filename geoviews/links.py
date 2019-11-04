import param

from holoviews.element import Path, Table, Points
from holoviews.plotting.links import Link
from holoviews.plotting.bokeh.callbacks import LinkCallback
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


class PointTableSelectionLink(Link):

    _requires_target = True


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


class PointTableSelectionLinkCallback(LinkCallback):

    source_model = 'selected'
    target_model = 'selected'

    on_source_changes = ['indices']
    on_target_changes = ['indices']

    source_code = """
    target_selected.indices = source_selected.indices
    """

    target_code = """
    source_selected.indices = target_selected.indices
    """


class PointTableLinkCallback(LinkCallback):

    source_model = 'cds'
    target_model = 'cds'

    on_source_changes = ['data', 'patching']
    on_target_changes = ['data', 'patching']

    source_code = """
    var projections = require("core/util/projections");
    [x, y] = point_columns
    var xs_column = source_cds.data[x];
    var ys_column = source_cds.data[y];
    var projected_xs = []
    var projected_ys = []
    for (i = 0; i < xs_column.length; i++) {
      var xv = xs_column[i]
      var yv = ys_column[i]
      p = projections.wgs84_mercator.inverse([xv, yv])
      projected_xs.push(p[0])
      projected_ys.push(p[1])
    }
    target_cds.data[x] = projected_xs;
    target_cds.data[y] = projected_ys;
    for (col of source_cds.columns()) {
       if ((col != x) && (col != y)) {
         target_cds.data[col] = source_cds.data[col]
       }
    }
    target_cds.change.emit()
    target_cds.data = target_cds.data
    """

    target_code = """
    var projections = require("core/util/projections");
    [x, y] = point_columns
    var xs_column = target_cds.data[x];
    var ys_column = target_cds.data[y];
    var projected_xs = []
    var projected_ys = []
    var empty = []
    for (i = 0; i < xs_column.length; i++) {
      var xv = xs_column[i]
      var yv = ys_column[i]
      p = projections.wgs84_mercator.forward([xv, yv])
      projected_xs.push(p[0])
      projected_ys.push(p[1])
    }
    source_cds.data[x] = projected_xs;
    source_cds.data[y] = projected_ys;
    for (col of target_cds.columns()) {
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
    var projections = require("core/util/projections");
    var index = source_cds.selected.indices[0];
    if (index == undefined) {
      var xs_column = [];
      var ys_column = [];
    } else {
      var xs_column = source_cds.data['xs'][index];
      var ys_column = source_cds.data['ys'][index];
    }
    if (xs_column == undefined) {
      var xs_column = [];
      var ys_column = [];
    }
    var projected_xs = []
    var projected_ys = []
    var empty = []
    for (i = 0; i < xs_column.length; i++) {
      var x = xs_column[i]
      var y = ys_column[i]
      p = projections.wgs84_mercator.inverse([x, y])
      projected_xs.push(p[0])
      projected_ys.push(p[1])
      empty.push(null)
    }
    [x, y] = vertex_columns
    target_cds.data[x] = projected_xs
    target_cds.data[y] = projected_ys
    var length = projected_xs.length
    for (var col in target_cds.data) {
      if (vertex_columns.indexOf(col) != -1) { continue; }
      else if (col in source_cds.data) {
        var path = source_cds.data[col][index];
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
    var projections = require("core/util/projections");
    if (!source_cds.selected.indices.length) { return }
    [x, y] = vertex_columns
    xs_column = target_cds.data[x]
    ys_column = target_cds.data[y]
    var projected_xs = []
    var projected_ys = []
    var points = []
    for (i = 0; i < xs_column.length; i++) {
      var xv = xs_column[i]
      var yv = ys_column[i]
      p = projections.wgs84_mercator.forward([xv, yv])
      projected_xs.push(p[0])
      projected_ys.push(p[1])
      points.push(i)
    }
    index = source_cds.selected.indices[0]
    const xpaths = source_cds.data['xs']
    const ypaths = source_cds.data['ys']
    var length = source_cds.data['xs'].length
    for (var col in target_cds.data) {
      if ((col == x) || (col == y)) { continue; }
      if (!(col in source_cds.data)) {
        var empty = []
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
          const column = source_cds.data[col][pindex]
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

    
VertexTableLink.register_callback('bokeh', VertexTableLinkCallback)
PointTableLink.register_callback('bokeh', PointTableLinkCallback)
PointTableSelectionLink.register_callback('bokeh', PointTableSelectionLinkCallback)
