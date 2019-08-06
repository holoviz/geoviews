import sys
from collections import OrderedDict

import numpy as np
from holoviews.core.data import Interface, DictInterface, MultiInterface
from holoviews.core.dimension import OrderedDict as cyODict, dimension_name
from holoviews.core.util import isscalar

from ..util import geom_types, geom_to_array, geom_length


class GeomDictInterface(DictInterface):

    datatype = 'geom_dictionary'

    @classmethod
    def applies(cls, obj):
        if 'shapely' not in sys.modules:
            return False
        return ((isinstance(obj, cls.types) and 'geometry' in obj
                 and isinstance(obj['geometry'], geom_types)) or
                isinstance(obj, geom_types))

    @classmethod
    def init(cls, eltype, data, kdims, vdims):
        odict_types = (OrderedDict, cyODict)
        if kdims is None:
            kdims = eltype.kdims
        if vdims is None:
            vdims = eltype.vdims

        dimensions = [dimension_name(d) for d in kdims + vdims]
        if isinstance(data, geom_types):
            data = {'geometry': data}

        if not cls.applies(data):
            raise ValueError("GeomDictInterface only handles dictionary types "
                             "containing a 'geometry' key and shapely geometry "
                             "value.")

        unpacked = []
        for d, vals in data.items():
            if isinstance(d, tuple):
                vals = np.asarray(vals)
                if vals.shape == (0,):
                    for sd in d:
                        unpacked.append((sd, np.array([], dtype=vals.dtype)))
                elif not vals.ndim == 2 and vals.shape[1] == len(d):
                    raise ValueError("Values for %s dimensions did not have "
                                     "the expected shape.")
                else:
                    for i, sd in enumerate(d):
                        unpacked.append((sd, vals[:, i]))
            elif d not in dimensions:
                unpacked.append((d, vals))
            else:
                if not isscalar(vals):
                    vals = np.asarray(vals)
                    if not vals.ndim == 1 and d in dimensions:
                        raise ValueError('DictInterface expects data for each column to be flat.')
                unpacked.append((d, vals))

        if not cls.expanded([vs for d, vs in unpacked if d in dimensions and not isscalar(vs)]):
            raise ValueError('DictInterface expects data to be of uniform shape.')
        if isinstance(data, odict_types):
            data.update(unpacked)
        else:
            data = OrderedDict(unpacked)

        return data, {'kdims':kdims, 'vdims':vdims}, {}

    @classmethod
    def validate(cls, dataset, validate_vdims):
        assert len([d for d in dataset.kdims + dataset.vdims
                    if d.name not in dataset.data]) == 2

    @classmethod
    def dtype(cls, dataset, dimension):
        name = dataset.get_dimension(dimension, strict=True).name
        if name not in dataset.data:
            return np.dtype('float') # Geometry dimension
        return super(GeomDictInterface, cls).dtype(dataset, dimension)

    @classmethod
    def has_holes(cls, dataset):
        from shapely.geometry import Polygon, MultiPolygon
        geom = dataset.data['geometry']
        if isinstance(geom, Polygon) and geom.interiors:
            return True
        elif isinstance(geom, MultiPolygon):
            for g in geom:
                if isinstance(g, Polygon) and g.interiors:
                    return True
        return False

    @classmethod
    def holes(cls, dataset):
        from shapely.geometry import Polygon, MultiPolygon
        geom = dataset.data['geometry']
        if isinstance(geom, Polygon):
            return [[[geom_to_array(h) for h in geom.interiors]]]
        elif isinstance(geom, MultiPolygon):
            return [[[geom_to_array(h) for h in g.interiors] for g in geom]]
        return []

    @classmethod
    def dimension_type(cls, dataset, dim):
        name = dataset.get_dimension(dim, strict=True).name
        if name in cls.geom_dims(dataset):
            return float
        values = dataset.data[name]
        return type(values) if isscalar(values) else values.dtype.type

    @classmethod
    def range(cls, dataset, dim):
        dim = dataset.get_dimension(dim)
        geom_dims = cls.geom_dims(dataset)
        if dim in geom_dims:
            bounds = dataset.data['geometry'].bounds
            if not bounds:
                return np.nan, np.nan
            elif geom_dims.index(dim) == 0:
                return bounds[0], bounds[2]
            else:
                return bounds[1], bounds[3]
        else:
            return DictInterface.range(dataset, dim)

    @classmethod
    def length(cls, dataset):
        return geom_length(dataset.data['geometry'])

    @classmethod
    def geom_dims(cls, dataset):
        return [d for d in dataset.kdims + dataset.vdims
                if d.name not in dataset.data]

    @classmethod
    def values(cls, dataset, dim, expanded=True, flat=True, compute=True):
        d = dataset.get_dimension(dim)
        geom_dims = cls.geom_dims(dataset)
        if d in geom_dims:
            g = dataset.data['geometry']
            if not g:
                return np.array([])
            array = geom_to_array(g)
            idx = geom_dims.index(d)
            return array[:, idx]
        return DictInterface.values(dataset, dim, expanded, flat)

    @classmethod
    def select(cls, dataset, selection_mask=None, **selection):
        raise NotImplementedError('select operation not implemented on geometries')

    @classmethod
    def iloc(cls, dataset, index):
        raise NotImplementedError('iloc operation not implemented for geometries.')

    @classmethod
    def sample(cls, dataset, samples=[]):
        raise NotImplementedError('sampling operation not implemented for geometries.')

    @classmethod
    def aggregate(cls, dataset, kdims, function, **kwargs):
        raise NotImplementedError('aggregate operation not implemented for geometries.')

    @classmethod
    def concat(cls, datasets, dimensions, vdims):
        raise NotImplementedError('concat operation not implemented for geometries.')


MultiInterface.subtypes.insert(0, 'geom_dictionary')
Interface.register(GeomDictInterface)
