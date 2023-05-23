#! /bin/sh
bokeh sampledata

geoviews fetch-data --path=examples

python -c "
try:
    import geodatasets as gds
    gds.get_path('geoda airbnb')
    gds.get_path('nybb')
except ImportError:
    pass
"
