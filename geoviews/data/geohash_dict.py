"""
Implements a data Interface to render Geohashes as polygons.
"""
import sys

from holoviews.core.data import Interface, MultiInterface
from holoviews.core.util import unicode
from holoviews.element import Path

from ..util import geohash_to_polygon
from .geom_dict import GeomDictInterface


class GeohashInterface(GeomDictInterface):

    datatype = 'geohash'

    _geom_column = 'geohash'

    @classmethod
    def applies(cls, obj):
        if 'shapely' not in sys.modules:
            return False
        return (isinstance(obj, cls.types) and cls._geom_column in obj
                 and isinstance(obj[cls._geom_column], (str, unicode)))

    
    @classmethod
    def validate(cls, dataset, validate_vdims):
        GeomDictInterface.validate(dataset, validate_vdims)
        try:
            import geohash
        except:
            raise ImportError("python-geohash library required for "
                              "geohash support.")

    @classmethod
    def get_geom(cls, data):
        return geohash_to_polygon(data[cls._geom_column])


MultiInterface.subtypes.insert(1, 'geohash')
Interface.register(GeohashInterface)
Path.datatype = ['geohash']+Path.datatype
