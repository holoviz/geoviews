import param

from holoviews import (extension, help, opts, output, renderer, Store, # noqa (API import)
                       Cycle, Palette, Overlay, Layout, NdOverlay, NdLayout,
                       HoloMap, DynamicMap, GridSpace, Dimension, dim)

from holoviews import render, save # noqa (API import)

from .annotators import annotate # noqa (API import)
from .element import ( # noqa (API import)
    _Element, Feature, Tiles, WMTS, LineContours, FilledContours,
    Text, Image, Points, Path, Polygons, Shape, Dataset, RGB,
    Contours, Graph, TriMesh, Nodes, EdgePaths, QuadMesh, VectorField,
    HexTiles, Labels, Rectangles, Segments
)
from .util import load_tiff, from_xarray # noqa (API import)
from .operation import project                      # noqa (API import)
from ._warnings import GeoviewsDeprecationWarning, GeoviewsUserWarning  # noqa: F401
from . import data                                  # noqa (API import)
from . import operation                             # noqa (API import)
from . import plotting                              # noqa (API import)
from . import feature                               # noqa (API import)
from . import tile_sources                          # noqa (API import)

__version__ = str(param.version.Version(fpath=__file__, archive_commit="$Format:%h$",
                                        reponame="geoviews"))

# Ensure opts utility is initialized with GeoViews elements
if Store._options:
    Store.set_current_backend(Store.current_backend)

# make pyct's example/data commands available if possible
from functools import partial
try:
    from pyct.cmd import copy_examples as _copy, fetch_data as _fetch, examples as _examples
    copy_examples = partial(_copy, 'geoviews')
    fetch_data = partial(_fetch, 'geoviews')
    examples = partial(_examples, 'geoviews')
except ImportError:
    def _missing_cmd(*args,**kw): return("install pyct to enable this command (e.g. `conda install -c pyviz pyct`)")
    _copy = _fetch = _examples = _missing_cmd
    def _err(): raise ValueError(_missing_cmd())
    fetch_data = copy_examples = examples = _err
del partial, _examples, _copy, _fetch
