import cartopy.crs as ccrs
import numpy as np
import pytest

import geoviews as gv
from geoviews.util import central_longitude, process_crs, project_extents

try:
    import rioxarray as rxr
except ImportError:
    rxr = None


@pytest.mark.parametrize(
    "raw_crs",
    [
        "+init=epsg:26911",
        "4326",
        4326,
        "epsg:4326",
        "EPSG: 4326",
        ccrs.PlateCarree(),
    ],
)
def test_process_crs(raw_crs) -> None:
    crs = process_crs(raw_crs)
    assert isinstance(crs, ccrs.CRS)


# To avoid '+init=<authority>:<code>' syntax is deprecated.
@pytest.mark.filterwarnings("ignore::FutureWarning")
def test_process_crs_raises_error():
    with pytest.raises(ValueError, match="must be defined as a EPSG code, proj4 string"):
        process_crs(43823)


class FakeProjection:
    """Stands in for a cartopy CRS so both proj4 layouts stay covered on either version."""

    def __init__(self, proj4_params):
        self.proj4_params = proj4_params


@pytest.mark.parametrize(
    ("proj4_params", "expected"),
    [
        # cartopy >= 0.26 PlateCarree: proj=latlong, prime meridian, no lon_0
        ({"proj": "latlong", "pm": 0.0}, 0.0),
        ({"proj": "latlong", "pm": 30}, 30),
        # cartopy < 0.26 PlateCarree, and projections that still use lon_0
        ({"proj": "eqc", "lon_0": 0.0}, 0.0),
        ({"proj": "robin", "lon_0": 45}, 45),
        # neither key present
        ({"proj": "geos"}, 0),
    ],
)
def test_central_longitude(proj4_params, expected):
    assert central_longitude(FakeProjection(proj4_params)) == expected


def test_project_extents_offset_platecarree():
    """Cartopy 0.26 drops lon_0 from PlateCarree, which used to raise KeyError here."""
    extents = (-10, -10, 10, 10)
    projected = project_extents(extents, ccrs.PlateCarree(central_longitude=30), ccrs.Robinson())

    assert len(projected) == 4
    assert all(np.isfinite(projected))


@pytest.mark.skipif(rxr is None, reason="Needs rioxarray to be installed")
def test_from_xarray():
    file = "https://github.com/holoviz/hvplot/raw/main/hvplot/tests/data/RGB-red.byte.tif"
    output = gv.from_xarray(rxr.open_rasterio(file))

    assert isinstance(output, gv.RGB)
    assert sorted(map(str, output.kdims)) == ["x", "y"]
    assert isinstance(output.crs, ccrs.CRS)
