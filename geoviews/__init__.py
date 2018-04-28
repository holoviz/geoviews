import os
import requests
from io import BytesIO
from zipfile import ZipFile

import param
from .element import (_Element, Feature, Tiles,     # noqa (API import)
                      WMTS, LineContours, FilledContours, Text, Image,
                      Points, Path, Polygons, Shape, Dataset, RGB,
                      Contours, Graph, TriMesh, Nodes, EdgePaths,
                      QuadMesh, VectorField, HexTiles, Labels)
from . import data                                  # noqa (API import)
from . import operation                             # noqa (API import)
from . import plotting                              # noqa (API import)
from . import feature                               # noqa (API import)


__version__ = str(param.version.Version(fpath=__file__, archive_commit="$Format:%h$",
                              reponame="geoviews"))



# make pvutil's install_examples() and download_data() available if possible
from functools import partial
try:
    from pvutil.cmd import install_examples as _examples, download_data as _data
    install_examples = partial(_examples,'geoviews')
    download_data = partial(_data,'geoviews')
except ImportError:
    def _missing_cmd(*args,**kw): return("install pvutil to enable this command (e.g. `conda install geoviews`)")
    _data = _examples = _missing_cmd
    def err(): raise ValueError(_missing_cmd())
    download_data = install_examples = err
del partial, _examples, _data
