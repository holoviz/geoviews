import os, glob
import requests
from io import BytesIO
from shutil import copyfile, copytree
from zipfile import ZipFile

from .element import (_Element, Feature, Tiles,     # noqa (API import)
                      WMTS, LineContours, FilledContours, Text, Image,
                      Points, Path, Polygons, Shape, Dataset, RGB,
                      Contours, Graph, TriMesh, Nodes, EdgePaths,
                      QuadMesh, VectorField, HexTiles, Labels)
from . import data                                  # noqa (API import)
from . import operation                             # noqa (API import)
from . import plotting                              # noqa (API import)
from . import feature                               # noqa (API import)


try:
    from version import Version
    __version__ = str(Version(fpath=__file__, archive_commit="$Format:%h$",
                              reponame="geoviews"))
except:
    import json
    __version__ = json.load(open(os.path.join(os.path.split(__file__)[0],
                                              '.version'), 'r'))['version_string']

SAMPLE_DATA_URL = 'http://assets.holoviews.org/geoviews-sample-data.zip'


def examples(path='geoviews-examples', include_data=False, verbose=False):
    """
    Copies the example notebooks to the supplied path. If
    include_data is enabled the sample data is also downloaded.
    """
    candidates = [os.path.join(__path__[0], '../doc/'),
                  os.path.join(__path__[0], '../../../../share/geoviews-examples')]

    path = os.path.abspath(path)
    asset_path = os.path.join(path, 'assets')
    if not os.path.exists(path):
        os.makedirs(path)
        if verbose:
            print('Created directory %s' % path)

    for source in candidates:
        if os.path.exists(source):
            if not os.path.exists(asset_path):
                copytree(os.path.join(source, 'assets'), asset_path)
                if verbose:
                    print('Copied assets to %s' % asset_path)
            for nb in glob.glob(os.path.join(source, '*.ipynb')):
                nb_name = os.path.basename(nb)
                nb_path = os.path.join(path, nb_name)
                copyfile(nb, nb_path)
                if verbose:
                    print("%s copied to %s" % (nb_name, path))
            break

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
