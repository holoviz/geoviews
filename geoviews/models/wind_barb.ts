import {XYGlyph, XYGlyphView} from "@bokehjs/models/glyphs/xy_glyph"
import {LineVector} from "@bokehjs/core/property_mixins"
import type {PointGeometry} from "@bokehjs/core/geometry"
import type {Context2d} from "@bokehjs/core/util/canvas"
import type * as visuals from "@bokehjs/core/visuals"
import * as p from "@bokehjs/core/properties"
import {Selection} from "@bokehjs/models/selections/selection"

export interface WindBarbView extends WindBarb.Data {}

export class WindBarbView extends XYGlyphView {
  declare model: WindBarb
  declare visuals: WindBarb.Visuals

  protected override _paint(ctx: Context2d, indices: number[], data?: WindBarb.Data): void {
    const {sx, sy, angle, magnitude} = data ?? this
    const y = this.y
    const scale = this.model.scale

    for (const i of indices) {
      const screen_x = sx[i]
      const screen_y = sy[i]
      const a = angle.get(i)
      const mag = magnitude.get(i)
      const lat = y[i]

      if (!isFinite(screen_x + screen_y + a + mag + lat))
        continue

      this._draw_wind_barb(ctx, screen_x, screen_y, a, mag, scale, i)
    }
  }

  protected _draw_wind_barb(ctx: Context2d, cx: number, cy: number, angle: number, magnitude: number, scale: number, idx: number = 0): void {
    // Wind barb drawing using meteorological convention
    // magnitude is in knots (or appropriate units)
    // angle is in meteorological convention (direction wind comes FROM)
    // barbs point in the direction the wind is coming FROM

    const barb_length = this.model.barb_length * scale
    const barb_width = this.model.barb_width * scale
    const flag_width = this.model.flag_width * scale

    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(-angle)

    ctx.beginPath()

    this.visuals.line.apply(ctx, idx)
    ctx.strokeStyle = ctx.strokeStyle || "black"

    ctx.lineCap = "round"
    ctx.lineJoin = "round"

    // Determine barbs/flags based on magnitude
    // Standard increments: 50 knots = flag (triangle), 10 knots = full barb, 5 knots = half barb
    const mag_rounded = Math.round(magnitude / 5) * 5

    if (mag_rounded >= 5) {
      // Draw the main staff (pointing in direction wind is coming from)
      ctx.moveTo(0, 0)
      ctx.lineTo(0, -barb_length)
      ctx.stroke()

      let remaining = mag_rounded
      let y_offset = -barb_length
      const spacing = this.model.spacing * scale

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
        ctx.lineTo(barb_width, y_offset + barb_width * 0.2)
        ctx.stroke()
        y_offset += spacing
        remaining -= 10
      }

      // Draw 5-knot half-barb
      if (remaining >= 5) {
        ctx.beginPath()
        ctx.moveTo(0, y_offset)
        ctx.lineTo(barb_width / 2, y_offset + barb_width * 0.1)
        ctx.stroke()
      }
    } else {
      // For calm winds (< 5 knots), draw only a circle (no staff line)
      ctx.beginPath()
      ctx.arc(0, 0, this.model.calm_circle_radius * scale, 0, 2 * Math.PI)
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
      if (dist < 10 * this.model.scale) {  // Hit radius
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
    barb_length: p.Property<number>
    barb_width: p.Property<number>
    flag_width: p.Property<number>
    spacing: p.Property<number>
    calm_circle_radius: p.Property<number>
  }

  export type Visuals = XYGlyph.Visuals & {line: visuals.LineVector}

  export type Data = p.GlyphDataOf<Props>
}

export interface WindBarb extends WindBarb.Attrs {}

export class WindBarb extends XYGlyph {
  declare properties: WindBarb.Props
  declare __view_type__: WindBarbView

  constructor(attrs?: Partial<WindBarb.Attrs>) {
    super(attrs)
  }

  static override __module__ = "geoviews.models.wind_barb"

  static {
    this.prototype.default_view = WindBarbView

    this.define<WindBarb.Props>(({Float}) => ({
      angle:              [p.AngleSpec, {value: 0}],
      magnitude:          [p.NumberSpec, {value: 0}],
      scale:              [Float, 1.0],
      barb_length:        [Float, 30.0],
      barb_width:         [Float, 15.0],
      flag_width:         [Float, 15.0],
      spacing:            [Float, 6.0],
      calm_circle_radius: [Float, 3.0],
    }))

    this.mixins<LineVector>(LineVector)
  }
}
