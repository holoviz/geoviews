import numpy as np
import xarray as xr
import holoviews as hv
import geoviews as gv
import geoviews.feature as gf
from cartopy import crs as ccrs

"""
The following examples were taken from
http://geoviews.org/user_guide/Gridded_Datasets_II.html

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

    Here dynamic examples have been included, but the plots will be static
    like in the docs.

    If you want an example script that you can serve using a boker server
    See Gridded_Datasets_II_dyn.py
"""

def realization_plot():
    """
    Multi-dimensional datastructure example
    Produce HoloMap with two sliders
    """

    hv.extension('matplotlib')
    renderer = hv.renderer('matplotlib')
    hv.output('size=200')

    xr_ensembles = xr.open_dataset('./sample-data/ensembles.nc')
    dataset = gv.Dataset(xr_ensembles, vdims='surface_temperature', crs=ccrs.PlateCarree())

    hv.Dimension.type_formatters[np.datetime64] = '%Y-%m-%d'

    geo_dims = ['longitude', 'latitude']
    img = (dataset.to(gv.Image, geo_dims) * gf.coastline)[::5, ::5]
    renderer.save(img, 'realization')

def realization_plot_3panel():
    """
    Three panel example with FilledContours, LineContours and Point elements
    """

    hv.extension('matplotlib')
    renderer = hv.renderer('matplotlib')
    hv.output('size=200')

    xr_ensembles = xr.open_dataset('./sample-data/ensembles.nc')
    dataset = gv.Dataset(xr_ensembles, vdims='surface_temperature', crs=ccrs.PlateCarree())

    hv.Dimension.type_formatters[np.datetime64] = '%Y-%m-%d'

    geo_dims = ['longitude', 'latitude']
    img = hv.Layout([dataset.to(el, geo_dims)[::10, ::10] * gf.coastline
                   for el in [gv.FilledContours, gv.LineContours, gv.Points]]).cols(1)

    # apply the opts locally by using them on img rather than hv.opts
    opts = "Points [color_index=2 size_index=None] (cmap='jet')"
    renderer.save(img.opts(opts), 'realization_3panel')

def dynamic_example():
    """
    requires a bokeh serve command to work correctly, saved html image
    will be like that on the website, the slider won't work.
    If you want to have the dynamic feature work
    See Gridded_Datasets_II_dyn.py and use a bokeh server
    """
    hv.extension('bokeh', 'matplotlib')
    renderer = hv.renderer('bokeh')
    hv.output('size=200')

    xr_ensembles = xr.open_dataset('./sample-data/ensembles.nc')
    dataset = gv.Dataset(xr_ensembles, vdims='surface_temperature', crs=ccrs.PlateCarree())

    hv.Dimension.type_formatters[np.datetime64] = '%Y-%m-%d'

    geo_dims = ['longitude', 'latitude']
    img = (dataset.to(gv.Image, geo_dims, dynamic=True) * gf.coastline)
    renderer.save(img, 'dynamic_example')

def irregularly_sampled_data():
    """
    If you get an issue with dates in the dataset, delete the file in
    ~/.xarray_tutorial_data/

    from the projection we can tell docs use matplotlib backend.
    however, to get dynamic=True to work outside of notebook we
    will use a bokeh server, which means which means we need bokeh backend.

    Here we will just replicate what is in the docs. For a true dynamic
    example see Gridded_Datasets_II_dyn.
    """

    hv.extension('matplotlib')
    renderer = hv.renderer('matplotlib')

    # cannot use projections in the img.opts() like in notebook notebook
    opts = "QuadMesh [colorbar=True fig_size=300] (cmap='RdBu_r')"
    xrds = xr.tutorial.load_dataset('rasm')

    qmesh = gv.Dataset(xrds.Tair).to(gv.QuadMesh, ['xc', 'yc'], dynamic=True)
    print('loaded')
    qmesh.redim.range(Tair=(-30, 30)) * gf.coastline

    # apply the opts, and do the projection
    img = qmesh.opts(opts)(plot=dict(projection=ccrs.Robinson())) * gf.coastline
    renderer.save(img, 'irregularly_sampled_data')

def temp_over_time():
    """
    Non-geographic views.
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

    renderer.save(img, 'temp_over_time')


def heatmap():
    """
    requires a bokeh serve command to work correctly, saved html image
    will be like that on the website, the slider won't work.
    If you want to have the dynamic feature work see
    Gridded_Datasets_II_dyn.py
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
    renderer.save(img, 'dynamic_heatmap')

