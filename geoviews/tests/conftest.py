import contextlib


with contextlib.suppress(ImportError):
    import matplotlib.pyplot as plt

    plt.switch_backend("agg")

with contextlib.suppress(Exception):
    # From Dask 2024.3.0 they now use `dask_expr` by default
    # https://github.com/dask/dask/issues/10995
    import dask

    dask.config.set({"dataframe.query-planning": False})
