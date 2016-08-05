import os, glob
from shutil import copyfile
import param

from .element import (_Element, Feature, Tiles,     # noqa (API import)
                      WMTS, LineContours, FilledContours, Text, Image,
                      Points, Path, Polygons, Shape)
from . import plotting                              # noqa (API import)


__version__ = param.Version(release=(1,0,0), fpath=__file__,
                            commit="$Format:%h$", reponame='geoviews')

def examples(path='.', verbose=False):
    """
    Copies the example Jupyter notebooks to the supplied path.
    """
    path = os.path.abspath(path)
    if not os.path.exists(path):
        os.makedirs(path)
        if verbose:
            print('Created directory %s' % path)
    notebook_glob = os.path.join(__path__[0], '..', 'doc', '*.ipynb')
    notebooks = glob.glob(notebook_glob)
    for notebook in notebooks:
        nb_path = os.path.join(path, os.path.basename(notebook))
        copyfile(notebook, nb_path)
        if verbose:
            print("%s copied to %s" % (os.path.basename(notebook), path))

