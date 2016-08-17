from holoviews.element import ElementConversion, Points as HvPoints

from .geo import (_Element, Feature, Tiles, is_geographic,     # noqa (API import)
                  WMTS, Points, Image, Text, LineContours,
                  FilledContours, Path, Polygons, Shape, Dataset)


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

    def __call__(self, *args, **kwargs):
        if 'crs' not in kwargs and isinstance(self._element, _Element):
            kwargs['crs'] = self._element.crs
        return super(GeoConversion, self).__call__(*args, **kwargs)

    def linecontours(self, kdims=None, vdims=None, mdims=None, **kwargs):
        return self(LineContours, kdims, vdims, mdims, **kwargs)

    def filledcontours(self, kdims=None, vdims=None, mdims=None, **kwargs):
        return self(FilledContours, kdims, vdims, mdims, **kwargs)

    def image(self, kdims=None, vdims=None, mdims=None, **kwargs):
        return self(Image, kdims, vdims, mdims, **kwargs)

    def points(self, kdims=None, vdims=None, mdims=None, **kwargs):
        if kdims is None: kdims = self._element.kdims
        el_type = Points if is_geographic(self._element, kdims) else HvPoints
        return self(el_type, kdims, vdims, mdims, **kwargs)


Dataset._conversion_interface = GeoConversion
