from contextlib import suppress

import geoviews as gv

with suppress(Exception):
    gv.extension("bokeh")

with suppress(Exception):
    gv.extension("matplotlib")

with suppress(ImportError):
    import matplotlib.pyplot as plt

    plt.switch_backend("agg")

with suppress(Exception):
    # From Dask 2024.3.0 they now use `dask_expr` by default
    # https://github.com/dask/dask/issues/10995
    import dask

    dask.config.set({"dataframe.query-planning": False})
