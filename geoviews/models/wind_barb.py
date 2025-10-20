"""WindBarb glyph for rendering wind barbs in Bokeh."""

from bokeh.core.properties import AngleSpec, Float, Include, NumberSpec, field
from bokeh.core.property_mixins import LineProps
from bokeh.models import XYGlyph


class WindBarb(XYGlyph):
    """
    A glyph for rendering wind barbs at (x, y) locations.

    Wind barbs are traditionally used in meteorology to plot wind speed
    and direction. The barb consists of a staff with flags and barbs
    representing wind speed increments.
    """

    # Explicit args
    _args = ("x", "y", "angle", "magnitude")

    # The x-coordinates
    x = NumberSpec(
        default=field("x"),
        help="""
        The x-coordinates of the wind barbs.
        """,
    )

    # The y-coordinates
    y = NumberSpec(
        default=field("y"),
        help="""
        The y-coordinates of the wind barbs.
        """,
    )

    # The angle in radians (meteorological convention: direction FROM which wind blows)
    angle = AngleSpec(
        default=field("angle"),
        help="""
        The angles to rotate the wind barbs, in radians.
        """,
    )

    # The magnitude (wind speed)
    magnitude = NumberSpec(
        default=field("magnitude"),
        help="""
        The magnitudes (wind speeds) for the wind barbs.
        """,
    )

    # Scale factor for the barb size
    scale = Float(
        default=1.0,
        help="""
        A scaling factor to apply to the wind barb size.
        """,
    )

    # Barb dimensions
    barb_length = Float(
        default=30.0,
        help="""
        Length of the main barb staff.
        """,
    )

    barb_width = Float(
        default=15.0,
        help="""
        Width of the barb lines.
        """,
    )

    flag_width = Float(
        default=15.0,
        help="""
        Width of the 50-knot flag triangles.
        """,
    )

    spacing = Float(
        default=6.0,
        help="""
        Vertical spacing between barbs and flags.
        """,
    )

    calm_circle_radius = Float(
        default=3.0,
        help="""
        Radius of the circle drawn for calm winds (< 5 knots).
        """,
    )

    # Line properties
    line_props = Include(
        LineProps,
        help="""
        The {prop} values for the wind barbs.
        """,
    )
