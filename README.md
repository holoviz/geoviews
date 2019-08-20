[![Travis](https://api.travis-ci.org/pyviz/geoviews.svg?branch=master)](https://travis-ci.org/pyviz/geoviews)
[![Windows build status](https://ci.appveyor.com/api/projects/status/4yl8w4kie2m0xu1q/branch/master?svg=true)](https://ci.appveyor.com/project/pyviz/geoviews/branch/master)

<h1>
GeoViews <img src="/doc/_static/geoviews-logo.png" width="50" height="50">
</h1>

GeoViews is a Python library that makes it easy to explore and
visualize any data that includes geographic locations.  It has
particularly powerful support for multidimensional meteorological
and oceanographic datasets, such as those used in weather, climate,
and remote sensing research, but is useful for almost anything
that you would want to plot on a map!  You can see lots of example 
notebooks at [geoviews.org](https://geoviews.org), and a good 
overview is in our [blog post announcement](https://www.continuum.io/blog/developer-blog/introducing-geoviews).

GeoViews is built on the [HoloViews](https://holoviews.org) library for
building flexible visualizations of multidimensional data.  GeoViews
adds a family of geographic plot types based on the
[Cartopy](http://scitools.org.uk/cartopy) library, plotted using
either the [Matplotlib](http://matplotlib.org) or
[Bokeh](https://bokeh.pydata.org) packages.

Each of the new GeoElement plot types is a new HoloViews Element that
has an associated geographic projection based on ``cartopy.crs``. The
GeoElements currently include ``Feature``, ``WMTS``, ``Tiles``,
``Points``, ``Contours``, ``Image``, ``QuadMesh``, ``TriMesh``,
``RGB``, ``HSV``, ``Labels``, ``Graph``, ``HexTiles``, ``VectorField``
and ``Text`` objects, each of which can easily be overlaid in the same
plots. E.g. an object with temperature data can be overlaid with
coastline data using an expression like ``gv.Image(temperature) *
gv.Feature(cartopy.feature.COASTLINE)``. Each GeoElement can also be
freely combined in layouts with any other HoloViews Element , making
it simple to make even complex multi-figure layouts of overlaid
objects.

## Installation

You can install GeoViews and its dependencies using conda:
   
```
conda install -c pyviz geoviews
```

Alternatively you can also install the geoviews-core package, which
only installs the minimal dependencies required to run geoviews:

```
conda install -c pyviz geoviews-core
```

Once installed you can copy the examples into the current directory
using the ``geoviews`` command and run them using the Jupyter
notebook:

```
geoviews examples 
cd geoviews-examples
jupyter notebook
```

(Here `geoviews examples` is a shorthand for `geoviews copy-examples
--path geoviews-examples && geoviews fetch-data --path
geoviews-examples`.)

To work with JupyterLab you will also need the PyViz JupyterLab
extension:

```
conda install -c conda-forge jupyterlab
jupyter labextension install @pyviz/jupyterlab_pyviz
```

Once you have installed JupyterLab and the extension launch it with:

```
jupyter-lab
```

If you want to try out the latest features between releases, you can
get the latest dev release by specifying `-c pyviz/label/dev` in place
of `-c pyviz`.

### Additional dependencies

If you need to install libraries only available from conda-forge, such
as Iris (to use data stored in Iris cubes) or xesmf, you should
install from conda-forge:

```
conda create -n env-name -c pyviz -c conda-forge geoviews iris xesmf
conda activate env-name
```

**Note -- Do not mix conda-forge and defaults.** I.e., do not install
packages from conda-forge into a GeoViews environment created with
defaults. If you are using the base environment of mini/anaconda, or
an environment created without specifying conda-forge before defaults,
and you then install from conda-forge, you will very likely have
incompatibilities in underlying, low-level dependencies. These binary
(ABI) incompatibilities can lead to segfaults because of differences
in how non-Python packages are built between conda-forge and defaults.

-----

GeoViews itself is also installable using `pip`, but to do that you
will first need to have installed the [dependencies of cartopy](http://scitools.org.uk/cartopy/docs/v0.15/installing.html#requirements),
or else have set up your system to be able to build them.
