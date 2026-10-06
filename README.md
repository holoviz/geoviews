<img src="https://raw.githubusercontent.com/holoviz/geoviews/refs/heads/main/doc/_static/logo_stacked.png" width="200"/><br>

---

**Geographic visualizations for HoloViews.**

|                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Downloads          | ![https://pypistats.org/packages/geoviews](https://img.shields.io/pypi/dm/geoviews?label=pypi) ![https://anaconda.org/pyviz/geoviews](https://pyviz.org/_static/cache/geoviews_conda_downloads_badge.svg)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Build Status       | [![Linux/MacOS/Windows Build Status](https://github.com/holoviz/geoviews/workflows/tests/badge.svg?query=branch:main)](https://github.com/holoviz/geoviews/actions/workflows/test.yaml?query=branch%3Amain)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Coverage           | [![codecov](https://codecov.io/gh/holoviz/geoviews/branch/main/graph/badge.svg)](https://codecov.io/gh/holoviz/geoviews)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Latest dev release | [![Github tag](https://img.shields.io/github/tag/holoviz/geoviews.svg?label=tag&colorB=11ccbb)](https://github.com/holoviz/geoviews/tags) [![dev-site](https://img.shields.io/website-up-down-green-red/https/holoviz-dev.github.io/geoviews.svg?label=dev%20website)](https://holoviz-dev.github.io/geoviews/)                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Latest release     | [![Github release](https://img.shields.io/github/release/holoviz/geoviews.svg?label=tag&colorB=11ccbb)](https://github.com/holoviz/geoviews/releases) [![PyPI version](https://img.shields.io/pypi/v/geoviews.svg?colorB=cc77dd)](https://pypi.python.org/pypi/geoviews) [![geoviews version](https://img.shields.io/conda/v/pyviz/geoviews.svg?colorB=4488ff&style=flat)](https://anaconda.org/pyviz/geoviews) [![conda-forge version](https://img.shields.io/conda/v/conda-forge/geoviews.svg?label=conda%7Cconda-forge&colorB=4488ff)](https://anaconda.org/conda-forge/geoviews) [![defaults version](https://img.shields.io/conda/v/anaconda/geoviews.svg?label=conda%7Cdefaults&style=flat&colorB=4488ff)](https://anaconda.org/anaconda/geoviews) |
| Docs               | [![gh-pages](https://img.shields.io/github/last-commit/holoviz/geoviews/gh-pages.svg)](https://github.com/holoviz/geoviews/tree/gh-pages) [![site](https://img.shields.io/website-up-down-green-red/http/geoviews.org.svg)](http://geoviews.org)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Support            | [![Discourse](https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.holoviz.org)](https://discourse.holoviz.org/)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |

## What is it?

GeoViews is a Python library that makes it easy to explore and
visualize any data that includes geographic locations. It has
particularly powerful support for multidimensional meteorological
and oceanographic datasets, such as those used in weather, climate,
and remote sensing research, but is useful for almost anything
that you would want to plot on a map! You can see lots of example
notebooks at [geoviews.org](https://geoviews.org).

GeoViews is built on the [HoloViews](https://holoviews.org) library for
building flexible visualizations of multidimensional data. GeoViews
adds a family of geographic plot types based on the
[Cartopy](http://scitools.org.uk/cartopy) library, plotted using
either the [Matplotlib](http://matplotlib.org) or
[Bokeh](https://bokeh.org) packages.

Each of the new GeoElement plot types is a new HoloViews Element that
has an associated geographic projection based on `cartopy.crs`. The
GeoElements currently include `Feature`, `WMTS`, `Tiles`, `Points`,
`Path`, `Polygons`, `Shape`, `Contours`, `LineContours`,
`FilledContours`, `Image`, `ImageStack`, `RGB`, `QuadMesh`, `TriMesh`,
`Graph`, `HexTiles`, `Labels`, `Text`, `Rectangles`, `Segments`,
`VectorField` and `WindBarbs` objects, each of which can easily be
overlaid in the same plots. E.g. an object with temperature data can be overlaid with
coastline data using an expression like `gv.Image(temperature) *
gv.Feature(cartopy.feature.COASTLINE)`. Each GeoElement can also be
freely combined in layouts with any other HoloViews Element, making
it simple to make even complex multi-figure layouts of overlaid
objects.

## Installation

You can then install GeoViews and all of its dependencies with the following:

```bash
conda install geoviews
```

Alternatively, you can install the geoviews-core package, which
only installs the minimal dependencies required to run geoviews:

```bash
conda install geoviews-core
```

If you want to try out the latest features between releases, you can
get the latest dev release by specifying `-c pyviz/label/dev`.

You can also install it with pip:

```bash
python -m pip install geoviews
```
