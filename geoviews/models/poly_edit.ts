import type * as p from "@bokehjs/core/properties"
import type {Dict} from "@bokehjs/core/types"
import type {GestureEvent, UIEvent, TapEvent} from "@bokehjs/core/ui_events"
import {entries} from "@bokehjs/core/util/object"
import {isArray} from "@bokehjs/core/util/types"
import type {MultiLine} from "@bokehjs/models/glyphs/multi_line"
import type {Patches} from "@bokehjs/models/glyphs/patches"
import type {GlyphRenderer} from "@bokehjs/models/renderers/glyph_renderer"
import type {HasXYGlyph} from "@bokehjs/models/tools/edit/edit_tool"
import {PolyEditTool, PolyEditToolView} from "@bokehjs/models/tools/edit/poly_edit_tool"

export interface HasPolyGlyph {
  glyph: MultiLine | Patches
}

export class PolyVertexEditToolView extends PolyEditToolView {
  declare model: PolyVertexEditTool

  override deactivate(): void {
    this._hide_vertices()
    if (this._selected_renderer == null) {
      return
    } else if (this._drawing) {
      this._remove_vertex()
      this._drawing = false
    }
    this._emit_cds_changes(this._selected_renderer.data_source, false, true, false)
  }

  override _pan(ev: GestureEvent): void {
    if (this._basepoint == null || this.model.vertex_renderer == null) {
      return
    }
    const points = this._drag_points(ev, [this.model.vertex_renderer])
    if (!ev.modifiers.shift) {
      this._move_linked(points)
    }
    if (this._selected_renderer != null) {
      this._selected_renderer.data_source.change.emit()
    }
  }

  override _pan_end(ev: GestureEvent): void {
    if (this._basepoint == null || this.model.vertex_renderer == null) {
      return
    }
    const points = this._drag_points(ev, [this.model.vertex_renderer])
    if (!ev.modifiers.shift) {
      this._move_linked(points)
    }
    this._emit_cds_changes(this.model.vertex_renderer.data_source, false, true, true)
    if (this._selected_renderer != null) {
      this._emit_cds_changes(this._selected_renderer.data_source)
    }
    this._basepoint = null
  }

  override _drag_points(ev: UIEvent, renderers: (GlyphRenderer & HasXYGlyph)[]): number[][] {
    if (this._basepoint == null) {
      return []
    }
    const [bx, by] = this._basepoint
    const points = []
    for (const renderer of renderers) {
      const basepoint = this._map_drag(bx, by, renderer)
      const point = this._map_drag(ev.sx, ev.sy, renderer)
      if (point == null || basepoint == null) {
        continue
      }
      const [x, y] = point
      const [px, py] = basepoint
      const [dx, dy] = [x-px, y-py]
      // Type once dataspecs are typed
      const glyph: any = renderer.glyph
      const cds = renderer.data_source
      const [xkey, ykey] = [glyph.x.field, glyph.y.field]
      for (const index of cds.selected.indices) {
        const point = []
        if (xkey) {
          const xs = cds.get<number>(xkey)
          point.push(xs[index])
          xs[index] += dx
        }
        if (ykey) {
          const ys = cds.get<number>(ykey)
          point.push(ys[index])
          ys[index] += dy
        }
        point.push(dx)
        point.push(dy)
        points.push(point)
      }
      cds.change.emit()
    }
    this._basepoint = [ev.sx, ev.sy]
    return points
  }

  override _set_vertices(xs: number[] | number, ys: number[] | number, styles?: {[key: string]: unknown[]}): void {
    if (this.model.vertex_renderer == null) {
      return
    }
    const point_glyph: any = this.model.vertex_renderer.glyph
    const point_cds = this.model.vertex_renderer.data_source
    const [pxkey, pykey] = [point_glyph.x.field, point_glyph.y.field]
    if (pxkey) {
      if (isArray(xs)) {
        point_cds.set(pxkey, xs)
      } else {
        point_glyph.x = {value: xs}
      }
    }
    if (pykey) {
      if (isArray(ys)) {
        point_cds.set(pykey, ys)
      } else {
        point_glyph.y = {value: ys}
      }
    }

    if (styles != null) {
      for (const [key, array] of entries(styles)) {
        point_cds.set(key, array)
        point_glyph[key] = {field: key}
      }
    } else {
      for (const col of point_cds.columns()) {
        point_cds.set(col, [])
      }
    }
    this._emit_cds_changes(point_cds, true, true, false)
  }

