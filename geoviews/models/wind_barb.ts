import {XYGlyph, XYGlyphView} from "@bokehjs/models/glyphs/xy_glyph"
import {LineVector} from "@bokehjs/core/property_mixins"
import type {PointGeometry} from "@bokehjs/core/geometry"
import type {Context2d} from "@bokehjs/core/util/canvas"
import type * as visuals from "@bokehjs/core/visuals"
import * as p from "@bokehjs/core/properties"
import {Indices} from "@bokehjs/core/types"
import {Selection} from "@bokehjs/models/selections/selection"

export class WindBarbView extends XYGlyphView {
  override model: WindBarb
  override visuals: WindBarb.Visuals

  protected override _paint(ctx: Context2d, indices: Indices, data?: any): void {
    const {sx, sy, _angle, _magnitude} = data ?? this
    const scale = this.model.scale

    for (const i of indices) {
      const x = sx[i]
      const y = sy[i]
      const angle = _angle.get(i)
      const mag = _magnitude.get(i)

      if (!isFinite(x + y + angle + mag))
        continue

      this._draw_wind_barb(ctx, x, y, angle, mag, scale, i)
    }
  }

  protected _draw_wind_barb(ctx: Context2d, cx: number, cy: number, angle: number, magnitude: number, scale: number, idx: number = 0): void {
    // Wind barb drawing using meteorological convention
    // magnitude is in knots (or appropriate units)
    // angle is the direction FROM which the wind blows
    
    const barb_length = 30 * scale
    const barb_width = 4 * scale
    const flag_width = 10 * scale
    
    ctx.save()
    ctx.translate(cx, cy)
    // In canvas, positive rotation is clockwise
    // We need to convert meteorological angle to canvas angle
    // Meteorological: 0 = from North, clockwise
    // Canvas: 0 = East, counter-clockwise
    // Adjustment: rotate by (90° - angle) and flip
    ctx.rotate(-angle + Math.PI / 2)
    
    ctx.beginPath()
    ctx.lineWidth = 1.5
    
    if (this.visuals.line.doit) {
      this.visuals.line.apply(ctx, idx)
      ctx.strokeStyle = ctx.strokeStyle || "black"
    } else {
      ctx.strokeStyle = "black"
    }
    
    ctx.lineCap = "round"
    ctx.lineJoin = "round"
    
    // Draw the main staff (pointing in direction of wind)
    ctx.moveTo(0, 0)
    ctx.lineTo(0, -barb_length)
    ctx.stroke()
    
    // Determine barbs/flags based on magnitude
    // Standard increments: 50 knots = flag (triangle), 10 knots = full barb, 5 knots = half barb
    const mag_rounded = Math.round(magnitude / 5) * 5
    
    if (mag_rounded >= 5) {
      let remaining = mag_rounded
      let y_offset = -barb_length
      const spacing = 6 * scale
      
      // Draw 50-knot flags (filled triangles)
      while (remaining >= 50) {
        ctx.fillStyle = ctx.strokeStyle || "black"
        ctx.beginPath()
        ctx.moveTo(0, y_offset)
        ctx.lineTo(flag_width, y_offset + spacing)
        ctx.lineTo(0, y_offset + spacing * 2)
        ctx.closePath()
        ctx.fill()
        y_offset += spacing * 2.5
        remaining -= 50
      }
      
      // Draw 10-knot barbs (full lines)
      while (remaining >= 10) {
        ctx.beginPath()
        ctx.moveTo(0, y_offset)
        ctx.lineTo(barb_width, y_offset + barb_width)
        ctx.stroke()
        y_offset += spacing
        remaining -= 10
      }
      
      // Draw 5-knot half-barb
      if (remaining >= 5) {
        ctx.beginPath()
        ctx.moveTo(0, y_offset)
        ctx.lineTo(barb_width / 2, y_offset + barb_width / 2)
        ctx.stroke()
      }
    } else {
      // For calm winds (< 5 knots), draw a circle
      ctx.beginPath()
      ctx.arc(0, 0, 3 * scale, 0, 2 * Math.PI)
      ctx.stroke()
    }
    
    ctx.restore()
  }

  protected override _hit_point(geometry: PointGeometry): Selection {
    const {sx, sy} = geometry

    const candidates = []

    for (let i = 0; i < this.data_size; i++) {
      const dx = this.sx[i] - sx
      const dy = this.sy[i] - sy
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < 30 * this.model.scale) {  // Hit radius
        candidates.push(i)
      }
    }

    return new Selection({indices: candidates})
  }

  override draw_legend_for_index(ctx: Context2d, {x0, x1, y0, y1}: {x0: number, y0: number, x1: number, y1: number}, _index: number): void {
    const cx = (x0 + x1) / 2
    const cy = (y0 + y1) / 2
    
    // Draw a representative wind barb in the legend
    this._draw_wind_barb(ctx, cx, cy, Math.PI / 4, 25, 0.5)
  }
}

export namespace WindBarb {
  export type Attrs = p.AttrsOf<Props>

  export type Props = XYGlyph.Props & {
    angle: p.AngleSpec
    magnitude: p.NumberSpec
    scale: p.Property<number>
  }

  export type Visuals = XYGlyph.Visuals & {line: visuals.LineVector}
}

export interface WindBarb extends WindBarb.Attrs {}

export class WindBarb extends XYGlyph {
  override properties: WindBarb.Props
  override __view_type__: WindBarbView

  constructor(attrs?: Partial<WindBarb.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = WindBarbView

    this.define<WindBarb.Props>(({Float}) => ({
      angle:     [p.AngleSpec, {value: 0}],
      magnitude: [p.NumberSpec, {value: 0}],
      scale:     [Float, 1.0],
    }))

    this.mixins<LineVector>(LineVector)
  }
}
