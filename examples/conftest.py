import re
from importlib.metadata import version
from importlib.util import find_spec

_re_no = re.compile(r"\d+")


def get_version(package):
    version_str = version(package)
    return tuple(map(int, _re_no.findall(version_str)[:3]))


MPL_VERSION = get_version("matplotlib")
CARTOPY_VERSION = get_version("cartopy")

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

if MPL_VERSION >= (3, 11, 0) and CARTOPY_VERSION <= (0, 25, 0):
    # https://github.com/SciTools/cartopy/issues/2682
    collect_ignore_glob += [
        "gallery/matplotlib/tile_sources.ipynb",
        "gallery/matplotlib/wind_barbs_example.ipynb",
        "user_guide/Geometries.ipynb",
    ]


def pytest_runtest_makereport(item, call):
    """
    Skip tests that fail because "the kernel died before replying to kernel_info"
    this is a common error when running the example tests in CI.

    Inspired from: https://stackoverflow.com/questions/32451811

    """
    from _pytest.runner import pytest_runtest_makereport

    tr = pytest_runtest_makereport(item, call)

    if call.excinfo is not None:
        msgs = [
            "Kernel died before replying to kernel_info",
            "Kernel didn't respond in 60 seconds",
        ]
        for msg in msgs:
            if call.excinfo.type is RuntimeError and call.excinfo.value.args[0] in msg:
                tr.outcome = "skipped"
                tr.wasxfail = f"reason: {msg}"

    return tr