  _move_linked(points: number[][]): void {
    if (this._selected_renderer == null) {
      return
    }
    const renderer = this._selected_renderer
    const glyph: any = renderer.glyph
    const cds: any = renderer.data_source
    const [xkey, ykey] = [glyph.xs.field, glyph.ys.field]
    const xpaths = cds.data[xkey]
    const ypaths = cds.data[ykey]
    for (const point of points) {
      const [x, y, dx, dy] = point
      for (let index = 0; index < xpaths.length; index++) {
        const xs = xpaths[index]
        const ys = ypaths[index]
        for (let i = 0; i < xs.length; i++) {
          if ((xs[i] == x) && (ys[i] == y)) {
            xs[i] += dx
            ys[i] += dy
          }
        }
      }
    }
  }

  override _tap(ev: TapEvent): void {
    if (this.model.vertex_renderer == null) {
      return
    }
    const renderer = this.model.vertex_renderer
    const point = this._map_drag(ev.sx, ev.sy, renderer)
    if (point == null) {
      return
    } else if (this._drawing && this._selected_renderer != null) {
      let [x, y] = point
      const cds = renderer.data_source
      // Type once dataspecs are typed
      const glyph: any = renderer.glyph
      const [xkey, ykey] = [glyph.x.field, glyph.y.field]
      const indices = cds.selected.indices
      ;[x, y] = this._snap_to_vertex(ev, x, y)
      const index = indices[0]
      cds.selected.indices = [index+1]
      if (xkey) {
        const xs = cds.get_array(xkey)
        const nx = xs[index]
        xs[index] = x
        xs.splice(index+1, 0, nx)
      }
      if (ykey) {
        const ys = cds.get_array(ykey)
        const ny = ys[index]
        ys[index] = y
        ys.splice(index+1, 0, ny)
      }
      cds.change.emit()
      this._emit_cds_changes(this._selected_renderer.data_source, true, false, true)
      return
    }
    this._select_event(ev, this._select_mode(ev), [renderer])
  }

  override _show_vertices(ev: UIEvent): void {
    if (!this.model.active) {
      return
    }

    const renderers = this._select_event(ev, "replace", this.model.renderers)
    if (renderers.length === 0) {
      this._hide_vertices()
      this._selected_renderer = null
      this._drawing = false
      return
    }

    const renderer = renderers[0]
    const glyph: any = renderer.glyph
    const cds = renderer.data_source
    const index = cds.selected.indices[0]
    const [xkey, ykey] = [glyph.xs.field, glyph.ys.field]
    let xs: number[]
    let ys: number[]
    if (xkey) {
      xs = cds.get<number[]>(xkey)[index]
      if (!isArray(xs)) {
        cds.get(xkey)[index] = xs = Array.from(xs)
      }
    } else {
      xs = glyph.xs.value
    }

    if (ykey) {
      ys = cds.get<number[]>(ykey)[index]
      if (!isArray(ys)) {
        cds.get(ykey)[index] = ys = Array.from(ys)
      }
    } else {
      ys = glyph.ys.value
    }
    const {end_style, node_style} = this.model
    const styles: {[key: string]: unknown[]} = {}
    for (const [key, val] of entries(end_style)) {
      styles[key] = [val]
    }
    for (const [key, val] of entries(node_style)) {
      for (let index = 0; index < xs.length - 2; index++) {
        styles[key].push(val)
      }
    }
    for (const [key, val] of entries(end_style)) {
      styles[key].push(val)
    }
    this._selected_renderer = renderer
    this._set_vertices(xs, ys, styles)
  }
}

export namespace PolyVertexEditTool {
  export type Attrs = p.AttrsOf<Props>

  export type Props = PolyEditTool.Props & {
    end_style:  p.Property<Dict<unknown>>
    node_style: p.Property<Dict<unknown>>
  }
}

export interface PolyVertexEditTool extends PolyVertexEditTool.Attrs {}

export class PolyVertexEditTool extends PolyEditTool {
  declare properties: PolyVertexEditTool.Props

  override renderers: (GlyphRenderer & HasPolyGlyph)[]

  constructor(attrs?: Partial<PolyVertexEditTool.Attrs>) {
    super(attrs)
  }

  static override __module__ = "geoviews.models.custom_tools"

  static {
    this.prototype.default_view = PolyVertexEditToolView

    this.define<PolyVertexEditTool.Props>(({Dict, Unknown}) => ({
      end_style:  [ Dict(Unknown), {} ],
      node_style: [ Dict(Unknown), {} ],
    }))
  }
}
