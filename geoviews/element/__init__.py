from holoviews.element import (
    ElementConversion, Points as HvPoints, Polygons as HvPolygons,
    Path as HvPath
)

from .geo import (_Element, Feature, Tiles, is_geographic,     # noqa (API import)
                  WMTS, Points, Image, Text, LineContours, RGB,
                  FilledContours, Path, Polygons, Shape, Dataset,
                  Contours, TriMesh, Graph, Nodes, EdgePaths, QuadMesh,
                  VectorField, Labels, HexTiles, Rectangles, Segments)


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
        group_type = args[0]
        if 'crs' not in kwargs and issubclass(group_type, _Element):
            kwargs['crs'] = self._element.crs
        is_gpd = self._element.interface.datatype == 'geodataframe'
        if is_gpd:
            kdims = args[1] if len(args) > 1 else kwargs.get('kdims', None)
            if len(args) > 1:
                args = (Dataset, [])+args[2:]
            else:
                args = (Dataset,)
                kwargs['kdims'] = []
        converted = super().__call__(*args, **kwargs)
        if is_gpd:
            if kdims is None: kdims = group_type.kdims
            converted = converted.map(lambda x: x.clone(kdims=kdims, new_type=group_type), Dataset)
        return converted

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

    def polygons(self, kdims=None, vdims=None, mdims=None, **kwargs):
        if kdims is None: kdims = self._element.kdims
        el_type = Polygons if is_geographic(self._element, kdims) else HvPolygons
        return self(el_type, kdims, vdims, mdims, **kwargs)

    def path(self, kdims=None, vdims=None, mdims=None, **kwargs):
        if kdims is None: kdims = self._element.kdims
        el_type = Path if is_geographic(self._element, kdims) else HvPath
        return self(el_type, kdims, vdims, mdims, **kwargs)


Dataset._conversion_interface = GeoConversion
