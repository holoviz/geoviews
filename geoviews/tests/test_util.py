import pytest
import cartopy.crs as ccrs
from geoviews.util import process_crs


@pytest.mark.parametrize(
    "raw_crs",
    [
        "+init=epsg:26911",
        "4326",
        4326,
        "epsg:4326",
        "EPSG: 4326",
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
