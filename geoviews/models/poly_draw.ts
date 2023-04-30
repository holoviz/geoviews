import * as p from "@bokehjs/core/properties"
import {UIEvent} from "@bokehjs/core/ui_events"
import {keys} from "@bokehjs/core/util/object"
import {isArray} from "@bokehjs/core/util/types"
import {PolyDrawTool, PolyDrawToolView} from "@bokehjs/models/tools/edit/poly_draw_tool"

import {MultiLine} from "@bokehjs/models/glyphs/multi_line"
import {Patches} from "@bokehjs/models/glyphs/patches"
import {GlyphRenderer} from "@bokehjs/models/renderers/glyph_renderer"


export class PolyVertexDrawToolView extends PolyDrawToolView {
  model: PolyVertexDrawTool

  _split_path(x: number, y: number): void {
    for (let r=0; r<this.model.renderers.length; r++) {
      const renderer = this.model.renderers[r]
      const glyph: any = renderer.glyph
      const cds: any = renderer.data_source
      const [xkey, ykey] = [glyph.xs.field, glyph.ys.field]
      const xpaths = cds.data[xkey]
      const ypaths = cds.data[ykey]
      for (let index = 0; index < xpaths.length; index++) {
        let xs = xpaths[index]
        if (!isArray(xs)) {
          xs = Array.from(xs)
          cds.data[xkey][index] = xs
        }
        let ys = ypaths[index]
        if (!isArray(ys)) {
          ys = Array.from(ys)
          cds.data[ykey][index] = ys
        }
        for (let i = 0; i < xs.length; i++) {
          if ((xs[i] == x) && (ys[i] == y) && (i != 0) && (i != (xs.length-1))) {
            xpaths.splice(index+1, 0, xs.slice(i))
            ypaths.splice(index+1, 0, ys.slice(i))
            xs.splice(i+1)
            ys.splice(i+1)
            for (const column of cds.columns()) {
              if ((column !== xkey) && (column != ykey))
                cds.data[column].splice(index+1, 0, cds.data[column][index])
            }
            return
          }
        }
      }
    }
  }

  _snap_to_vertex(ev: UIEvent, x: number, y: number): [number, number] {
    if (this.model.vertex_renderer) {
      // If an existing vertex is hit snap to it
      const vertex_selected = this._select_event(ev, "replace", [this.model.vertex_renderer])
      const point_ds = this.model.vertex_renderer.data_source
      // Type once dataspecs are typed
      const point_glyph: any = this.model.vertex_renderer.glyph
      const [pxkey, pykey] = [point_glyph.x.field, point_glyph.y.field]
      if (vertex_selected.length) {
        // If existing vertex is hit split path at that location
        // converting to feature vertex
        const index = point_ds.selected.indices[0]
        if (pxkey)
          x = point_ds.data[pxkey][index]
        if (pykey)
          y = point_ds.data[pykey][index]
        if (ev.type != 'mousemove')
          this._split_path(x, y)
        point_ds.selection_manager.clear()
      }
    }
    return [x, y]
  }

  _set_vertices(xs: number[] | number, ys: number[] | number, styles?: any): void {
    if (this.model.vertex_renderer == null)
      return
    const point_glyph: any = this.model.vertex_renderer.glyph
    const point_cds = this.model.vertex_renderer.data_source
    const [pxkey, pykey] = [point_glyph.x.field, point_glyph.y.field]
    if (pxkey) {
      if (isArray(xs))
        point_cds.data[pxkey] = xs
      else
        point_glyph.x = {value: xs}
    }
    if (pykey) {
      if (isArray(ys))
        point_cds.data[pykey] = ys
      else
        point_glyph.y = {value: ys}
    }

    if (styles != null) {
      for (const key of keys(styles)) {
        point_cds.data[key] = styles[key]
        point_glyph[key] = {field: key}
      }
    } else {
      for (const col of point_cds.columns()) {
        point_cds.data[col] = []
      }
    }
    this._emit_cds_changes(point_cds, true, true, false)
  }

  _show_vertices(): void {
    if (!this.model.active ) { return }
    const xs: number[] = []
    const ys: number[] = []
    const styles: any = {}
    for (const key of keys((this.model as any).end_style))
      styles[key] = []
    for (let i=0; i<this.model.renderers.length; i++) {
      const renderer = this.model.renderers[i]
      const cds = renderer.data_source
      const glyph: any = renderer.glyph
      const [xkey, ykey] = [glyph.xs.field, glyph.ys.field]
      for (const array of cds.get_array(xkey)) {
        Array.prototype.push.apply(xs, array)
        for (const key of keys((this.model as any).end_style))
          styles[key].push((this.model as any).end_style[key])
        for (const key of keys((this.model as any).node_style)) {
          for (let index = 0; index < ((array as any).length-2); index++) {
            styles[key].push((this.model as any).node_style[key])
          }
        }
        for (const key of keys((this.model as any).end_style))
          styles[key].push((this.model as any).end_style[key])
      }
      for (const array of cds.get_array(ykey))
        Array.prototype.push.apply(ys, array)
      if (this._drawing && (i == (this.model.renderers.length-1))) {
        // Skip currently drawn vertex
        xs.splice(xs.length-1, 1)
        ys.splice(ys.length-1, 1)
        for (const key of keys(styles))
          styles[key].splice(styles[key].length-1, 1)
      }
    }
    this._set_vertices(xs, ys, styles)
  }

  _remove(): void {
    const renderer = this.model.renderers[0]
    const cds = renderer.data_source
    const glyph: any = renderer.glyph
    const [xkey, ykey] = [glyph.xs.field, glyph.ys.field]
    if (xkey) {
      const xidx = cds.data[xkey].length-1
      const xs = cds.get_array<number[]>(xkey)[xidx]
      xs.splice(xs.length-1, 1)
      if (xs.length == 1)
        (cds.data[xkey] as any).splice(xidx, 1)
    }
    if (ykey) {
      const yidx = cds.data[ykey].length-1
      const ys = cds.get_array<number[]>(ykey)[yidx]
      ys.splice(ys.length-1, 1)
      if (ys.length == 1)
        (cds.data[ykey] as any).splice(yidx, 1)
    }
    this._emit_cds_changes(cds)
    this._drawing = false;
    this._show_vertices()
  }
}

export namespace PolyVertexDrawTool {
  export type Attrs = p.AttrsOf<Props>
  export type Props = PolyDrawTool.Props & {
    node_style: p.Property<any>
    end_style:  p.Property<any>
  }
}

export interface PolyVertexDrawTool extends PolyVertexDrawTool.Attrs {}

export interface HasPolyGlyph {
  glyph: MultiLine | Patches
}

export class PolyVertexDrawTool extends PolyDrawTool {
  properties: PolyVertexDrawTool.Props

  renderers: (GlyphRenderer & HasPolyGlyph)[]

  constructor(attrs?: Partial<PolyVertexDrawTool.Attrs>) {
    super(attrs)
  }

  static __module__ = "geoviews.models.custom_tools"

  static {
    this.prototype.default_view = PolyVertexDrawToolView

    this.define<PolyVertexDrawTool.Props>(({Any}) => ({
      end_style:  [ Any, {} ],
      node_style: [ Any, {} ],
    }))
  }
}
