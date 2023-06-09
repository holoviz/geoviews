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

    arrow_heads = param.Boolean(
        default=True,
        doc="""
       Whether or not to draw arrow heads. If arrowheads are enabled,
       they may be customized with the 'headlength' and
       'headaxislength' style options.""",
    )

    magnitude = param.ClassSelector(
        class_=(str, dim),
        doc="""
        Dimension or dimension value transform that declares the magnitude
        of each vector. Magnitude is expected to be scaled between 0-1,
        by default the magnitudes are rescaled relative to the minimum
        distance between vectors, this can be disabled with the
        rescale_lengths option.""",
    )

    padding = param.ClassSelector(default=0.05, class_=(int, float, tuple))

    rescale_lengths = param.Boolean(
        default=True,
        doc="""
       Whether the lengths will be rescaled to take into account the
       smallest non-zero distance between two vectors.""",
    )

    # Deprecated parameters

    color_index = param.ClassSelector(
        default=None,
        class_=(str, int),
        allow_None=True,
        doc="""
        Deprecated in favor of dimension value transform on color option,
        e.g. `color=dim('Magnitude')`.
        """,
    )

    size_index = param.ClassSelector(
        default=None,
        class_=(str, int),
        allow_None=True,
        doc="""
        Deprecated in favor of the magnitude option, e.g.
        `magnitude=dim('Magnitude')`.
        """,
    )

    normalize_lengths = param.Boolean(
        default=True,
        doc="""
        Deprecated in favor of rescaling length using dimension value
        transforms using the magnitude option, e.g.
        `dim('Magnitude').norm()`.""",
    )

    style_opts = [
        "alpha",
        "color",
        "edgecolors",
        "facecolors",
        "linewidth",
        "marker",
        "visible",
        "cmap",
        "scale",
        "headlength",
        "headaxislength",
        "pivot",
        "width",
        "headwidth",
        "norm",
    ]

    _nonvectorized_styles = [
        "alpha",
        "marker",
        "cmap",
        "visible",
        "norm",
        "pivot",
        "headlength",
        "headaxislength",
        "headwidth",
    ]

    _plot_methods = dict(single="quiver")

    def _get_magnitudes(self, element, style, ranges):
        size_dim = element.get_dimension(self.size_index)
        mag_dim = self.magnitude
        if size_dim and mag_dim:
            self.param.warning(
                "Cannot declare style mapping for 'magnitude' option "
                "and declare a size_index; ignoring the size_index."
            )
        elif size_dim:
            mag_dim = size_dim
        elif isinstance(mag_dim, str):
            mag_dim = element.get_dimension(mag_dim)
        if mag_dim is not None:
            if isinstance(mag_dim, dim):
                magnitudes = mag_dim.apply(element, flat=True)
            else:
                magnitudes = element.dimension_values(mag_dim)
                _, max_magnitude = ranges[dimension_name(mag_dim)]["combined"]
                if self.normalize_lengths and max_magnitude != 0:
                    magnitudes = magnitudes / max_magnitude
        else:
            magnitudes = np.ones(len(element))
        return magnitudes

    def get_data(self, element, ranges, style):
        # Compute coordinates
        xidx, yidx = (1, 0) if self.invert_axes else (0, 1)
        xs = element.dimension_values(xidx) if len(element.data) else []
        ys = element.dimension_values(yidx) if len(element.data) else []

        # Compute vector angle and magnitude
        radians = element.dimension_values(2) if len(element.data) else []
        if self.invert_axes:
            radians = radians + 1.5 * np.pi
        angles = list(np.rad2deg(radians))
        magnitudes = self._get_magnitudes(element, style, ranges)
        input_scale = style.pop("scale", 1.0)

        args = (xs, ys, magnitudes, [0.0] * len(element))

        # Compute color
        cdim = element.get_dimension(self.color_index)
        color = style.get("color", None)
        if cdim and (
            (isinstance(color, str) and color in element) or isinstance(color, dim)
        ):
            self.param.warning(
                "Cannot declare style mapping for 'color' option and "
                "declare a color_index; ignoring the color_index."
            )
            cdim = None
        if cdim:
            colors = element.dimension_values(self.color_index)
            style["c"] = colors
            cdim = element.get_dimension(self.color_index)
            self._norm_kwargs(element, ranges, style, cdim)
            style.pop("color", None)

        # Process style
        style.update(dict(scale=input_scale, angles=angles, units="x", scale_units="x"))
        if "vmin" in style:
            style["clim"] = (style.pop("vmin"), style.pop("vmax"))
        if "c" in style:
            style["array"] = style.pop("c")
        if "pivot" not in style:
            style["pivot"] = "mid"
        if not self.arrow_heads:
            style["headaxislength"] = 0

        return args, style, {}

    def update_handles(self, key, axis, element, ranges, style):
        args, style, axis_kwargs = self.get_data(element, ranges, style)

        # Set magnitudes, angles and colors if supplied.
        quiver = self.handles["artist"]
        quiver.set_offsets(np.column_stack(args[:2]))
        quiver.U = args[2]
        quiver.angles = style["angles"]
        if "color" in style:
            quiver.set_facecolors(style["color"])
            quiver.set_edgecolors(style["color"])
        if "array" in style:
            quiver.set_array(style["array"])
        if "clim" in style:
            quiver.set_clim(style["clim"])
        if "linewidth" in style:
            quiver.set_linewidths(style["linewidth"])
        return axis_kwargs
