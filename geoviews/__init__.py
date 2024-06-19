from functools import partial

import param
from holoviews import (  # noqa: F401
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

from . import (  # noqa: F401
    data,
    feature,
    plotting,
    tile_sources,
)
from ._warnings import GeoviewsDeprecationWarning, GeoviewsUserWarning  # noqa: F401
from .element import (  # noqa: F401
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
    _Element,
)
from .util import from_xarray  # noqa: F401

__version__ = str(param.version.Version(fpath=__file__, archive_commit="$Format:%h$",
                                        reponame="geoviews"))

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

__all__ = [k for k in locals() if not k.startswith('_')]
__all__ += ['annotate', 'project', 'operation', '__version__']

def __dir__():
    return __all__

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import operation
    from .annotators import annotate
    from .operation import project
