import iris
from holoviews.core.data import Dataset
from holoviews.element import ElementConversion, Points as HvPoints

from .geo import (_Element, Feature, Tiles,     # noqa (API import)
                  WMTS, Points, Image, Text, Contours)


def is_geographic(dataset, kdims):
    """
    Small utility that determines whether the supplied dataset
    and kdims represent a geographic coordinate system.
    """

    kdims = [dataset.get_dimension(d) for d in kdims]
    if (len(kdims) == 2 and
        ((isinstance(dataset, _Element) and kdims == dataset.kdims) or
        (isinstance(dataset.data, iris.cube.Cube) and all(dataset.data.coord(
            kd.name).coord_system for kd in kdims)))):
        return True
    return False


class GeoConversion(ElementConversion):
    """
    GeoConversion is a very simple container object which can
    be given an existing Dataset and provides methods to convert
    the Dataset into most other Element types. If the requested
    key dimensions correspond to geographical coordinates the
    conversion interface will automatically use a geographical
    Element type while all other plot will use regular HoloViews
    Elements.
    """

    def __init__(self, cube):
        self._element = cube

    def contours(self, kdims=None, vdims=None, mdims=None, **kwargs):
        return self(Contours, kdims, vdims, mdims, **kwargs)

    def image(self, kdims=None, vdims=None, mdims=None, **kwargs):
        return self(Image, kdims, vdims, mdims, **kwargs)

    def points(self, kdims=None, vdims=None, mdims=None, **kwargs):
        if kdims is None: kdims = self._element.kdims
        el_type = Points if is_geographic(self._element, kdims) else HvPoints
        return self(el_type, kdims, vdims, mdims, **kwargs)


Dataset._conversion_interface = GeoConversion
