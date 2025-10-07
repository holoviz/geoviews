# Bokeh WindBarbsPlot Implementation

## Overview

This PR implements a Bokeh-based WindBarbsPlot for GeoViews, providing feature parity with the existing Matplotlib implementation. Wind barbs are commonly used in meteorology to visualize wind speed and direction data.

## Components Implemented

### 1. Custom Bokeh Glyph (`geoviews/models/wind_barb.py` and `wind_barb.ts`)

A custom `WindBarb` glyph that renders wind barbs following meteorological conventions:
- **Python Model**: Extends `XYGlyph` with additional properties for angle, magnitude, and scale
- **TypeScript Rendering**: Implements the visual rendering logic with:
  - 50-knot flags (filled triangles)
  - 10-knot full barbs
  - 5-knot half barbs
  - Calm wind circles (< 5 knots)
  - Proper rotation using meteorological convention (direction FROM which wind blows)

**Properties:**
- `x`, `y`: Coordinates for wind barb positions
- `angle`: Wind direction in radians (meteorological convention)
- `magnitude`: Wind speed magnitude
- `scale`: Scaling factor for barb size (default: 1.0)
- Line properties: `line_color`, `line_alpha`, `line_width`

### 2. WindBarbsPlot Class (`geoviews/plotting/bokeh/chart.py`)

Bokeh plotting class that matches the API of the Matplotlib version:
- Converts between angle/magnitude and U/V components
- Supports `convention` parameter ("from" or "to")
- Handles coordinate transformations and projections
- Properly separates glyph properties from renderer properties

**Parameters:**
- `convention`: "from" (meteorological - default) or "to" (oceanographic)
- `scale`: Size scaling factor for wind barbs
- `invert_axes`: Swap x/y axes if needed

### 3. GeoWindBarbsPlot Wrapper (`geoviews/plotting/bokeh/__init__.py`)

Geographic plotting wrapper that adds projection support via `project_windbarbs` operation.

### 4. Tests (`geoviews/tests/plotting/bokeh/test_windbarbs.py`)

Comprehensive test suite covering:
- Basic wind barbs rendering
- Creation from U/V components using `from_uv()`
- Custom scale parameter
- Convention parameter ("from" vs "to")

## Usage Examples

### Basic Usage

```python
import numpy as np
import geoviews as gv

gv.extension('bokeh')

# Create sample wind data
x = np.linspace(-10, 10, 8)
y = np.linspace(-10, 10, 8)
X, Y = np.meshgrid(x, y)
U = 10 * np.sin(X / 5) * np.cos(Y / 5)
V = 10 * np.cos(X / 5) * np.sin(Y / 5)

# Method 1: From U/V components
windbarbs = gv.WindBarbs.from_uv((X, Y, U, V))

# Method 2: From angle and magnitude
angle = np.pi / 2 - np.arctan2(-V, -U)
magnitude = np.hypot(U, V)
windbarbs = gv.WindBarbs((X, Y, angle, magnitude))

# Display with custom styling
windbarbs.opts(
    scale=0.8,
    line_color='navy',
    line_width=2,
    width=600,
    height=400,
    tools=['hover']
)
```

### With Geographic Projection

```python
import geoviews as gv
import geoviews.feature as gf
import cartopy.crs as ccrs

# Create wind barbs with geographic coordinates
windbarbs = gv.WindBarbs.from_uv(
    data,
    kdims=['longitude', 'latitude'],
    vdims=['u', 'v'],
    crs=ccrs.PlateCarree()
)

# Overlay on map
(gf.coastline * windbarbs).opts(
    projection=ccrs.Orthographic(),
    global_extent=True,
    width=800,
    height=600
)
```

## Implementation Details

### Meteorological Convention

The wind barbs follow standard meteorological conventions:
- Direction indicates where the wind is coming FROM
- North is 0°, East is 90°, etc.
- Barbs point in the direction the wind is blowing TO
- Speed increments:
  - Triangle (flag): 50 knots
  - Full barb: 10 knots
  - Half barb: 5 knots
  - Circle: Calm (< 5 knots)

### TypeScript Rendering

The custom glyph's TypeScript implementation handles:
- Canvas-based rendering with proper rotation
- Hit testing for hover interactions
- Legend rendering
- Visual styling through LineVector mixin

### Build Process

The custom glyph requires building with `bokeh.ext`:
```bash
python -c "from bokeh.ext import build; build('geoviews')"
```

This generates `geoviews/dist/geoviews.js` with the custom glyph code.

## Testing

All tests pass:
- 4 new Bokeh WindBarbsPlot tests
- 7 existing Matplotlib WindBarbsPlot tests (unchanged)

Run tests with:
```bash
pytest geoviews/tests/plotting/bokeh/test_windbarbs.py -v
pytest geoviews/tests/plotting/mpl/test_chart.py::TestWindBarbsPlot -v
```

## Files Changed

### New Files
- `geoviews/models/wind_barb.py` - Python glyph model
- `geoviews/models/wind_barb.ts` - TypeScript rendering implementation
- `geoviews/plotting/bokeh/chart.py` - WindBarbsPlot class
- `geoviews/tests/plotting/bokeh/test_windbarbs.py` - Test suite
- `examples/user_guide/windbarbs_bokeh_example.py` - Usage example

### Modified Files
- `geoviews/models/__init__.py` - Export WindBarb model
- `geoviews/models/index.ts` - Export WindBarb TypeScript class
- `geoviews/plotting/bokeh/__init__.py` - Register GeoWindBarbsPlot

## Compatibility

- **Bokeh**: Requires bokeh >=3.6.0 (as per project dependencies)
- **HoloViews**: Compatible with holoviews >=1.16.0
- **Backward Compatible**: Existing Matplotlib WindBarbsPlot unchanged

## Future Enhancements

Potential improvements for future PRs:
- Colorbar support for magnitude-based coloring
- Additional barb styles (Southern Hemisphere convention)
- Performance optimization for large datasets
- Interactive barb editing tools
