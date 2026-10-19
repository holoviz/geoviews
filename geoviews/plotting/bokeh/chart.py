"""Chart-based plot classes for Bokeh backend."""

import numpy as np
import param
from bokeh.models import CustomJS, Scatter
from holoviews.core.options import abbreviated_exception
from holoviews.plotting.bokeh.element import ColorbarPlot
from holoviews.plotting.bokeh.styles import mpl_to_bokeh
from holoviews.util.transform import dim

# Barb dimensions are relative to the marker radius (the staff length),
# so the legend, which draws markers at a fixed size, shrinks them too.
_WINDBARB_CODE_JS = """
export default (args, obj, {ctx, i, r, visuals}) => {
  const {source, barb_length, barb_width, flag_width, spacing, calm_circle_radius} = args
  const k = r / barb_length
  const bw = barb_width * k
  const fw = flag_width * k
  const sp = spacing * k
  const mag = Math.round(source.get_array("magnitude")[i] / 5) * 5
  if (!isFinite(mag)) {
    return
  }
  ctx.lineCap = "round"
  ctx.lineJoin = "round"
  if (mag < 5) {
    ctx.arc(0, 0, calm_circle_radius * k, 0, 2 * Math.PI)
    visuals.line.apply(ctx, i)
    return
  }
  ctx.moveTo(0, 0)
  ctx.lineTo(0, -r)
  let remaining = mag
  let y = -r
  const flags = new Path2D()
  while (remaining >= 50) {
    flags.moveTo(0, y)
    flags.lineTo(fw, y + sp)
    flags.lineTo(0, y + 2 * sp)
    flags.closePath()
    y += 2.5 * sp
    remaining -= 50
  }
  while (remaining >= 10) {
    ctx.moveTo(0, y)
    ctx.lineTo(bw, y + 0.2 * bw)
    y += sp
    remaining -= 10
  }
  if (remaining >= 5) {
    ctx.moveTo(0, y)
    ctx.lineTo(bw / 2, y + 0.1 * bw)
  }
  visuals.line.apply(ctx, i)
  visuals.fill.apply(ctx, i, flags)
}
"""

_BARB_DEFAULTS = {
    "barb_length": 30.0,
    "barb_width": 15.0,
    "flag_width": 15.0,
    "spacing": 6.0,
    "calm_circle_radius": 3.0,
}


