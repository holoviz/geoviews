import geoviews as gv
import xarray as xr
from holoviews.operation import contours

def test_quadmesh_contoures_filled():
    # Regression test for: https://github.com/holoviz/holoviews/pull/5925
    ds = xr.tutorial.open_dataset("air_temperature").isel(time=0)
    p1 = gv.QuadMesh(ds, kdims=["lon", "lat"])
    p2 = contours(p1, filled=True)
    gv.renderer("bokeh").get_plot(p2)
