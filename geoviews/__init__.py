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

SAMPLE_DATA_URL = 'http://assets.holoviews.org/geoviews-sample-data.zip'


def examples(path='geoviews-examples', include_data=False, verbose=False):
    """
    Copies the example notebooks to the supplied path. If
    include_data is enabled the sample data is also downloaded.
    """
    import warnings, distutils.dir_util
    source = os.path.join(os.path.dirname(__file__),"examples")
    path = os.path.abspath(path)
    if os.path.exists(path):
        warnings.warn("Path %s already exists; will not overwrite newer files."%path)
    distutils.dir_util.copy_tree(source, path, verbose=verbose)
    print("Installed examples at %s"%path)

    if include_data:
        data_path = os.path.join(path, 'sample-data')
        sample_data(data_path, verbose)


def sample_data(path='../doc/sample-data', verbose=False):
    """
    Downloads and unzips the sample data to a particular location.
    """
    url = requests.get(SAMPLE_DATA_URL)
    zipfile = ZipFile(BytesIO(url.content))
    zip_names = zipfile.namelist()

    path = os.path.abspath(path)
    if not os.path.exists(path):
        os.makedirs(path)
        if verbose:
            print('Created directory %s' % path)

    for nc_file in zip_names:
        extracted_file = zipfile.open(nc_file).read()
        save_path = os.path.join(path, nc_file)
        with open(save_path, 'wb') as f:
            f.write(extracted_file)
        if verbose:
            print("%s downloaded to %s" % (nc_file, path))
