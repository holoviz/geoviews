import numpy as np
import geopandas as gpd

from holoviews.core.data import Interface, MultiInterface
from holoviews.core.util import max_range
from holoviews.element import Path

from ..util import geom_to_array


class GeoPandasInterface(MultiInterface):

    types = (gpd.GeoDataFrame,)

    datatype = 'geodataframe'

    @classmethod
    def init(cls, eltype, data, kdims, vdims):
        return data, {'kdims': eltype.kdims, 'vdims': []}, {}

    @classmethod
    def validate(cls, dataset):
        pass

    @classmethod
    def dimension_type(cls, dataset, dim):
        arr = geom_to_array(dataset.data.geometry.iloc[0])
        ds = dataset.clone(arr, datatype=cls.subtypes, vdims=[])
        return ds.interface.dimension_type(ds, dim)

    @classmethod
    def range(cls, dataset, dim):
        dim = dataset.get_dimension_index(dim)
        if dim in [0, 1]:
            ranges = []
            arr = geom_to_array(dataset.data.geometry.iloc[0])
            ds = dataset.clone(arr, datatype=cls.subtypes, vdims=[])
            for d in dataset.data.geometry:
                ds.data = geom_to_array(d)
                ranges.append(ds.interface.range(ds, dim))
            return max_range(ranges)
        else:
            dim = dataset.get_dimension(dim)
            vals = dataset.data[dim.name]
            return vals.min(), vals.max()
        
    @classmethod
    def aggregate(cls, columns, dimensions, function, **kwargs):
        raise NotImplementedError

    @classmethod
    def groupby(cls, columns, dimensions, container_type, group_type, **kwargs):
        raise NotImplementedError

    @classmethod
    def sample(cls, columns, samples=[]):
        raise NotImplementedError

    @classmethod
    def shape(cls, dataset):
        rows, cols = 0, 0
        arr = geom_to_array(dataset.data.geometry.iloc[0])
        ds = dataset.clone(arr, datatype=cls.subtypes, vdims=[])
        for d in dataset.data.geometry:
            ds.data = geom_to_array(d)
            r, cols = ds.interface.shape(ds)
            rows += r
        return rows+len(dataset.data)-1, cols

    @classmethod
    def length(cls, dataset):
        length = 0
        arr = geom_to_array(dataset.data.geometry.iloc[0])
        ds = dataset.clone(arr, datatype=cls.subtypes, vdims=[])
        for d in dataset.data.geometry:
            ds.data = geom_to_array(d)
            length += ds.interface.length(ds)
        return length+len(dataset.data)-1

    @classmethod
    def nonzero(cls, dataset):
        return bool(cls.length(dataset))

    @classmethod
    def redim(cls, dataset, dimensions):
        new_data = []
        arr = geom_to_array(dataset.data.geometry.iloc[0])
        ds = dataset.clone(arr, datatype=cls.subtypes, vdims=[])
        for d in dataset.data.geometry:
            ds.data = geom_to_array(d)
            new_data.append(ds.interface.redim(ds, dimensions))
        return new_data

    @classmethod
    def values(cls, dataset, dimension, expanded, flat):
        values = []
        arr = geom_to_array(dataset.data.geometry.iloc[0])
        ds = dataset.clone(arr, datatype=cls.subtypes, vdims=[])
        for d in dataset.data.geometry:
            ds.data = geom_to_array(d)
            values.append(ds.interface.values(ds, dimension))
            values.append([np.NaN])
        return np.concatenate(values[:-1]) if values else []

    @classmethod
    def split(cls, dataset, start, end):
        objs = []
        for d in dataset.data.geometry:
            arr = geom_to_array(d)
            objs.append(dataset.clone(arr, datatype=cls.subtypes, vdims=[]))
        return objs


Interface.register(GeoPandasInterface)
Path.datatype += ['geodataframe']
