import param
import numpy as np
from holoviews.plotting.mpl.element import ColorbarPlot
from holoviews.util.transform import dim
from holoviews.core.dimension import dimension_name
from holoviews.plotting.util import get_min_distance
from holoviews.core.options import Store, abbreviated_exception


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

    from_uv_components = param.Boolean(default=False, doc="""
        If True, the vdims are expected to be in the form of
        wind components (U and V); else, wind direction and speed.""")

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


    def _get_us_vs(self, element, style, ranges):
        mag_dim = self.magnitude
        if self.from_uv_components:
            us = element.dimension_values(2, flat=False) if len(element.data) else []
            vs = element.dimension_values(3, flat=False) if len(element.data) else []
            uv_magnitudes = np.hypot(us, vs)  # unscaled
            radians = (np.pi / 2.0) - np.arctan2(us / uv_magnitudes, vs / uv_magnitudes)
            element = element.add_dimension("Angle", 4, radians, vdim=True)
            element = element.add_dimension("Magnitude", 5, uv_magnitudes, vdim=True)
            if mag_dim is None:
                mag_dim = element.get_dimension(5)
        else:
            radians = element.dimension_values(2) if len(element.data) else []
            if mag_dim is None:
                mag_dim = element.get_dimension(3)

        if isinstance(mag_dim, str):
            mag_dim = element.get_dimension(mag_dim)

        if isinstance(mag_dim, dim):
            magnitudes = mag_dim.apply(element, flat=True)
        else:
            magnitudes = element.dimension_values(mag_dim)

        if self.invert_axes:
            radians += 1.5 * np.pi

        # Compute U, V to serialize to matplotlib
        # Even if it's from U, V components, we still need to re-compute
        # because operations may have been applied to magnitudes
        if not self.from_uv_components or isinstance(mag_dim, dim):
            us = magnitudes * np.cos(radians.flatten())
            vs = magnitudes * np.sin(radians.flatten())

        return us, vs

    def get_data(self, element, ranges, style):
        # Compute coordinates
        xidx, yidx = (1, 0) if self.invert_axes else (0, 1)
        xs = element.dimension_values(xidx) if len(element.data) else []
        ys = element.dimension_values(yidx) if len(element.data) else []

        # Compute vector angle and magnitude
        us, vs = self._get_us_vs(element, style, ranges)
        args = (xs, ys, us, vs)

        # Process style
        with abbreviated_exception():
            style = self._apply_transforms(element, ranges, style)
        if "vmin" in style:
            style["clim"] = (style.pop("vmin"), style.pop("vmax"))
        if "c" in style:
            style["array"] = style.pop("c")
        if "pivot" not in style:
            style["pivot"] = "tip"

        return args, style, {}

    def update_handles(self, key, axis, element, ranges, style):
        args, style, axis_kwargs = self.get_data(element, ranges, style)

        # Set magnitudes, angles and colors if supplied.
        barbs = self.handles["artist"]
        barbs.set_offsets(np.column_stack(args[:2]))
        if "color" in style:
            barbs.set_facecolors(style["color"])
            barbs.set_edgecolors(style["color"])
        if "array" in style:
            barbs.set_array(style["array"])
        if "clim" in style:
            barbs.set_clim(style["clim"])
        if "linewidth" in style:
            barbs.set_linewidths(style["linewidth"])
        return axis_kwargs
