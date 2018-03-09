import iris
import numpy as np
import xarray as xr
import holoviews as hv
import geoviews as gv
import geoviews.feature as gf
from cartopy import crs

"""
The following examples were taken from
http://geoviews.org/user_guide/Gridded_Datasets_I.html

This script is designed to be run by the python interpreter rather
than in a notebook.

Typical modifications when moving from notebook to script include:
    The need to create a renderer with a chosen backend.
    e.g. renderer = hv.renderer('matplotlib')

    plots are saved using render.save method.
    e.g. renderer.save(obj, 'my_filename')

    instead of ipython magics for controlling how elements look
    options are passed using the .opts() methods.
    below is an ipython cell magic format example
    %opts Image {+framewise} [colorbar=True] Curve [xrotation=60]

    when applying the above options globally you would do
    hv.opts("Image {+framewise} [colorbar=True] Curve [xrotation=60]")

    if you want to apply the options just to the object you would do
    obj.opts("Image {+framewise} [colorbar=True] Curve [xrotation=60]")

    Note that the .opts() method can also take a dictionary as an arg
    but for ease of use the string format is preferred.
"""

hv.extension('matplotlib', 'bokeh')
renderer = hv.renderer('matplotlib')

def set_globals():
    # Let's start by setting some normalization options
    # always enable colorbars for the elements we will be displaying:
    hv.opts('Image {+framewise} [colorbar=True] Curve [xrotation=60]')

    # specify the maximum number of frames we will display
    hv.output(max_frames=1000)

def load_data():
    """
    most of the examples load this dataset so lets turn it into
    a function
    """
    # load the dataset via xarray
    xr_ensemble = xr.open_dataset('./sample-data/ensemble.nc')

    # load the dataset via Iris
    iris.FUTURE.netcdf_promote=True
    iris_ensemble = iris.load_cube('./sample-data/ensemble.nc')

    # wrap the data in a GeoViews Dataset
    kdims = ['time', 'longitude', 'latitude']
    vdims = ['surface_temperature']
    xr_dataset = gv.Dataset(xr_ensemble, kdims=kdims, vdims=vdims, crs=crs.PlateCarree())
    iris_dataset = gv.Dataset(iris_ensemble, kdims=kdims, vdims=vdims)

    # improve the formatting of dates on the xarray dataset
    hv.Dimension.type_formatters[np.datetime64] = '%Y-%m-%d'
    return xr_dataset, iris_dataset

def simple_example1():
    """
    create a holomap using the xarray dataset
    """

    xr_dataset, iris_dataset = load_data()
    img_xr = xr_dataset.to(gv.Image, ['longitude', 'latitude'])
    renderer.save(img_xr, 'simple_example_1_xr')

def simple_example2():
    """
    create a holomap using the iris dataset
    """

    xr_dataset, iris_dataset = load_data()
    img_iris = iris_dataset.to(gv.Image, ['longitude', 'latitude'])
    renderer.save(img_iris, 'simple_example_2_iris')

def simple_example3():
    """
    Holomap combiend with single frame
    """

    xr_dataset, iris_dataset = load_data()
    air_temperature = gv.Dataset(xr.open_dataset('./sample-data/pre-industrial.nc'),
            kdims=['longitude', 'latitude'], group='Pre-industrial air temperature',
            vdims=['air_temperature'], crs=crs.PlateCarree())

    img = (xr_dataset.to.image(['longitude', 'latitude']) +
            air_temperature.to.image(['longitude', 'latitude']))
    renderer.save(img, 'simple_example_3')

def simple_example4():
    """
    Overlay point on holomap and combine with curve plot
    """

    xr_dataset, iris_dataset = load_data()
    opts_crv = "Curve [aspect=2 xticks=4 xrotation=15]"
    opts_pnt = " Points (color='k')"
    temp_curve = hv.Curve(xr_dataset.select(longitude=0, latitude=10),
            kdims=['time']).opts(opts_crv)

    temp_map = (xr_dataset.to(gv.Image,['longitude', 'latitude'])
            * gv.Points([(0,10)], crs=crs.PlateCarree()).opts(opts_pnt))

    img = temp_map + temp_curve
    renderer.save(img, 'simple_example_4')

def simple_example5():
    """
    Overlaying data with framewize normalization
    """

    xr_dataset, iris_dataset = load_data()
    opts_img = "Image (cmap='Greens')"
    opts_ov = "Overlay [xaxis=None yaxis=None]"
    img = (xr_dataset.to.image(['longitude', 'latitude']).opts(opts_img)
            * gf.coastline).opts(opts_ov)

    opts_proj = {'Image': {'plot':dict(projection=crs.Geostationary())}}
    renderer.save(img, 'simple_example_5', options=opts_proj)

def simple_example6():
    """
    Overlaying data with normalization set by redim
    use 300 and max_surface_temp for the normalization range
    """

    xr_dataset, iris_dataset = load_data()
    opts_img = "Image (cmap='Greens')"
    opts_ov = "Overlay [xaxis=None yaxis=None]"
    max_surface_temp = xr_dataset.range('surface_temperature')[1]
    print(max_surface_temp)
    ds_redim = xr_dataset.redim(surface_temperature=dict(range=(300, max_surface_temp)))
    img = (ds_redim.to(gv.Image,['longitude', 'latitude']).opts(opts_img)
            * gf.coastline)

    opts_proj = {'Image': {'plot':dict(projection=crs.Geostationary())}}
    renderer.save(img.opts(opts_ov), 'simple_example_6', options=opts_proj)

def simple_example7():
    """
    Filled Contours example
    """
    xr_dataset, iris_dataset = load_data()
    img = xr_dataset.to(gv.FilledContours,['longitude', 'latitude']) * gf.coastline
    renderer.save(img, 'simple_example_7')

if __name__ == '__main__':
    set_globals()
    simple_example1()
    simple_example2()
    simple_example3()
    simple_example4()
    simple_example5()
    simple_example6()
    simple_example7()

