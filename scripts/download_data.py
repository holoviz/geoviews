from contextlib import suppress
from pathlib import Path

import bokeh.sampledata

BASE_PATH = Path(__file__).resolve().parents[1]

bokeh.sampledata.download()

with suppress(ImportError):
    import pyct.cmd

    pyct.cmd.fetch_data(
        name="data",
        path=str(BASE_PATH / "examples"),
        datasets="datasets.yml",
    )


with suppress(ImportError):
    import geodatasets as gds

    gds.get_path("geoda airbnb")
    gds.get_path("nybb")


with suppress(ImportError):
    import pooch  # noqa: F401
    import scipy  # noqa: F401
    import xarray as xr

    xr.tutorial.open_dataset("air_temperature")
    xr.tutorial.open_dataset("rasm")
