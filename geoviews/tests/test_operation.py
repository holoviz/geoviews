import pytest
from holoviews.operation import contours

import geoviews as gv

xr = pytest.importorskip("xarray")


@pytest.mark.filterwarnings(
    "ignore:numpy.ndarray size changed, may indicate binary incompatibility"  # https://github.com/pydata/xarray/issues/7259
)
def test_quadmesh_contoures_filled():
    # Regression test for: https://github.com/holoviz/holoviews/pull/5925
    ds = xr.tutorial.open_dataset("air_temperature").isel(time=0)
    p1 = gv.QuadMesh(ds, kdims=["lon", "lat"])
    p2 = contours(p1, filled=True)
    gv.renderer("bokeh").get_plot(p2)


def test_unwrap_lons():
    pytest.importorskip("datashader")
    # Regression test for: https://github.com/holoviz/geoviews/pull/722
    from holoviews.operation.datashader import rasterize
    ds = xr.tutorial.open_dataset("air_temperature").isel(time=0)
    p1 = gv.Image(ds)
    p2 = rasterize(p1, filled=True)
    gv.renderer("bokeh").get_plot(p2)
    for x in p2.range(0):
        assert x >= 0
        assert x <= 360
    p2.callback()
    for x in p2.range(0):
        assert x >= 0
        assert x <= 360


def test_no_unwrap_lons():
    pytest.importorskip("datashader")
    # Regression test for: https://github.com/holoviz/geoviews/pull/722
    from holoviews.operation.datashader import rasterize
    ds = xr.tutorial.open_dataset("air_temperature").isel(time=0)
    # to -180, 180
    ds["lon"] = (ds["lon"] + 180) % 360 - 180

    p1 = gv.Image(ds)
    p2 = rasterize(p1, filled=True)
    gv.renderer("bokeh").get_plot(p2)
    for x in p2.range(0):
        assert x >= -180
        assert x <= 180
    p2.callback()
    for x in p2.range(0):
        assert x >= -180
        assert x <= 180
