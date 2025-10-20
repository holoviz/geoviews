"""Chart-based plot classes for Bokeh backend."""

import numpy as np
import param
from holoviews.core.options import abbreviated_exception
from holoviews.plotting.bokeh.element import ColorbarPlot
from holoviews.plotting.bokeh.styles import mpl_to_bokeh
from holoviews.util.transform import dim

from ...models import WindBarb


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
        doc="""
        Scaling factor for the size of the wind barbs.""",
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

        # Build data dict
        data = {"x": xs, "y": ys, "angle": angles, "magnitude": magnitudes}

        # Build mapping
        mapping = {"x": "x", "y": "y", "angle": "angle", "magnitude": "magnitude"}

        # Process style
        with abbreviated_exception():
            style = self._apply_transforms(element, data, ranges, style)

        # Add scale to style if not present
        if "scale" not in style:
            style["scale"] = self.scale

        # Add hover data for tooltips
        self._get_hover_data(data, element)

        return data, mapping, style

    def _init_glyph(self, plot, mapping, properties):
        """
        Returns a Bokeh glyph object using our custom WindBarb glyph.
        """
        # Set up tags for apply_ranges
        mapping["tags"] = ["apply_ranges" if self.apply_ranges else "no_apply_ranges"]
        properties = mpl_to_bokeh(properties)

        # Handle legend properties
        if "legend_field" in properties and "legend_label" in properties:
            del properties["legend_label"]

        # Handle coordinate ranges
        if (
            self.handles["x_range"].name in plot.extra_x_ranges
            and not self.subcoordinate_y
        ):
            properties["x_range_name"] = self.handles["x_range"].name
        if (
            self.handles["y_range"].name in plot.extra_y_ranges
            and not self.subcoordinate_y
        ):
            properties["y_range_name"] = self.handles["y_range"].name

        if "name" not in properties:
            properties["name"] = properties.get("legend_label") or properties.get(
                "legend_field"
            )

        # Separate glyph properties from renderer properties
        # Glyph properties are those that the WindBarb glyph understands
        # Renderer properties are those that GlyphRenderer understands
        glyph_prop_names = [
            "scale",
            "line_color",
            "line_alpha",
            "line_width",
            "barb_length",
            "barb_width",
            "flag_width",
            "spacing",
            "calm_circle_radius",
        ]
        glyph_props = {}
        for prop in glyph_prop_names:
            if prop in properties:
                glyph_props[prop] = properties.pop(prop)

        # Remove 'source' if present (it's not a renderer property)
        properties.pop("source", None)

        # Create the glyph
        glyph = WindBarb(**mapping, **glyph_props)

        # Get the data source from handles (parent class should have set this)
        source = self.handles["source"]

        # Add the glyph to the plot
        renderer = plot.add_glyph(source, glyph, **properties)

        return renderer, glyph

    def _update_glyph(self, renderer, properties, mapping, glyph, source, data):
        """Update the glyph with new data or properties."""
        glyph.update(**mapping)
        props = {k: v for k, v in properties.items() if k in glyph.properties()}
        glyph.update(**props)

        if data is not None:
            source.data.update(data)
