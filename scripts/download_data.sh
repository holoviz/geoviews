#!/usr/bin/env bash

bokeh sampledata

HERE=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
geoviews fetch-data --path="$HERE/../examples"

python -c "
try:
    import geodatasets as gds
    gds.get_path('geoda airbnb')
    gds.get_path('nybb')
except ImportError:
    pass
"
