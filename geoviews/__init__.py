import os, glob
import requests
from io import BytesIO
from shutil import copyfile, copytree
from zipfile import ZipFile

import param

from .element import (_Element, Feature, Tiles,     # noqa (API import)
                      WMTS, LineContours, FilledContours, Text, Image,
                      Points, Path, Polygons, Shape, Dataset, RGB)
from . import operation                             # noqa (API import)
from . import plotting                              # noqa (API import)
from . import feature                               # noqa (API import)


__version__ = param.Version(release=(1,3,0), fpath=__file__,
                            commit="$Format:%h$", reponame='geoviews')

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
