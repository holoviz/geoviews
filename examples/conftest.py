from importlib.util import find_spec

# depend on optional iris, xesmf, etc
collect_ignore_glob = [
    "Homepage.ipynb",
    "user_guide/Resampling_Grids.ipynb",
    "user_guide/Gridded_Datasets_*.ipynb",
    "gallery/bokeh/xarray_gridded.ipynb",
    "gallery/*/xarray_image.ipynb",
    "gallery/*/xarray_quadmesh.ipynb",
    "gallery/*/katrina_track.ipynb",
]


# Needed for gpd.read_file
if find_spec("fiona") is None:
    collect_ignore_glob += [
        "gallery/bokeh/brexit_choropleth.ipynb",
        "gallery/bokeh/new_york_boroughs.ipynb",
        "gallery/matplotlib/brexit_choropleth.ipynb",
        "gallery/matplotlib/new_york_boroughs.ipynb",
        "user_guide/Geometries.ipynb",
        "user_guide/Working_with_Bokeh.ipynb",
    ]
