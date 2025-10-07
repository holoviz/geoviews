"""
Example demonstrating Bokeh-based WindBarbsPlot in GeoViews.

This example shows how to create wind barb plots using the Bokeh backend,
which renders wind barbs using a custom Bokeh glyph following meteorological
conventions.
"""
import numpy as np
import geoviews as gv

# Enable the bokeh extension
gv.extension('bokeh')

# Create sample wind data on a grid
x = np.linspace(-10, 10, 8)
y = np.linspace(-10, 10, 8)
X, Y = np.meshgrid(x, y)

# Create U and V wind components (m/s)
U = 10 * np.sin(X / 5) * np.cos(Y / 5)
V = 10 * np.cos(X / 5) * np.sin(Y / 5)

# Method 1: Create WindBarbs from U/V components
windbarbs_uv = gv.WindBarbs.from_uv((X, Y, U, V)).opts(
    title='Wind Barbs from U/V Components',
    width=600,
    height=400,
    scale=0.8,
    line_color='navy'
)

# Method 2: Create WindBarbs from angle and magnitude
angle = np.pi / 2 - np.arctan2(-V, -U)  # Meteorological convention
magnitude = np.hypot(U, V)

windbarbs_angle_mag = gv.WindBarbs((X, Y, angle, magnitude)).opts(
    title='Wind Barbs from Angle/Magnitude',
    width=600,
    height=400,
    scale=0.8,
    line_color='darkred'
)

# Method 3: Different scale
windbarbs_scale = gv.WindBarbs.from_uv((X, Y, U, V)).opts(
    title='Wind Barbs with Custom Scale',
    width=600,
    height=400,
    scale=1.5,
    line_color='green',
    line_width=2,
    tools=['hover']
)

# Display all three plots
layout = (windbarbs_uv + windbarbs_angle_mag + windbarbs_scale).cols(2)

if __name__ == '__main__':
    # Save or display the plot
    # gv.save(layout, 'windbarbs_bokeh_example.html')
    print("WindBarbs plots created successfully!")
    print("Use gv.render(layout) or layout in a Jupyter notebook to view the plots.")
