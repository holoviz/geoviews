import numpy as np
import geopandas as gpd

from holoviews.core.data import Interface, MultiInterface, PandasInterface
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
        not_found = [d for d in dataset.dimensions(label='name')[2:]
                     if d not in dataset.data.columns]
        if not_found:
            raise ValueError("Supplied data does not contain specified "
                             "dimensions, the following dimensions were "
                             "not found: %s" % repr(not_found))

    @classmethod
    def dimension_type(cls, dataset, dim):
        arr = geom_to_array(dataset.data.geometry.iloc[0])
        ds = dataset.clone(arr, datatype=cls.subtypes, vdims=[])
        return ds.interface.dimension_type(ds, dim)

    @classmethod
    def isscalar(cls, dataset, dim):
        """
        Tests if dimension is scalar in each subpath.
        """
        idx = dataset.get_dimension_index(dim)
        return idx not in [0, 1]

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
        dimension = dataset.get_dimension(dimension)
        idx = dataset.get_dimension_index(dimension)
        data = dataset.data
        if idx not in [0, 1] and not expanded:
            return data[dimension.name].values
        values = []
        columns = list(data.columns)
        arr = geom_to_array(data.geometry.iloc[0])
        ds = dataset.clone(arr, datatype=cls.subtypes, vdims=[])
        for i, d in enumerate(data.geometry):
            arr = geom_to_array(d)
            if idx in [0, 1]:
                ds.data = arr
                values.append(ds.interface.values(ds, dimension))
            else:
                arr = np.full(len(arr), data.iloc[i, columns.index(dimension.name)])
                values.append(arr)
            values.append([np.NaN])
        return np.concatenate(values[:-1]) if values else np.array([])

    @classmethod
    def split(cls, dataset, start, end, datatype, **kwargs):
        objs = []
        xdim, ydim = dataset.kdims[:2]
        row = dataset.data.iloc[0]
        arr = geom_to_array(row['geometry'])
        d = {(xdim.name, ydim.name): arr}
        d.update({vd.name: row[vd.name] for vd in dataset.vdims})
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
