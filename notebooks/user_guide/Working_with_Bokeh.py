import xarray as xr
import pandas as pd
import holoviews as hv
import geoviews as gv
import geoviews.feature as gf
import geopandas as gpd

from cartopy import crs as ccrs

from bokeh.tile_providers import STAMEN_TONER, STAMEN_TONER_LABELS

"""
The following examples were taken from
http://geoviews.org/user_guide/Working_with_Bokeh.html

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

def WMTS_tiles():
    """
    Example showing the different tile sources available.
    e.g. ESRI, OpenMap, Stamen Toner and Wikipedia
    """

    hv.extension('bokeh')
    renderer = hv.renderer('bokeh')

    tiles = {'OpenMap': 'http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png',
         'ESRI': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg',
         'Wikipedia': 'https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}@2x.png',
         'Stamen Toner': STAMEN_TONER}

    opts = "WMTS [width=450 height=250 xaxis=None yaxis=None]"
    img = hv.NdLayout({name: gv.WMTS(wmts).opts(opts)
                for name, wmts in tiles.items()}, kdims=['Source']).cols(2)

    renderer.save(img, 'WMTS_tiles')

def label_example():
    """
    Apply the STAMEN TONER labels to a map
    """

    hv.extension('bokeh')
    renderer = hv.renderer('bokeh')

    tiles = {'OpenMap': 'http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png',
         'ESRI': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg',
         'Wikipedia': 'https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}@2x.png',
         'Stamen Toner': STAMEN_TONER}

    opts = "WMTS [width=600 height=570]"
    img = gv.WMTS(tiles['ESRI'], extents=(0, -90, 360, 90), crs=ccrs.PlateCarree()) *\
            gv.WMTS(STAMEN_TONER_LABELS).opts(style=dict(level='annotation'))

    renderer.save(img.opts(opts), 'label_example')


def cities_example():
    """
    HoloMap showing city populations over time.
    Can hover over cities to get information

    """
    hv.extension('bokeh')
    renderer = hv.renderer('bokeh')

    tiles = {'OpenMap': 'http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png',
         'ESRI': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg',
         'Wikipedia': 'https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}@2x.png',
         'Stamen Toner': STAMEN_TONER}

    cities = pd.read_csv('./assets/cities.csv', encoding="ISO-8859-1")
    population = gv.Dataset(cities, kdims=['City', 'Country', 'Year'])
    cities.head()

    opts_ov = "Overlay [width=600 height=350]"
    opts_pt = " Points (size=0.005 cmap='viridis') [tools=['hover'] size_index=2 color_index=2]"
    img = (gv.WMTS(tiles['Wikipedia']) *\
            population.to(gv.Points, kdims=['Longitude', 'Latitude'],
                              vdims=['Population', 'City', 'Country'], crs=ccrs.PlateCarree()))

    # we can chain opts as well as combing them in the string
    renderer.save(img.opts(opts_ov).opts(opts_pt), 'cities_example')


def choropleth_example():
    """
    Example with geopandas.
    """

    hv.extension('bokeh')
    renderer = hv.renderer('bokeh')

    geometries = gpd.read_file('./assets/boundaries/boundaries.shp')
    referendum = pd.read_csv('./assets/referendum.csv')
    gdf = gpd.GeoDataFrame(pd.merge(geometries, referendum))

    opts = ("Polygons [tools=['hover'] width=450 height=600 color_index=""'leaveVoteshare'"
            " colorbar=True toolbar='above' xaxis=None yaxis=None]")
    img = gv.Polygons(gdf, vdims=['name', 'leaveVoteshare'])

    renderer.save(img.opts(opts), 'choropleth_example')

def image_example():

    hv.extension('bokeh')
    renderer = hv.renderer('bokeh')

    opts = "Overlay [width=600 height=500] Image (cmap='viridis') Feature (line_color='black')"
    dataset = xr.open_dataset('./sample-data/pre-industrial.nc')
    air_temperature = gv.Dataset(dataset, kdims=['longitude', 'latitude'], 
            group='Pre-industrial air temperature', vdims=['air_temperature'], 
            crs=ccrs.PlateCarree())
    img = air_temperature.to.image() * gf.coastline()

    renderer.save(img.opts(opts), 'image_example')

if __name__ == '__main__':
    WMTS_tiles()
    label_example()
    cities_example()
    choropleth_example()
    image_example()
