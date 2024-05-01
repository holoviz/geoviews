from pathlib import Path

import bokeh.sampledata

BASE_PATH = Path(__file__).resolve().parents[1]

bokeh.sampledata.download()

try:
    import pyct.cmd
except ImportError:
    pass
else:
    pyct.cmd.fetch_data(
        name="data",
        path=str(BASE_PATH / "examples"),
        datasets="datasets.yml",
    )

try:
    import geodatasets as gds
except ImportError:
    pass
else:
    gds.get_path("geoda airbnb")
    gds.get_path("nybb")

try:
    import pooch  # noqa: F401
    import scipy  # noqa: F401
    import xarray as xr
except ImportError:
    pass
else:
    xr.tutorial.open_dataset("air_temperature")
    xr.tutorial.open_dataset("rasm")