def boxplots():
    """
    lower-dimensional view, boxplot example
    """

    hv.extension('matplotlib')
    renderer = hv.renderer('matplotlib')
    #hv.output('size=200')

    xr_ensembles = xr.open_dataset('./sample-data/ensembles.nc')
    dataset = gv.Dataset(xr_ensembles, vdims='surface_temperature', crs=ccrs.PlateCarree())

    hv.Dimension.type_formatters[np.datetime64] = '%Y-%m-%d'

    opts = "BoxWhisker [xrotation=25 bgcolor='w']"
    hv.opts(opts)
    img = hv.Layout([dataset.to(hv.BoxWhisker, d, None, []) for d in ['time', 'realization']])
    renderer.save(img, 'box_plots')

def distribution_example():
    """
    lower-dimensional view, Distribution example
    """
    hv.extension('matplotlib')
    renderer = hv.renderer('matplotlib')
    #hv.output('size=200')

    xr_ensembles = xr.open_dataset('./sample-data/ensembles.nc')
    dataset = gv.Dataset(xr_ensembles, vdims='surface_temperature', crs=ccrs.PlateCarree())

    hv.Dimension.type_formatters[np.datetime64] = '%Y-%m-%d'

    opts = "GridSpace [shared_xaxis=True]"
    hv.opts(opts)
    grid = dataset.to(hv.Distribution, 'surface_temperature', groupby=['realization', 'time']).grid()
    renderer.save(grid, 'distribution')

def slice_example():
    """
    Easily select ranges of coordinates
    """

    hv.extension('matplotlib')
    renderer = hv.renderer('matplotlib')
    hv.output('size=200')

    xr_ensembles = xr.open_dataset('./sample-data/ensembles.nc')
    dataset = gv.Dataset(xr_ensembles, vdims='surface_temperature', crs=ccrs.PlateCarree())

    hv.Dimension.type_formatters[np.datetime64] = '%Y-%m-%d'

    geo_dims = ['longitude', 'latitude']
    northern = dataset.select(latitude=(25, 75))
    img = (northern.select(longitude=(260, 305)).to(gv.Image, geo_dims) *
             northern.select(longitude=(330, 362)).to(gv.Image, geo_dims) *
              gf.coastline)[::5, ::5]
    renderer.save(img, 'slice_example')

def select_coords():
    """
    Select a coord and cast dta to Curves element
    """

    hv.extension('bokeh', 'matplotlib')
    renderer = hv.renderer('bokeh')
    hv.output('size=100')

    xr_ensembles = xr.open_dataset('./sample-data/ensembles.nc')
    dataset = gv.Dataset(xr_ensembles, vdims='surface_temperature', crs=ccrs.PlateCarree())

    hv.Dimension.type_formatters[np.datetime64] = '%Y-%m-%d'

    geo_dims = ['longitude', 'latitude']

    opts ="NdOverlay [width=600 height=400 legend_position='right' toolbar='above'] Curve (color=Palette('Set1'))"
    img = dataset.select(latitude=0, longitude=0).to(hv.Curve, ['time']).reindex().overlay()

    renderer.save(img.opts(opts), 'select_coords')

def aggregate_example():
    """
    Aggregate over dimensions.
    Compute mean and standard deviation by latitude and longitude
    """

    hv.extension('bokeh', 'matplotlib')
    renderer = hv.renderer('bokeh')
    hv.output('size=100')

    xr_ensembles = xr.open_dataset('./sample-data/ensembles.nc')
    dataset = gv.Dataset(xr_ensembles, vdims='surface_temperature', crs=ccrs.PlateCarree())

    hv.Dimension.type_formatters[np.datetime64] = '%Y-%m-%d'

    geo_dims = ['longitude', 'latitude']

    img = hv.Spread(dataset.aggregate('latitude', np.mean, np.std)) +\
                hv.Spread(dataset.aggregate('longitude', np.mean, np.std))

    renderer.save(img, 'aggregate_example')

if __name__ == '__main__':
    realization_plot()
    realization_plot_3panel()
    dynamic_example()
    irregularly_sampled_data()
    temp_over_time()
    heatmap()
    boxplots()
    distribution_example()
    slice_example()
    select_coords()
    aggregate_example()

