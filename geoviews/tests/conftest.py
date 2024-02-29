from contextlib import suppress

import geoviews as gv

with suppress(Exception):
    gv.extension("bokeh")

with suppress(Exception):
    gv.extension("matplotlib")
