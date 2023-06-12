import cartopy.crs as ccrs
import pytest

import geoviews as gv
from geoviews.util import from_xarray, process_crs

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
    with pytest.raises(
        ValueError, match="must be defined as a EPSG code, proj4 string"
    ):
        process_crs(43823)


@pytest.mark.skipif(rxr is None, reason="Needs rioxarray to be installed")
def test_from_xarray():
    file = (
        "https://github.com/holoviz/hvplot/raw/main/hvplot/tests/data/RGB-red.byte.tif"
    )
    output = from_xarray(rxr.open_rasterio(file))

    assert isinstance(output, gv.RGB)
    assert sorted(map(str, output.kdims)) == ["x", "y"]
    assert isinstance(output.crs, ccrs.CRS)
