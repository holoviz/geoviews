import sys
from collections import OrderedDict, defaultdict
try:
    import itertools.izip as zip
except ImportError:
    pass

import numpy as np


from holoviews.core.data import Interface, DictInterface, MultiInterface
from holoviews.core.dimension import OrderedDict as cyODict, dimension_name
from holoviews.core.util import isscalar

from ..util import geom_types, geom_to_array


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
    def validate(cls, dataset):
        assert len([d for d in dataset.kdims + dataset.vdims
                    if d.name not in dataset.data]) == 2

    @classmethod
    def dimension_type(cls, dataset, dim):
        name = dataset.get_dimension(dim, strict=True).name
        if name in cls.geom_dims(dataset):
            return float
        values = dataset.data[name]
        return type(values) if isscalar(values) else values.dtype.type

    @classmethod
    def redim(cls, dataset, dimensions):
        pass

    @classmethod
    def length(cls, dataset):
        return len(geom_to_array(dataset.data['geometry']))

    @classmethod
    def geom_dims(cls, dataset):
        return [d for d in dataset.kdims + dataset.vdims
                if d.name not in dataset.data]
    
    @classmethod
    def xdim(cls, dataset):
        return [d for d in dataset.kdims + dataset.vdims
                if d.name not in dataset.data][0]

    @classmethod
    def ydim(cls, dataset):
        return [d for d in dataset.kdims + dataset.vdims
                if d.name not in dataset.data][1]

    @classmethod
    def values(cls, dataset, dim, expanded=True, flat=True):
        d = dataset.get_dimension(dim)
        array = geom_to_array(dataset.data['geometry'])
        if d is cls.xdim(dataset):
            return array[:, 0]
        elif d is cls.ydim(dataset):
            return array[:, 1]
        return DictInterface.values(dataset, dim, expanded, flat)

    @classmethod
    def validate(cls, dataset, vdims=True):
        pass

    @classmethod
    def iloc(cls, dataset, index):
        raise NotImplementedError()

    @classmethod
    def sample(cls, dataset, samples=[]):
        raise NotImplementedError()

    @classmethod
    def aggregate(cls, dataset, kdims, function, **kwargs):
        raise NotImplementedError()

    @classmethod
    def concat(cls, datasets, dimensions, vdims):
        raise NotImplementedError()

MultiInterface.subtypes.append('geom_dictionary')
Interface.register(GeomDictInterface)
