#!/usr/bin/env bash

set -euxo pipefail

python -m bokeh sampledata

HERE=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python -m geoviews fetch-data --path="$HERE/../examples" || echo "geoviews fetch-data failed"

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
    xr.tutorial.open_dataset('rasm')
"
