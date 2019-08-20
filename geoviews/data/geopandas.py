from __future__ import absolute_import

import sys

import numpy as np

from holoviews.core.data import Dataset, Interface, MultiInterface
from holoviews.core.data.interface  import DataError
from holoviews.core.dimension import dimension_name
from holoviews.element import Path

from ..util import geom_to_array, geom_types, geom_length


class GeoPandasInterface(MultiInterface):

    types = ()

    datatype = 'geodataframe'

    multi = True

    @classmethod
    def loaded(cls):
        return 'geopandas' in sys.modules

    @classmethod
    def applies(cls, obj):
        if not cls.loaded():
            return False
        from geopandas import GeoDataFrame
        return isinstance(obj, GeoDataFrame)

    @classmethod
    def init(cls, eltype, data, kdims, vdims):
        import pandas as pd
        from geopandas import GeoDataFrame

        if isinstance(data, list):
            if all(isinstance(d, geom_types) for d in data):
                data = [{'geometry': d} for d in data]
            if all('geometry' in d and isinstance(d['geometry'], geom_types) for d in data):
                data = GeoDataFrame(data)
        elif not isinstance(data, GeoDataFrame):
            raise ValueError("GeoPandasInterface only support geopandas DataFrames.")
        elif 'geometry' not in data:
            raise ValueError("GeoPandas dataframe must contain geometry column, "
                             "to plot non-geographic data use pandas DataFrame.", cls)
        if kdims is None:
            kdims = eltype.kdims

        if vdims is None:
            vdims = eltype.vdims

        index_names = data.index.names if isinstance(data, pd.DataFrame) else [data.index.name]
        if index_names == [None]:
            index_names = ['index']

        for kd in kdims+vdims:
            kd = dimension_name(kd)
            if kd in data.columns:
                continue
            if any(kd == ('index' if name is None else name)
                   for name in index_names):
                data = data.reset_index()
                break

        shp_types = {gt[5:] if 'Multi' in gt else gt for gt in data.geom_type}
        if len(shp_types) > 1:
            raise DataError('The GeopandasInterface can only read dataframes which '
                            'share a common geometry type, found %s types.' % shp_types,
                            cls)

        return data, {'kdims': kdims, 'vdims': vdims}, {}

    @classmethod
    def validate(cls, dataset, vdims=True):
        dim_types = 'key' if vdims else 'all'
        geom_dims = cls.geom_dims(dataset)
        if len(geom_dims) != 2:
            raise DataError('Expected %s instance to declare two key '
                            'dimensions corresponding to the geometry '
                            'coordinates but %d dimensions were found '
                            'which did not refer to any columns.'
                            % (type(dataset).__name__, len(geom_dims)), cls)
        not_found = [d.name for d in dataset.dimensions(dim_types)
                     if d not in geom_dims and d.name not in dataset.data]
        if not_found:
            raise DataError("Supplied data does not contain specified "
                             "dimensions, the following dimensions were "
                             "not found: %s" % repr(not_found), cls)


    @classmethod
    def dtype(cls, dataset, dimension):
        name = dataset.get_dimension(dimension, strict=True).name
        if name not in dataset.data:
            return np.dtype('float') # Geometry dimension
        return dataset.data[name].dtype


    @classmethod
    def has_holes(cls, dataset):
        from shapely.geometry import Polygon, MultiPolygon
        for geom in dataset.data.geometry:
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
        holes = []
        for geom in dataset.data.geometry:
            if isinstance(geom, Polygon) and geom.interiors:
                holes.append([[geom_to_array(h) for h in geom.interiors]])
            elif isinstance(geom, MultiPolygon):
                holes += [[[geom_to_array(h) for h in g.interiors] for g in geom]]
            else:
                holes.append([[]])
        return holes

    @classmethod
    def geom_dims(cls, dataset):
        return [d for d in dataset.kdims + dataset.vdims
                if d.name not in dataset.data]

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
        dim = dataset.get_dimension(dim)
        geom_dims = cls.geom_dims(dataset)
        if dim in geom_dims:
            idx = geom_dims.index(dim)
            bounds = dataset.data.geometry.bounds
            if idx == 0:
                return bounds.minx.min(), bounds.maxx.max()
            else:
                return bounds.miny.min(), bounds.maxy.max()
        else:
            vals = dataset.data[dim.name]
            return vals.min(), vals.max()

    @classmethod
    def aggregate(cls, columns, dimensions, function, **kwargs):
        raise NotImplementedError

    @classmethod
    def groupby(cls, columns, dimensions, container_type, group_type, **kwargs):
        from holoviews.core.data import PandasInterface
        return PandasInterface.groupby(columns, dimensions, container_type, group_type, **kwargs)

    @classmethod
    def reindex(cls, dataset, kdims=None, vdims=None):
        return dataset.data

    @classmethod
    def sample(cls, columns, samples=[]):
        raise NotImplementedError

    @classmethod
    def shape(cls, dataset):
        from holoviews.core.data import PandasInterface
        return PandasInterface.shape(dataset)

    @classmethod
    def length(cls, dataset):
        from holoviews.core.data import PandasInterface
        length = sum([geom_length(g) for g in dataset.data.geometry])
        geom_type = dataset.data.geom_type.iloc[0]
        if geom_type != 'Point':
            length += (PandasInterface.length(dataset)-1)
        return length

    @classmethod
    def nonzero(cls, dataset):
        return bool(cls.length(dataset))

    @classmethod
    def redim(cls, dataset, dimensions):
        from holoviews.core.data import PandasInterface
        return PandasInterface.redim(dataset, dimensions)

    @classmethod
    def select(cls, dataset, selection_mask=None, **selection):
        from holoviews.core.data import PandasInterface
        return PandasInterface.select(dataset, selection_mask, **selection)

    @classmethod
    def values(cls, dataset, dimension, expanded=True, flat=True, compute=True):
        dimension = dataset.get_dimension(dimension)
        geom_dims = dataset.interface.geom_dims(dataset)
        data = dataset.data
        if dimension not in geom_dims and not expanded:
            return data[dimension.name].values
        elif not len(data):
            return np.array([])

        values = []
        geom_type = data.geom_type.iloc[0]
        ds = dataset.clone(data.iloc[0].to_dict(), datatype=['geom_dictionary'])
        for i, row in data.iterrows():
            ds.data = row.to_dict()
            values.append(ds.interface.values(ds, dimension))
            if geom_type != 'Point':
                values.append([np.NaN])
        values = values if geom_type == 'Point' else values[:-1]
        if len(values) == 1:
            return values[0]
        elif not values:
            return np.array([])
        else:
            return np.concatenate(values)

    @classmethod
    def split(cls, dataset, start, end, datatype, **kwargs):
        objs = []
        xdim, ydim = dataset.kdims[:2]
        if not len(dataset.data):
            return []
        row = dataset.data.iloc[0]
        arr = geom_to_array(row['geometry'])
        d = {(xdim.name, ydim.name): arr}
        d.update({vd.name: row[vd.name] for vd in dataset.vdims})
        ds = dataset.clone(d, datatype=['dictionary'])
        for i, row in dataset.data.iterrows():
            if datatype == 'geom':
                objs.append(row['geometry'])
                continue
            geom = row.geometry
            arr = geom_to_array(geom)
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
Dataset.datatype = ['geodataframe']+Dataset.datatype
Path.datatype = ['geodataframe']+Path.datatype
