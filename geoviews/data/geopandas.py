import numpy as np
import geopandas as gpd

from holoviews.core.data import Interface, MultiInterface
from holoviews.core.util import max_range
from holoviews.element import Path

from ..util import geom_to_array


class GeoPandasInterface(MultiInterface):

    types = (gpd.GeoDataFrame,)

    datatype = 'geodataframe'

    multi = True

    @classmethod
    def init(cls, eltype, data, kdims, vdims):
        dims = {'kdims': eltype.kdims, 'vdims': eltype.vdims}
        if kdims is not None:
            dims['kdims'] = kdims
        if vdims is not None:
            dims['vdims'] = vdims
        return data, dims, {}

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
    def split(cls, dataset, start, end, datatype, **kwargs):
        objs = []
        xdim, ydim = dataset.kdims[:2]
        row = dataset.data.iloc[0]
        arr = geom_to_array(row['geometry'])
        d = {(xdim.name, ydim.name): arr}
        ds = dataset.clone(d, datatype=['dictionary'])
        for i, row in dataset.data.iterrows():
            if datatype == 'geom':
                objs.append(row['geometry'])
                continue
            arr = geom_to_array(row['geometry'])
            d = {xdim.name: arr[:, 0], ydim.name: arr[:, 1]}
            d.update({vd.name: row[vd.name] for vd in dataset.vdims})
            ds.data = d
            if datatype == 'array':
                obj = ds.array(**kwargs)
            elif datatype == 'dataframe':
                obj = ds.dframe(**kwargs)
            elif datatype == 'columns':
                obj = ds.columns(**kwargs)
            elif datatype is None:
                obj = ds.clone()
            else:
                raise ValueError("%s datatype not support" % datatype)
            objs.append(obj)
        return objs


Interface.register(GeoPandasInterface)
Path.datatype += ['geodataframe']
