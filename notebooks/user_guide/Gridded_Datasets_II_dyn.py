import numpy as np
import xarray as xr
import holoviews as hv
import geoviews as gv
import geoviews.feature as gf
from cartopy import crs as ccrs
from bokeh.plotting import curdoc, save, output_file

"""
The following examples were taken from
http://geoviews.org/user_guide/Gridded_Datasets_II.html

This script is designed to be run used with the bokeh server.

To run it you can do the following
bokeh serve --allow-websocket-origin localhost:5006  Gridded_Datasets_II_dyn.py'
then in a browser connect to localhost:5006/Gridded_Datasets_II_dyn

Make sure port 5006 is open in your firewall

For sample non-dynamic script that has all the plots in the docs see 
Gridded_Datasets_II.py
"""

def dynamic_example():
    """
    requires a bokeh serve command to work correctly

    If you want to have the dynamic feature work use the following

    bokeh serve --allow-websocket-origin localhost:5006  Gridded_Datasets_II_dyn.py'

    then in browser address bar enter

    localhost:5006/Gridded_Datasets_II_dyn

    see bokeh docs or system admin if you cannot get this to work
    """
    hv.extension('bokeh', 'matplotlib')
    renderer = hv.renderer('bokeh')
    hv.output('size=200')

    xr_ensembles = xr.open_dataset('./sample-data/ensembles.nc')
    dataset = gv.Dataset(xr_ensembles, vdims='surface_temperature', crs=ccrs.PlateCarree())

    hv.Dimension.type_formatters[np.datetime64] = '%Y-%m-%d'

    geo_dims = ['longitude', 'latitude']
    img = (dataset.to(gv.Image, geo_dims, dynamic=True) * gf.coastline)

    # to get the dynamic feature to work must create a bokeh doc
    # and run the script through a bokeh serve
    doc = renderer.server_doc(img)
    return doc

def irregularly_sampled_data():
    """
    If you get an issue with dates in the dataset, delete the file in
    ~/.xarray_tutorial_data/
    from projection we can tell docs use matplotlib backend.
    however, to get dynamic=True outside of notebook we will need to use
    the bokeh serve which means we need bokeh backend.
    """

    hv.extension('bokeh')
    renderer = hv.renderer('bokeh')

    # cannot use projections in the img.opts() like in notebook notebook
    opts = "QuadMesh [colorbar=True fig_size=300] (cmap='RdBu_r')"
    xrds = xr.tutorial.load_dataset('rasm')

    qmesh = gv.Dataset(xrds.Tair).to(gv.QuadMesh, ['xc', 'yc'], dynamic=True)
    print('loaded')
    qmesh.redim.range(Tair=(-30, 30)) * gf.coastline

    # apply the opts, and do the projection
    img = qmesh.opts(opts)(plot=dict(projection=ccrs.Robinson())) * gf.coastline

    # instead of renderer.save use renderer.server_doc so we can display
    # using a bokeh server
    doc = renderer.server_doc(img)
    return doc

def temp_over_time():
    """
    Non-geographic views, dynamic example
    """

    hv.extension('bokeh', 'matplotlib')
    renderer = hv.renderer('bokeh')
    #hv.output('size=200')

    xr_ensembles = xr.open_dataset('./sample-data/ensembles.nc')
    dataset = gv.Dataset(xr_ensembles, vdims='surface_temperature', crs=ccrs.PlateCarree())

    hv.Dimension.type_formatters[np.datetime64] = '%Y-%m-%d'

    opts = "Curve [xrotation=25 width=400 height=200] {+framewise} NdOverlay [legend_position='right' toolbar='above']"
    # apply options globally
    hv.opts(opts)

    opts_crv = "Curve [xrotation=25 width=400 height=200] {+framewise}"
    opts_nd = " NdOverlay [legend_position='right' toolbar='above']"
    img = dataset.to(hv.Curve, 'time', dynamic=True).opts(opts_crv).overlay('realization').opts(opts_nd)

    # instead of renderer.save use renderer.server_doc so we can display
    # using a bokeh server
    doc = renderer.server_doc(img)
    return doc

def heatmap():
    """
    requires a bokeh serve command to work correctly

    If you want to have the dynamic feature work use the following

    bokeh serve --allow-websocket-origin localhost:5006  Gridded_Datasets_II_dyn.py'

    then in browser address bar enter

    localhost:5006/Gridded_Datasets_II_dyn

    see bokeh docs or system admin if you cannot get this to work
    """

    hv.extension('bokeh', 'matplotlib')
    renderer = hv.renderer('bokeh')
    #hv.output('size=200')

    xr_ensembles = xr.open_dataset('./sample-data/ensembles.nc')
    dataset = gv.Dataset(xr_ensembles, vdims='surface_temperature', crs=ccrs.PlateCarree())

    hv.Dimension.type_formatters[np.datetime64] = '%Y-%m-%d'

    opts = "HeatMap [width=400 colorbar=True tools=['hover'] toolbar='above']"
    # apply options globally
    hv.opts(opts)
    img = dataset.to(hv.HeatMap, ['realization', 'time'], dynamic=True)

    # instead of renderer.save use renderer.server_doc so we can display
    # using a bokeh server
    doc = renderer.server_doc(img)
    return doc


doc1 = dynamic_example()
doc2 = irregularly_sampled_data()
doc2 = temp_over_time()
doc3 = heatmap()

