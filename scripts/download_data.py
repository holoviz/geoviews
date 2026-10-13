import sys
import time
from contextlib import suppress
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import requests

BASE_PATH = Path(__file__).resolve().parents[1]


def retry(func, *args, **kwargs):
    for i in range(5):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            wait = 10 * 2**i
            print(f"Attempt {i + 1} failed: {e}. Retrying in {wait}s...", file=sys.stderr)
            time.sleep(wait)
    return func(*args, **kwargs)


def fetch_sample_data():
    data_path = BASE_PATH / "examples" / "data"
    if data_path.exists():
        return

    resp = requests.get("http://assets.holoviews.org/geoviews-sample-data.zip", timeout=30)
    resp.raise_for_status()
    with ZipFile(BytesIO(resp.content)) as zf:
        zf.extractall(data_path)


retry(fetch_sample_data)


with suppress(ImportError):
    import geodatasets as gds

    retry(gds.get_path, "geoda airbnb")
    retry(gds.get_path, "nybb")


with suppress(ImportError):
    import pooch  # noqa: F401
    import scipy  # noqa: F401
    import xarray as xr

    retry(xr.tutorial.open_dataset, "air_temperature")
    retry(xr.tutorial.open_dataset, "rasm", decode_times=False)

with suppress(ImportError):
    from cartopy.feature import shapereader

    retry(shapereader.natural_earth, name="coastline")
    retry(shapereader.natural_earth, name="land")
    retry(shapereader.natural_earth, name="ocean")
    retry(
        shapereader.natural_earth,
        category="cultural",
        name="admin_0_boundary_lines_land",
    )
