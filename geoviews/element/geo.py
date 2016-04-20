import param

from cartopy import crs as ccrs
from cartopy.feature import Feature as cFeature
from cartopy.io.img_tiles import GoogleTiles as cGoogleTiles
from holoviews.core import Element2D, Dimension, Dataset
from holoviews.core import util
from holoviews.element import Text as HVText
from iris.cube import Cube


class _Element(Element2D):
    """
    Baseclass for Element2D types with associated cartopy
    coordinate reference system.
    """

    _abstract = True

    crs = param.ClassSelector(class_=ccrs.CRS, doc="""
        Cartopy coordinate-reference-system specifying the
        coordinate system of the data. Inferred automatically
        when _Element wraps cartopy Feature object.""")

    def __init__(self, data, **kwargs):
        crs = None
        crs_data = data.data if isinstance(data, Dataset) else data
        if isinstance(crs_data, Cube):
            coord_sys = crs_data.coord_system()
            if hasattr(coord_sys, 'as_cartopy_projection'):
                crs = coord_sys.as_cartopy_projection()
        elif isinstance(crs_data, (cFeature, cGoogleTiles)):
            crs = crs_data.crs

        supplied_crs = kwargs.get('crs', None)
        if supplied_crs and crs and crs != supplied_crs:
            raise ValueError('Supplied coordinate reference '
                             'system must match crs of the data.')
        elif crs:
            kwargs['crs'] = crs
        super(_Element, self).__init__(data, **kwargs)

    def clone(self, data=None, shared_data=True, new_type=None,
              *args, **overrides):
        if 'crs' not in overrides:
            overrides['crs'] = self.crs
        return super(_Element, self).clone(data, shared_data, new_type,
                                           *args, **overrides)


class Feature(_Element):
    """
    A Feature represents a geographical feature
    specified as a cartopy Feature type.
    """

    group = param.String(default='Feature')

    _auxiliary_component = True

    def __init__(self, data, **params):
        if not isinstance(data, cFeature):
            raise TypeError('%s data has to be an cartopy Feature type'
                            % type(data).__name__)
        super(Feature, self).__init__(data, **params)


class WMTS(_Element):
    """
    The WMTS Element represents a Web Map Tile Service
    specified as a tuple of the API URL and
    """

    group = param.String(default='WMTS')

    layer = param.String(doc="The layer on the tile service")

    _auxiliary_component = True

    def __init__(self, data, **params):
        if not isinstance(data, util.basestring):
            raise TypeError('%s data has to be a tile service URL'
                            % type(data).__name__)
        super(WMTS, self).__init__(data, **params)


class Tiles(_Element):
    """
    Tiles represents an image tile source to dynamically
    load data from depending on the zoom level.
    """

    group = param.String(default='Tiles')

    _auxiliary_component = True

    def __init__(self, data, **params):
        if not isinstance(data, cGoogleTiles):
            raise TypeError('%s data has to be a cartopy GoogleTiles type'
                            % type(data).__name__)
        super(Tiles, self).__init__(data, **params)


class Points(_Element, Dataset):
    """
    Points represent a collection of points with
    an associated cartopy coordinate-reference system.
    """

    kdims = param.List(default=['longitude', 'latitude'])

    group = param.String(default='Points')


class Contours(_Element, Dataset):
    """
    Contours represents a 2D array of some quantity with
    some associated coordinates, which may be discretized
    into one or more contours.
    """

    kdims = param.List(default=[Dimension('x'), Dimension('y')])

    vdims = param.List(default=[Dimension('z')], bounds=(1, 1))

    group = param.String(default='Contours')


class Image(_Element, Dataset):
    """
    Image represents a 2D array of some quantity with
    some associated coordinates.
    """

    kdims = param.List(default=[Dimension('x'), Dimension('y')])

    vdims = param.List(default=[Dimension('z')], bounds=(1, 1))

    group = param.String(default='Image')


class Text(HVText, _Element):
    """
    An annotation containing some text at an x, y coordinate
    along with a coordinate reference system.
    """
