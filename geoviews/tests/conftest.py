from contextlib import suppress

import geoviews as gv

CUSTOM_MARKS = ("ui",)


def pytest_addoption(parser):
    for marker in CUSTOM_MARKS:
        parser.addoption(
            f"--{marker}",
            action="store_true",
            default=False,
            help=f"Run {marker} related tests",
        )


def pytest_configure(config):
    for marker in CUSTOM_MARKS:
        config.addinivalue_line("markers", f"{marker}: {marker} test marker")


def pytest_collection_modifyitems(config, items):
    skipped, selected = [], []
    markers = [m for m in CUSTOM_MARKS if config.getoption(f"--{m}")]
    empty = not markers
    for item in items:
        if empty and any(m in item.keywords for m in CUSTOM_MARKS):
            skipped.append(item)
        elif empty:
            selected.append(item)
        elif not empty and any(m in item.keywords for m in markers):
            selected.append(item)
        else:
            skipped.append(item)

    config.hook.pytest_deselected(items=skipped)
    items[:] = selected


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
