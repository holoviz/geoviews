"""WindBarb glyph for rendering wind barbs in Bokeh."""
from bokeh.core.properties import AngleSpec, Float, NumberSpec, field
from bokeh.models import XYGlyph


class WindBarb(XYGlyph):
    """
    A glyph for rendering wind barbs at (x, y) locations.
    
    Wind barbs are traditionally used in meteorology to plot wind speed
    and direction. The barb consists of a staff with flags and barbs
    representing wind speed increments.
    """
    
    # Explicit args
    _args = ('x', 'y', 'angle', 'magnitude')
    
    # The x-coordinates
    x = NumberSpec(default=field("x"), help="""
        The x-coordinates of the wind barbs.
        """)
    
    # The y-coordinates
    y = NumberSpec(default=field("y"), help="""
        The y-coordinates of the wind barbs.
        """)
    
    # The angle in radians (meteorological convention: direction FROM which wind blows)
    angle = AngleSpec(default=field("angle"), help="""
        The angles to rotate the wind barbs, in radians.
        """)
    
    # The magnitude (wind speed)
    magnitude = NumberSpec(default=field("magnitude"), help="""
        The magnitudes (wind speeds) for the wind barbs.
        """)
    
    # Scale factor for the barb size
    scale = Float(default=1.0, help="""
        A scaling factor to apply to the wind barb size.
        """)
