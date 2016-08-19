import os, glob
from shutil import copyfile
import param

from .element import (_Element, Feature, Tiles,     # noqa (API import)
                      WMTS, LineContours, FilledContours, Text, Image,
                      Points, Path, Polygons, Shape, Dataset)
from . import plotting                              # noqa (API import)


__version__ = param.Version(release=(1,0,0), fpath=__file__,
                            commit="$Format:%h$", reponame='geoviews')


def examples(path='geoviews-examples', verbose=False):
    """
    Copies the examples to the supplied path.
    """

    import os, glob
    from shutil import copytree, ignore_patterns

    candidates = [os.path.join(__path__[0], '../doc/'),
                  os.path.join(__path__[0], '../../../../share/geoviews-examples')]

    path = os.path.abspath(path)
    if not os.path.exists(path):
        os.makedirs(path)
        if verbose:
            print('Created directory %s' % path)

    for source in candidates:
        if os.path.exists(source):
            for nb in glob.glob(os.path.join(source, '*.ipynb')):
                nb_name = os.path.basename(nb)
                nb_path = os.path.join(path, nb_name)
                copyfile(nb, nb_path)
                if verbose:
                    print("%s copied to %s" % (nb_name, path))
            break
