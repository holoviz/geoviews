import pandas as pd
import holoviews as hv
import geoviews as gv
import geoviews.feature as gf
import cartopy
import cartopy.feature as cf
from cartopy import crs as ccrs
import geopandas as gpd

"""
The following examples were taken from
http://geo.holoviews.org/user_guide/Geometries.html

This script is designed to be run by the python interpreter rather
than in a notebook.
Each function has been designed as a stand-alone example.

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

def geoviews_features():
    """
    geoviews features example
    using matplotlib as a backend so we can save as svg
    """

    hv.extension('matplotlib')
    renderer = hv.renderer('matplotlib')
    renderer.dpi = 120

    features = (gf.ocean + gf.land + gf.ocean * gf.land * gf.coastline * gf.borders).cols(3)
    renderer.save(features, 'geoviews_features', fmt='svg')


def natural_earth_features():
    """
    load custom NaturalEarthFeatures such as graticules at 30 intervals
    """
    hv.extension('matplotlib')
    renderer = hv.renderer('matplotlib')
    renderer.dpi = 120

    graticules = cf.NaturalEarthFeature(
        category='physical', name='graticules_30', scale='110m')
    features = gf.ocean * gf.land() * gv.Feature(
        graticules, group='Lines') * gf.borders * gf.coastline

    # define how the Lines element will look, will use a dictionary to
    # show how it is done but later we will use the string fromat
    opts = {
        'Feature.Lines': {
            'plot': dict(projection=ccrs.Robinson()),
            'style': dict(facecolor='none', edgecolor='gray')
        }
    }

    renderer.save(features, 'natural_earth_features', fmt='svg', options=opts)


def feature_scale():
    """
    set the scale of features in cartopy.
    use bokeh as the backend so we can zoom

    This plot is slightly different to that on the website as it
    has been modified to show how scale works on land feature
    """
    hv.extension('bokeh', 'matplotlib')
    renderer = hv.renderer('bokeh')
    # hv.opts applies options globally, later we will see that we can
    # apply our options to a single element/object. here we are
    # still using the dictionary format
    hv.opts({'Feature.Land.110m': {'plot': dict(scale='110m')}})
    hv.opts({'Feature.Land.50m': {'plot': dict(scale='50m')}})

    graticules = cf.NaturalEarthFeature(
        category='physical', name='graticules_30', scale='110m')

    feat_110m = gf.ocean * gf.land().relabel(label='110m') * gv.Feature(graticules, group='Lines')
    feat_50m = gf.ocean * gf.land().relabel(label='50m') * gv.Feature(graticules, group='Lines')

    img = feat_110m + feat_50m
    renderer.save(img, 'feature_scale')

def shape_files():
    """
    Shape example: plotting Australia with matplotlib and overlaying
    Alice Springs point.
    """
    hv.extension('matplotlib')
    renderer = hv.renderer('matplotlib')

    # use string format for opts, much easier especially later when
    # we have more options to set
    opts = "Points (color='black')"
    hv.opts(opts)

    land_geoms = list(gf.land.data.geometries())
    australia = gv.Shape(land_geoms[21], crs=ccrs.PlateCarree())
    img = (australia * gv.Points([(133.870,-23.700)]) 
            * gv.Text(133.870,-21.5, 'Alice Springs', crs=ccrs.PlateCarree()))
    renderer.save(img, 'Alice_Springs')

def NdOverlay():
    """
    creating an NdOverlay
    """
    hv.extension('matplotlib')
    renderer = hv.renderer('matplotlib')

    land_geoms = list(gf.land.data.geometries())

    img = hv.NdOverlay({i: gv.Shape(s, crs=ccrs.PlateCarree()) for i, s in enumerate(land_geoms)})

    # apply options locally by supplying them to the renderer
    renderer.save(img, 'ndoverlay', options={'NdOverlay': {'plot': dict(aspect=2)}})

def UK_electoral_boundaries():
    """
    read a shape file and plot the UK electoral boundaries
    """
    hv.extension('matplotlib')
    renderer = hv.renderer('matplotlib')

    shapefile = './assets/boundaries/boundaries.shp'
    shp = gv.Shape.from_shapefile(shapefile, crs=ccrs.PlateCarree())
    renderer.save(shp, 'UK_electoral_boundaries')

def choropleth():
    """
    Create a choropleth map using shape file and referendum data (pandas)

    using bokeh backend
    """
    hv.extension('bokeh', 'matplotlib')
    renderer = hv.renderer('bokeh')

    shapefile = './assets/boundaries/boundaries.shp'
    shapes = cartopy.io.shapereader.Reader(shapefile)

    referendum = pd.read_csv('./assets/referendum.csv')
    referendum = hv.Dataset(referendum)

    img = gv.Shape.from_records(shapes.records(), referendum, on='code',
            value='leaveVoteshare', index=['name', 'regionName'],
            crs=ccrs.PlateCarree())

    # apply options locally using the opts method
    opts = {'Shape':{'style':dict(cmap='viridis')}}
    renderer.save(img.opts(opts), 'chloropleth')

def geopandas():
    """
    We can simply pass the GeoPandas DataFrame to a Polygons,
    Path or Contours element and it will plot the data for us.
    The Contours and Polygons will automatically color the data
    by the first specified value dimension defined by the vdims keyword
    (the geometries may be colored by any dimension using the 
    color_index plot option):

    using matplotlib backend
    """
    hv.extension('matplotlib')
    renderer = hv.renderer('matplotlib')

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # note we cannot pass the projection or size into the .opts() method
    renderer.size = 250
    img = gv.Polygons(world, vdims='pop_est')(plot=dict(projection=ccrs.Robinson()))
    renderer.save(img, 'geopandas', fmt='svg')

def bokeh_hover_tools():
    """
    geopandas example with bokeh backend and hover tool

    Geometries can be displayed using both matplotlib and bokeh,
    here we will switch to bokeh allowing us to color by a categorical
    variable ( continent ) and activating the hover tool to reveal
    information about the plot.
    """
    hv.extension('bokeh')
    renderer = hv.renderer('bokeh')

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    opts = "Polygons [width=600 height=500 tools=['hover']] (cmap='tab20')"
    vdims = ['continent',  'name', 'pop_est']
    img = gv.Polygons(world, vdims=vdims).redim.range(Latitude=(-60, 90))
    img = img.opts(opts)
    renderer.save(img, 'world_map_with_hover')

if __name__ == '__main__':
    geoviews_features()
    natural_earth_features()
    feature_scale()
    shape_files()
    NdOverlay()
    UK_electoral_boundaries()
    choropleth()
    geopandas()
    bokeh_hover_tools()