class WindBarbsPlot(ColorbarPlot):
    """Barbs are traditionally used in meteorology as a way to plot the speed and
    direction of wind observations, but can technically be used to plot any two
    dimensional vector quantity. As opposed to arrows, which give vector
    magnitude by the length of the arrow, the barbs give more quantitative
    information about the vector magnitude by putting slanted lines or a
    triangle for various increments in magnitude.

    The largest increment is given by a triangle (or "flag"). After those come full lines (barbs).
    The smallest increment is a half line. There is only, of course, ever at most 1 half line.
    If the magnitude is small and only needs a single half-line and no full lines or
    triangles, the half-line is offset from the end of the barb so that it can be
    easily distinguished from barbs with a single full line. The magnitude for the barb
    shown above would nominally be 65, using the standard increments of 50, 10, and 5.
    """

    padding = param.ClassSelector(default=0.05, class_=(int, float, tuple))

    convention = param.Selector(
        default="from",
        objects=["from", "to"],
        doc="""
        Convention to return direction; 'from' returns the direction the wind is coming from
        (meteorological convention), 'to' returns the direction the wind is going towards
        (oceanographic convention).""",
    )

    scale = param.Number(
        default=1.0,
        doc="Scaling factor for the size of the wind barbs.",
    )

    style_opts = [
        "cmap",
        "alpha",
        "line_color",
        "line_alpha",
        "line_width",
        "scale",
        "barb_length",
        "barb_width",
        "flag_width",
        "spacing",
        "calm_circle_radius",
        "visible",
    ]

    _nonvectorized_styles = [
        "cmap",
        "scale",
        "barb_length",
        "barb_width",
        "flag_width",
        "spacing",
        "calm_circle_radius",
    ]

    _plot_methods = dict(single="scatter")  # Placeholder, we override _init_glyph

    def _get_angle_magnitude(self, element):
        """Extract angle and magnitude from element data."""
        radians = element.dimension_values(2) if len(element.data) else np.array([])

        mag_dim = element.get_dimension(3)
        if isinstance(mag_dim, dim):
            magnitudes = mag_dim.apply(element, flat=True)
        else:
            magnitudes = element.dimension_values(mag_dim)

        if self.convention == "to":
            radians = radians - np.pi

        if self.invert_axes:
            radians = radians - 0.5 * np.pi

        return radians.flatten(), magnitudes.flatten()

    def get_data(self, element, ranges, style):
        # Get coordinates
        xidx, yidx = (1, 0) if self.invert_axes else (0, 1)
        xs = element.dimension_values(xidx) if len(element.data) else np.array([])
        ys = element.dimension_values(yidx) if len(element.data) else np.array([])

        # Get angle and magnitude
        angles, magnitudes = self._get_angle_magnitude(element)

        # Scatter rotates by the materialized (negated) angle, the opposite
        # direction of the old WindBarb glyph.
        data = {
            "x": xs,
            "y": ys,
            "angle": angles,
            "neg_angle": -angles,
            "magnitude": magnitudes,
        }
        mapping = {"x": "x", "y": "y", "angle": "neg_angle"}

        with abbreviated_exception():
            style = self._apply_transforms(element, data, ranges, style)

        if "scale" not in style:
            style["scale"] = self.scale

        self._get_hover_data(data, element)

        return data, mapping, style

    def _split_properties(self, properties):
        barb_args = {k: properties.pop(k, v) for k, v in _BARB_DEFAULTS.items()}
        scale = properties.pop("scale", self.scale)
        alpha = properties.pop("alpha", 1.0)
        line_color = properties.pop("line_color", "black")
        line_alpha = properties.pop("line_alpha", alpha)
        glyph_props = {
            "size": 2 * barb_args["barb_length"] * scale,
            "line_color": line_color,
            "line_alpha": line_alpha,
            # The flags are filled with the line style
            "fill_color": line_color,
            "fill_alpha": line_alpha,
        }
        if "line_width" in properties:
            glyph_props["line_width"] = properties.pop("line_width")
        return glyph_props, barb_args

    def _init_glyph(self, plot, mapping, properties):
        mapping["tags"] = ["apply_ranges" if self.apply_ranges else "no_apply_ranges"]
        properties = mpl_to_bokeh(properties)

        if "legend_field" in properties and "legend_label" in properties:
            del properties["legend_label"]

        if self.handles["x_range"].name in plot.extra_x_ranges and not self.subcoordinate_y:
            properties["x_range_name"] = self.handles["x_range"].name
        if self.handles["y_range"].name in plot.extra_y_ranges and not self.subcoordinate_y:
            properties["y_range_name"] = self.handles["y_range"].name

        if "name" not in properties:
            properties["name"] = properties.get("legend_label") or properties.get("legend_field")

        properties.pop("source", None)
        glyph_props, barb_args = self._split_properties(properties)

        source = self.handles["source"]
        marker = CustomJS(args=dict(source=source, **barb_args), code=_WINDBARB_CODE_JS)
        glyph = Scatter(marker="@windbarb", defs={"@windbarb": marker}, **mapping, **glyph_props)
        renderer = plot.add_glyph(source, glyph, **properties)
        return renderer, glyph

    def _update_glyph(self, renderer, properties, mapping, glyph, source, data):
        properties = dict(properties)
        glyph_props, barb_args = self._split_properties(properties)
        glyph.update(**mapping, **glyph_props)
        glyph.update(**{k: v for k, v in properties.items() if k in glyph.properties()})
        marker = glyph.defs["@windbarb"]
        marker.args = dict(marker.args, **barb_args)

        if data is not None:
            source.data.update(data)
