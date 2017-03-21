[![Travis](https://api.travis-ci.org/ioam/geoviews.svg?branch=master)](https://travis-ci.org/ioam/geoviews)
[![Coveralls](https://img.shields.io/coveralls/ioam/geoviews.svg)](https://coveralls.io/github/ioam/geoviews)
[![Waffle](https://badge.waffle.io/ioam/geoviews.png?label=ready&title=ready)](https://waffle.io/ioam/geoviews)

# GeoViews

GeoViews is a Python library that makes it easy to explore and
visualize any data that includes geographic locations.  It has
particularly powerful support for multidimensional meteorological
and oceanographic datasets, such as those used in weather, climate,
and remote sensing research, but is useful for almost anything
that you would want to plot on a map!  You can see lots of example 
notebooks at [geo.holoviews.org](http://geo.holoviews.org), and a good 
overview is in our [blog post announcement](https://www.continuum.io/blog/developer-blog/introducing-geoviews).

GeoViews is built on the [HoloViews](http://holoviews.org) library for
building flexible visualizations of multidimensional data.  GeoViews
adds a family of geographic plot types based on the
[Cartopy](http://scitools.org.uk/cartopy) library, plotted using
either the [Matplotlib](http://matplotlib.org) or
[Bokeh](http://bokeh.pydata.org) packages.  Each of the new
`GeoElement` plot types is a new HoloViews `Element` that has an
associated geographic projection based on `cartopy.crs`. The
`GeoElements` currently include `Feature`, `WMTS`, `Tiles`, `Points`,
`Contours`, `Image`, and `Text` objects, each of which can easily be
overlaid in the same plots.  E.g. an object with temperature data can
be overlaid with coastline data using an expression like
``gv.Image(temperature)*gv.Feature(cartopy.feature.COASTLINE)``.  Each
`GeoElement` can also be freely combined in layouts with any other
HoloViews `Element`, making it simple to make even complex
multi-figure layouts of overlaid objects.

## Installation

You can then install GeoViews and its other dependencies using conda,
many users will want iris and/or xarray as well:


```
conda install -c conda-forge -c ioam holoviews>=1.6.2 geoviews
# (Optional)
conda install xarray
conda install -c conda-forge iris
```

You can now switch to your preferred working directory, grab a copy of
the notebooks to run locally, and run them using the Jupyter notebook:: 

```
cd ~
python -c 'import geoviews; geoviews.examples("geoviews-examples",include_data=True)'
cd geoviews-examples
jupyter notebook
```
