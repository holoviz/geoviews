#!/usr/bin/env bash

set -euxo pipefail

bokeh sampledata

HERE=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
geoviews fetch-data --path="$HERE/../examples"

python -c "
try:
    import geodatasets as gds
except ImportError:
    pass
else:
    gds.get_path('geoda airbnb')
    gds.get_path('nybb')
"

python -c "
try:
    import pooch
    import scipy
    import xarray as xr
except ImportError:
    pass
else:
    xr.tutorial.open_dataset('air_temperature')
"
