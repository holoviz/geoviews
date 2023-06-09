import param
import numpy as np
from holoviews.plotting.mpl.element import ColorbarPlot
from holoviews.util.transform import dim
from holoviews.core.dimension import dimension_name


class WindBarbsPlot(ColorbarPlot):
    """
    Renders vector fields in sheet coordinates. The vectors are
    expressed in polar coordinates and may be displayed according to
    angle alone (with some common, arbitrary arrow length) or may be
    true polar vectors.

    The color or magnitude can be mapped onto any dimension using the
    color_index and size_index.

    The length of the arrows is controlled by the 'scale' style
    option. The scaling of the arrows may also be controlled via the
    normalize_lengths and rescale_lengths plot option, which will
    normalize the lengths to a maximum of 1 and scale them according
    to the minimum distance respectively.
    """

    rounding = param.Boolean(default=True, doc="""
        Whether the vector magnitude should be rounded when allocating
        barb components.""")

    barb_increments = param.Dict(default=None, doc="""
        A dictionary of increments specifying values to associate
        with different parts of the barb.""")

    flip_barb = param.Parameter(default=False, doc="""
        Whether the lines and flags should point opposite to normal.""")

    padding = param.ClassSelector(default=0.05, class_=(int, float, tuple))

    style_opts = [
        "alpha",
        "color",
        "edgecolors",
        "facecolors",
        "linewidth",
        "marker",
        "visible",
        "cmap",
        "length",
        "barbcolor",
        "flagcolor",
        "pivot",
        "width",
        "norm",
    ]

    _nonvectorized_styles = [
        "alpha",
        "marker",
        "cmap",
        "visible",
        "norm",
        "pivot",
    ]

    _plot_methods = dict(single="barbs")

    def get_data(self, element, ranges, style):
        # Compute coordinates
        xidx, yidx = (1, 0) if self.invert_axes else (0, 1)
        xs = element.dimension_values(xidx) if len(element.data) else []
        ys = element.dimension_values(yidx) if len(element.data) else []

        us = element.dimension_values(2)
        vs = element.dimension_values(3)
        args = (xs, ys, us, vs)

        # Process style
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
        barbs.angles = style["angles"]
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
