# Using WMTS Offline

## Caching the Tiles

Web map tile services simply provide tiled images for a given target domain request. So to use them offline, you simply need to copy these images from their server to a preferred local mirror and point to that local mirror.

However, attempting to determine the corresponding tiles to specific target domains can be a daunting task--thankfully, Cartopy provides utilities that can assist you with this task.

When Cartopy is invoked for a given target domain, it retrieves and stores the relevant map tiles in a NumPy, binary file format `.npy`.

```python
from pathlib import Path

import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import numpy as np
from PIL import Image
from shapely import box


def cache_tiles(
    tile_source,
    max_target_z=1,
    x_bounds=(-180, 180),
    y_bounds=(-90, 90),
    cache_dir="tiles",
):
    """
    Caches map tiles within specified bounds from a given tile source.

    Args:
        tile_source (str or cartopy.io.img_tiles.Tiles): The tile source to use for caching.
            It can be a string specifying a built-in tile source, or an instance of a custom tile source class.
        max_target_z (int, optional): The maximum zoom level to cache. Defaults to 1.
        x_bounds (tuple, optional): The longitudinal bounds of the tiles to cache. Defaults to (-180, 180).
        y_bounds (tuple, optional): The latitudinal bounds of the tiles to cache. Defaults to (-90, 90).
        cache_dir (str, optional): The directory to store the cached tiles. Defaults to "tiles".

    Returns:
        pathlib.Path: The path to the cache directory.
    """
    if not isinstance(tile_source, cimgt.GoogleWTS):
        tile_source = getattr(cimgt, tile_source)
    tiles = tile_source(cache=cache_dir)

    bbox = ccrs.GOOGLE_MERCATOR.transform_points(
        ccrs.PlateCarree(), x=np.array(x_bounds), y=np.array(y_bounds)
    )[:, :-1].flatten()  # drop Z, then convert to x0, y0, x1, y1
    target_domain = box(*bbox)

    for target_z in range(max_target_z):
        tiles.image_for_domain(target_domain, target_z)
    return Path(cache_dir) / tile_source.__name__
```

As an example, to cache OpenStreetMaps tiles, you can simply call the provided function, ensuring that you specify a maximum zoom level (`max_target_z`).

```python
cache_dir = cache_tiles("OSM", max_target_z=6)
```

WARNING: When working with higher zoom levels, it is **highly recommended** to specify the `x_bounds` and `y_bounds` parameters to your region of interest. This is crucial to prevent potential issues such as rate limiting or, in extreme cases, *being banned*.

As the zoom level increases, the time required for downloading and caching the tiles grows exponentially due to the increasing number of fine-grained tiles that need to be retrieved. By setting appropriate boundaries, you can effectively manage the download process and mitigate the risk of encountering problems related to excessive requests.

Here is a table illustrating the number of tiles for *global extents* at different zoom levels:

```
z=0: 1 tile (entire world)
z=1: 4 tiles
z=2: 16 tiles
z=3: 64 tiles
z=4: 256 tiles
z=5: 1,024 tiles
z=6: 4,096 tiles
z=7: 16,384 tiles
z=8: 65,536 tiles
z=9: 262,144 tiles
z=10: 1,048,576 tiles
z=11: 4,194,304 tiles
z=12: 16,777,216 tiles
z=13: 67,108,864 tiles
z=14: 268,435,456 tiles
z=15: 1,073,741,824 tiles
z=16: 4,294,967,296 tiles
z=17: 17,179,869,184 tiles
z=18: 68,719,476,736 tiles
z=19: 274,877,906,944 tiles
z=20: 1,099,511,627,776 tiles
```

## Converting to PNG

Since GeoViews lacks support for reading cached NumPy binary files, an additional step is required to:

1. convert them to PNG format
2. update their directories
3. build a format string containing "{X}/{Y}/{Z}" (or similar variations)

Fortunately, this process only involves a straightforward loop that performs minimal processing on each file.

```python
def convert_tiles_cache(cache_dir):
    """
    Converts cached tiles from numpy format to PNG format.

    Args:
        cache_dir (str): The directory containing the cached tiles in numpy format.

    Returns:
        str: The format string representing the converted PNG tiles.
    """
    for np_path in Path(cache_dir).rglob("*.npy"):
        img = Image.fromarray(np.load(np_path))
        img_path = Path(str(np_path.with_suffix(".png")).replace("_", "/"))
        img_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(img_path)

    tiles_fmt = str(cache_dir / "{X}" / "{Y}" / "{Z}.png")
    return tiles_fmt
```

```python
tiles_fmt = convert_tiles_cache(cache_dir)
```

## Testing Locally

Now, all that's left is passing that generated tiles format string into `gv.WMTS`.

```python
import geoviews as gv

gv.extension("bokeh")

gv.WMTS(tiles_dir).opts(global_extent=True)
```

Please keep in mind that when reaching higher zoom levels beyond the cached max_target_z, you might encounter a blank map.

To avoid this issue, it is essential to set the `max_zoom` option to the same value as `max_target_z`.

```python
import geoviews as gv

gv.extension("bokeh")

gv.WMTS(tiles_dir).opts(global_extent=True, max_zoom=6)
```
