from functools import partial

from holoviews import (
    Cycle,
    Dimension,
    DynamicMap,
    GridSpace,
    HoloMap,
    Layout,
    NdLayout,
    NdOverlay,
    Overlay,
    Palette,
    Store,
    dim,
    extension,
    help,
    opts,
    output,
    render,
    renderer,
    save,
)

from . import data, feature, plotting, tile_sources
from .__version import __version__
from ._warnings import GeoviewsDeprecationWarning, GeoviewsUserWarning
from .element import (
    RGB,
    WMTS,
    Contours,
    Dataset,
    EdgePaths,
    Feature,
    FilledContours,
    Graph,
    HexTiles,
    Image,
    ImageStack,
    Labels,
    LineContours,
    Nodes,
    Path,
    Points,
    Polygons,
    QuadMesh,
    Rectangles,
    Segments,
    Shape,
    Text,
    Tiles,
    TriMesh,
    VectorField,
    WindBarbs,
)
from .util import from_xarray

__all__ = (
    "RGB",
    "WMTS",
    "Contours",
    "Cycle",
    "Dataset",
    "Dimension",
    "DynamicMap",
    "EdgePaths",
    "Feature",
    "FilledContours",
    "GeoviewsDeprecationWarning",
    "GeoviewsUserWarning",
    "Graph",
    "GridSpace",
    "HexTiles",
    "HoloMap",
    "Image",
    "ImageStack",
    "Labels",
    "Layout",
    "LineContours",
    "NdLayout",
    "NdOverlay",
    "Nodes",
    "Overlay",
    "Palette",
    "Path",
    "Points",
    "Polygons",
    "QuadMesh",
    "Rectangles",
    "Segments",
    "Shape",
    "Store",
    "Text",
    "Tiles",
    "TriMesh",
    "VectorField",
    "WindBarbs",
    "__version__",
    "annotate", # Lazy modules
    "data",
    "dim",
    "extension",
    "feature",
    "from_xarray",
    "help",
    "operation", # Lazy modules
    "opts",
    "output",
    "plotting",
    "project", # Lazy modules
    "render",
    "renderer",
    "save",
    "tile_sources",
)

# Ensure opts utility is initialized with GeoViews elements
if Store._options:
    Store.set_current_backend(Store.current_backend)

# make pyct's example/data commands available if possible
try:
    from pyct.cmd import (
        copy_examples as _copy,
        examples as _examples,
        fetch_data as _fetch,
    )
    copy_examples = partial(_copy, 'geoviews')
    fetch_data = partial(_fetch, 'geoviews')
    examples = partial(_examples, 'geoviews')
except ImportError:
    def _missing_cmd(*args,**kw): return("install pyct to enable this command (e.g. `conda install -c pyviz pyct`)")
    _copy = _fetch = _examples = _missing_cmd
    def _err(): raise ValueError(_missing_cmd())
    fetch_data = copy_examples = examples = _err
del partial, _examples, _copy, _fetch


def __getattr__(attr):
    # Lazy loading heavy modules
    if attr == 'annotate':
        from .annotators import annotate
        return annotate
    elif attr == 'project':
        from .operation import project
        return project
    elif attr == 'operation':
        from . import operation
        return operation
    raise AttributeError(f"module {__name__} has no attribute {attr!r}")


def __dir__():
    return __all__

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import operation
    from .annotators import annotate
    from .operation import project
