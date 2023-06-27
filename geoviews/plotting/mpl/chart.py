import param
import numpy as np
from holoviews.plotting.mpl.element import ColorbarPlot
from holoviews.util.transform import dim
from holoviews.core.options import abbreviated_exception


class WindBarbsPlot(ColorbarPlot):
    """
    Barbs are traditionally used in meteorology as a way to plot the speed and
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

    convention = param.ObjectSelector(objects=["from", "to"], doc="""
        Convention to return direction; 'from' returns the direction the wind is coming from
        (meteorological convention), 'to' returns the direction the wind is going towards
        (oceanographic convention).""")

    style_opts = [
        "alpha",
        "color",
        "edgecolors",
        "facecolors",
        "linewidth",
        "marker",
        "visible",
        "cmap",
        "norm",
        # barb specific
        "length",
        "barbcolor",
        "flagcolor",
        "fill_empty",
        "rounding",
        "barb_increments",
        "flip_barb",
        "pivot",
        "sizes",
        "width",
    ]

    _nonvectorized_styles = [
        "alpha",
        "marker",
        "cmap",
        "visible",
        "norm",
        # TODO: clarify whether these are vectorized or not
        "length",
        "barbcolor",
        "flagcolor",
        "fill_empty",
        "rounding",
        "barb_increments",
        "flip_barb",
        "pivot",
        "sizes",
        "width",
    ]

    _plot_methods = dict(single="barbs")

    def _get_us_vs(self, element):
        radians = element.dimension_values(2) if len(element.data) else []

        mag_dim = element.get_dimension(3)
        if isinstance(mag_dim, dim):
            magnitudes = mag_dim.apply(element, flat=True)
        else:
            magnitudes = element.dimension_values(mag_dim)

        if self.convention == "to":
            radians -= np.pi

        if self.invert_axes:
            radians -= 0.5 * np.pi

        us = -magnitudes * np.sin(radians.flatten())
        vs = -magnitudes * np.cos(radians.flatten())

        return us, vs

    def get_data(self, element, ranges, style):
        # Compute coordinates
        xidx, yidx = (1, 0) if self.invert_axes else (0, 1)
        xs = element.dimension_values(xidx) if len(element.data) else []
        ys = element.dimension_values(yidx) if len(element.data) else []

        # Compute U and V components as required by matplotlib plt.barbs
        us, vs = self._get_us_vs(element)
        args = (xs, ys, us, vs)

        color = style.get('color', None)  # must do before apply transform
        flagcolor = style.get('flagcolor', None)
        barbcolor = style.get('barbcolor', None)

        # Process style
        with abbreviated_exception():
            style = self._apply_transforms(element, ranges, style)
        uses_color = ((isinstance(color, str) and color in element) or isinstance(color, dim))
        if uses_color and (flagcolor is not None or barbcolor is not None):
            self.param.warning(
                "Cannot declare style mapping for 'color' option and either "
                "'flagcolor' and 'barbcolor'; ignoring 'flagcolor' and 'barbcolor'.")
            style.pop('flagcolor', None)
            style.pop('barbcolor', None)
        if "vmin" in style:
            style["clim"] = (style.pop("vmin"), style.pop("vmax"))
        if "c" in style:
            style["array"] = style.pop("c")
        if "pivot" not in style:
            style["pivot"] = "tip"
        return args, style, {}

    def update_handles(self, key, axis, element, ranges, style):
        args, style, axis_kwargs = self.get_data(element, ranges, style)

        barbs = self.handles["artist"]
        barbs.set_offsets(np.column_stack(args[:2]))
        if "color" in style:
            if "flagcolor" not in style:
                barbs.set_facecolors(style["color"])
            if "barbcolor" not in style:
                barbs.set_edgecolors(style["color"])
        if "array" in style:
            barbs.set_array(style["array"])
        if "clim" in style:
            barbs.set_clim(style["clim"])
        if "linewidth" in style:
            barbs.set_linewidths(style["linewidth"])
        return axis_kwargs
