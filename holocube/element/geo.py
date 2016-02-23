import param

import iris
from cartopy import crs
from cartopy.feature import Feature
from cartopy.io.img_tiles import GoogleTiles
from holoviews.core import Element2D, Dimension
from holoviews.element import Points

from .cube  import Cube


class GeoElement(Element2D):
    """
    Baseclass for Element2D types with associated cartopy coordinate
    reference system.
    """

    _abstract = True
    
    crs = param.ClassSelector(class_=crs.CRS)
    
    def __init__(self, data, **kwargs):
        crs = None
        if isinstance(data, iris.cube.Cube):
            coord_sys = data.coord_system()
            if hasattr(coord_sys, 'as_cartopy_crs'):
                crs = coord_sys.as_cartopy_crs()
        elif isinstance(data, (Feature, GoogleTiles)):
            crs = data.crs

        supplied_crs = kwargs.get('crs', None)
        if supplied_crs and crs and crs != supplied_crs:
            raise ValueError('Supplied coordinate reference system must match crs of the data.')
        elif crs:
            kwargs['crs'] = crs
        super(GeoElement, self).__init__(data, **kwargs)


class GeoPoints(Points, GeoElement):
    
    group = param.String(default='GeoPoints')


class GeoFeature(GeoElement):
    
    group = param.String(default='GeoFeature')
    

class WMTS(GeoElement):
    
    group = param.String(default='WMTS')
    
    
class GeoTiles(GeoElement):
    
    group = param.String(default='GeoTiles')
    
    zoom = param.Integer(default=8)


class GeoContour(Cube, GeoElement):
    
    group = param.String(default='GeoContour')

    levels = param.ClassSelector(default=5, class_=(int, list))

    
class GeoImage(Cube, GeoElement):

    group = param.String(default='GeoImage')
