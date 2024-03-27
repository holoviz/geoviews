import type * as p from "@bokehjs/core/properties"
import type {Dict} from "@bokehjs/core/types"
import type {UIEvent} from "@bokehjs/core/ui_events"
import {isField} from "@bokehjs/core/vectorization"
import {keys, entries} from "@bokehjs/core/util/object"
import {isArray} from "@bokehjs/core/util/types"
import {assert} from "@bokehjs/core/util/assert"
import {PolyDrawTool, PolyDrawToolView} from "@bokehjs/models/tools/edit/poly_draw_tool"

import type {MultiLine} from "@bokehjs/models/glyphs/multi_line"
import type {Patches} from "@bokehjs/models/glyphs/patches"
import type {GlyphRenderer} from "@bokehjs/models/renderers/glyph_renderer"

export class PolyVertexDrawToolView extends PolyDrawToolView {
  declare model: PolyVertexDrawTool

  _split_path(x: number, y: number): void {
    for (const renderer of this.model.renderers) {
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
              if ((column !== xkey) && (column != ykey)) {
                cds.data[column].splice(index+1, 0, cds.data[column][index])
              }
            }
            return
          }
        }
      }
    }
  }

  override _snap_to_vertex(ev: UIEvent, x: number, y: number): [number, number] {
    const {vertex_renderer} = this.model
    if (vertex_renderer != null) {
      // If an existing vertex is hit snap to it
      const vertex_selected = this._select_event(ev, "replace", [vertex_renderer])
      const point_ds = vertex_renderer.data_source
      // Type once dataspecs are typed
      const point_glyph: any = vertex_renderer.glyph
      const [pxkey, pykey] = [point_glyph.x.field, point_glyph.y.field]
      if (vertex_selected.length > 0) {
        // If existing vertex is hit split path at that location
        // converting to feature vertex
        const index = point_ds.selected.indices[0]
        if (pxkey) {
          x = point_ds.get(pxkey)[index] as number
        }
        if (pykey) {
          y = point_ds.get(pykey)[index] as number
        }
        if (ev.type != "move") {
          this._split_path(x, y)
        }
        point_ds.selection_manager.clear()
      }
    }
    return [x, y]
  }

  override _set_vertices(xs: number[] | number, ys: number[] | number, styles?: any): void {
    const {vertex_renderer} = this.model
    if (vertex_renderer == null) {
      return
    }
    const point_glyph: any = vertex_renderer.glyph
    const point_cds = vertex_renderer.data_source
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
      for (const key of keys(styles)) {
        point_cds.set(key, styles[key])
        point_glyph[key] = {field: key}
      }
    } else {
      for (const col of point_cds.columns()) {
        point_cds.set(col, [])
      }
    }
    this._emit_cds_changes(point_cds, true, true, false)
  }

  override _show_vertices(): void {
    if (!this.model.active) {
      return
    }
    const {renderers, node_style, end_style} = this.model
    const xs: number[] = []
    const ys: number[] = []
    const styles: {[key: string]: unknown[]} = {}
    for (const key of keys(end_style)) {
      styles[key] = []
    }
    for (let i = 0; i < renderers.length; i++) {
      const renderer = renderers[i]
      const cds = renderer.data_source
      const glyph: any = renderer.glyph
      const [xkey, ykey] = [glyph.xs.field, glyph.ys.field]
      for (const array of cds.get_array(xkey)) {
        assert(isArray<number>(array))
        xs.push(...array)

        for (const [key, val] of entries(end_style)) {
          styles[key].push(val)
        }
        for (const [key, val] of entries(node_style)) {
          for (let index = 0; index < array.length - 2; index++) {
            styles[key].push(val)
          }
        }
        for (const [key, val] of entries(end_style)) {
          styles[key].push(val)
        }
      }
      for (const array of cds.get_array(ykey)) {
        assert(isArray<number>(array))
        ys.push(...array)
      }
      if (this._drawing && i == renderers.length - 1) {
        // Skip currently drawn vertex
        xs.splice(xs.length - 1, 1)
        ys.splice(ys.length - 1, 1)
        for (const [_, array] of entries(styles)) {
          array.splice(array.length - 1, 1)
        }
      }
    }
    this._set_vertices(xs, ys, styles)
  }

  override _remove(): void {
    const renderer = this.model.renderers[0]
    const cds = renderer.data_source
    const glyph = renderer.glyph
    if (isField(glyph.xs)) {
      const xkey = glyph.xs.field
      const array = cds.get_array<number[]>(xkey)
      const xidx = array.length - 1
      const xs = array[xidx]
      xs.splice(xs.length - 1, 1)
      if (xs.length == 1) {
        array.splice(xidx, 1)
      }
    }
    if (isField(glyph.ys)) {
      const ykey = glyph.ys.field
      const array = cds.get_array<number[]>(ykey)
      const yidx = array.length - 1
      const ys = array[yidx]
      ys.splice(ys.length - 1, 1)
      if (ys.length == 1) {
        array.splice(yidx, 1)
      }
    }
    this._emit_cds_changes(cds)
    this._drawing = false
    this._show_vertices()
  }
}

export namespace PolyVertexDrawTool {
  export type Attrs = p.AttrsOf<Props>
  export type Props = PolyDrawTool.Props & {
    node_style: p.Property<Dict<unknown>>
    end_style:  p.Property<Dict<unknown>>
  }
}

export interface PolyVertexDrawTool extends PolyVertexDrawTool.Attrs {}

export interface HasPolyGlyph {
  glyph: MultiLine | Patches
}

export class PolyVertexDrawTool extends PolyDrawTool {
  declare properties: PolyVertexDrawTool.Props

  override renderers: (GlyphRenderer & HasPolyGlyph)[]

  constructor(attrs?: Partial<PolyVertexDrawTool.Attrs>) {
    super(attrs)
  }

  static override __module__ = "geoviews.models.custom_tools"

  static {
    this.prototype.default_view = PolyVertexDrawToolView

    this.define<PolyVertexDrawTool.Props>(({Dict, Unknown}) => ({
      end_style:  [ Dict(Unknown), {} ],
      node_style: [ Dict(Unknown), {} ],
    }))
  }
}
