import cartopy.crs as ccrs
import holoviews as hv
import numpy as np
import pytest
from holoviews.tests.ui import expect, wait_until

import geoviews as gv

pytestmark = pytest.mark.ui

xr = pytest.importorskip("xarray")


@pytest.mark.usefixtures("bokeh_backend")
def test_range_correct_longitude(serve_hv):
    """
    Regression test for https://github.com/holoviz/geoviews/issues/753
    """
    coastline = gv.feature.coastline().opts(active_tools=["box_zoom"])
    xy_range = hv.streams.RangeXY(source=coastline)

    page = serve_hv(coastline)
    hv_plot = page.locator(".bk-events")

    expect(hv_plot).to_have_count(1)

    bbox = hv_plot.bounding_box()
    hv_plot.click()

    page.mouse.move(bbox["x"] + 100, bbox["y"] + 100)
    page.mouse.down()
    page.mouse.move(bbox["x"] + 150, bbox["y"] + 150, steps=5)
    page.mouse.up()

    wait_until(lambda: np.isclose(xy_range.x_range[0], -105.68691588784145), page)
    wait_until(lambda: np.isclose(xy_range.x_range[1], -21.80841121496224), page)


@pytest.mark.usefixtures("bokeh_backend")
@pytest.mark.parametrize("lon_start,lon_end", [(-180, 180), (0, 360)])
@pytest.mark.parametrize("bbox_x", [100, 250])
def test_rasterize_with_coastline_not_blank_on_zoom(serve_hv, lon_start, lon_end, bbox_x):
    """
    Regression test for https://github.com/holoviz/geoviews/issues/726
    """
    from holoviews.operation.datashader import rasterize

    lon = np.linspace(lon_start, lon_end, 360)
    lat = np.linspace(-90, 90, 180)
    data = np.random.rand(180, 360)
    ds = xr.Dataset({"data": (["lat", "lon"], data)}, coords={"lon": lon, "lat": lat})

    overlay = rasterize(
        gv.Image(ds, ["lon", "lat"], ["data"], crs=ccrs.PlateCarree()).opts(
            tools=["hover"], active_tools=["box_zoom"]
        )
    ) * gv.feature.coastline()

    page = serve_hv(overlay)

    hv_plot = page.locator(".bk-events")

    expect(hv_plot).to_have_count(1)

    bbox = hv_plot.bounding_box()
    hv_plot.click()

    page.mouse.move(bbox["x"] + bbox_x, bbox["y"] + 100)
    page.mouse.down()
    page.mouse.move(bbox["x"] + bbox_x + 50, bbox["y"] + 150, steps=5)
    page.mouse.up()

    # get hover tooltip
    page.mouse.move(bbox["x"] + 100, bbox["y"] + 150)

    wait_until(lambda: expect(page.locator(".bk-Tooltip")).to_have_count(1), page=page)

    expect(page.locator(".bk-Tooltip")).to_contain_text("lon:")
    expect(page.locator(".bk-Tooltip")).to_contain_text("lat:")
    expect(page.locator(".bk-Tooltip")).to_contain_text("data:")
    expect(page.locator(".bk-Tooltip")).not_to_contain_text("?")
