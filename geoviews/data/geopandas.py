from __future__ import absolute_import

import sys
import warnings

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
    def geo_column(cls, data):
        from geopandas import GeoSeries
        col = 'geometry'
        if col in data and isinstance(data[col], GeoSeries):
            return col
        cols = [c for c in data.columns if isinstance(data[c], GeoSeries)]
        if not cols:
            raise ValueError('No geometry column found in geopandas.DataFrame, '
                             'use the PandasInterface instead.')
        return cols[0]

    @classmethod
    def init(cls, eltype, data, kdims, vdims):
        import pandas as pd
        from geopandas import GeoDataFrame, GeoSeries

        if isinstance(data, GeoSeries):
            data = data.to_frame()
        if isinstance(data, list):
            if all(isinstance(d, geom_types) for d in data):
                data = [{'geometry': d} for d in data]
            if all('geometry' in d and isinstance(d['geometry'], geom_types) for d in data):
                data = GeoDataFrame(data)
        elif not isinstance(data, GeoDataFrame):
            raise ValueError("GeoPandasInterface only support geopandas DataFrames.")
        elif 'geometry' not in data:
            cls.geo_column(data)
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
        col = cls.geo_column(dataset.data)
        for geom in dataset.data[col]:
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
        col = cls.geo_column(dataset.data)
        for geom in dataset.data[col]:
            if isinstance(geom, Polygon) and geom.interiors:
                holes.append([[geom_to_array(h) for h in geom.interiors]])
            elif isinstance(geom, MultiPolygon):
                holes += [[[geom_to_array(h) for h in g.interiors] for g in geom]]
            else:
                holes.append([[]])
        return holes


    @classmethod
    def select(cls, dataset, selection_mask=None, **selection):
        if cls.geom_dims(dataset):
            df = cls.shape_mask(dataset, selection)
        else:
            df = dataset.data
        if not selection:
            return df
        elif selection_mask is None:
            selection_mask = cls.select_mask(dataset, selection)
        indexed = cls.indexed(dataset, selection)
        df = df.iloc[selection_mask]
        if indexed and len(df) == 1 and len(dataset.vdims) == 1:
            return df[dataset.vdims[0].name].iloc[0]
        return df

    @classmethod
    def shape_mask(cls, dataset, selection):
        xdim, ydim = cls.geom_dims(dataset)
        xsel = selection.pop(xdim.name, None)
        ysel = selection.pop(ydim.name, None)
        if xsel is None and ysel is None:
            return dataset.data

        from shapely.geometry import box

        if xsel is None:
            x0, x1 = cls.range(dataset, xdim)
        elif isinstance(xsel, slice):
            x0, x1 = xsel.start, xsel.stop
        elif isinstance(xsel, tuple):
            x0, x1 = xsel
        else:
            raise ValueError("Only slicing is supported on geometries, %s "
                             "selection is of type %s."
                             % (xdim, type(xsel).__name__))

        if ysel is None:
            y0, y1 = cls.range(dataset, ydim)
        elif isinstance(ysel, slice):
            y0, y1 = ysel.start, ysel.stop
        elif isinstance(ysel, tuple):
            y0, y1 = ysel
        else:
            raise ValueError("Only slicing is supported on geometries, %s "
                             "selection is of type %s."
                             % (ydim, type(ysel).__name__))

        bounds = box(x0, y0, x1, y1)
        col = cls.geo_column(dataset.data)
        df = dataset.data.copy()
        df[col] = df[col].intersection(bounds)
        return df[df[col].area > 0]

    @classmethod
    def select_mask(cls, dataset, selection):
        mask = np.ones(len(dataset.data), dtype=np.bool)
        for dim, k in selection.items():
            if isinstance(k, tuple):
                k = slice(*k)
            arr = dataset.data[dim].values
            if isinstance(k, slice):
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', r'invalid value encountered')
                    if k.start is not None:
                        mask &= k.start <= arr
                    if k.stop is not None:
                        mask &= arr < k.stop
            elif isinstance(k, (set, list)):
                iter_slcs = []
                for ik in k:
                    with warnings.catch_warnings():
                        warnings.filterwarnings('ignore', r'invalid value encountered')
                        iter_slcs.append(arr == ik)
                mask &= np.logical_or.reduce(iter_slcs)
            elif callable(k):
                mask &= k(arr)
            else:
                index_mask = arr == k
                if dataset.ndims == 1 and np.sum(index_mask) == 0:
                    data_index = np.argmin(np.abs(arr - k))
                    mask = np.zeros(len(dataset), dtype=np.bool)
                    mask[data_index] = True
                else:
                    mask &= index_mask
        return mask

    @classmethod
    def geom_dims(cls, dataset):
        return [d for d in dataset.kdims + dataset.vdims
                if d.name not in dataset.data]

    @classmethod
    def dimension_type(cls, dataset, dim):
        col = cls.geo_column(dataset.data)
        arr = geom_to_array(dataset.data[col].iloc[0])
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
            col = cls.geo_column(dataset.data)
            idx = geom_dims.index(dim)
            bounds = dataset.data[col].bounds
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
        col = cls.geo_column(dataset.data)
        length = sum([geom_length(g) for g in dataset.data[col]])
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
    def values(cls, dataset, dimension, expanded=True, flat=True, compute=True, keep_index=False):
        dimension = dataset.get_dimension(dimension)
        geom_dims = dataset.interface.geom_dims(dataset)
        data = dataset.data
        if dimension not in geom_dims and not expanded:
            data = data[dimension.name]
            return data if keep_index else data.values
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
        col = cls.geo_column(dataset.data)
        arr = geom_to_array(row[col])
        d = {(xdim.name, ydim.name): arr}
        d.update({vd.name: row[vd.name] for vd in dataset.vdims})
        ds = dataset.clone(d, datatype=['dictionary'])
        for i, row in dataset.data.iterrows():
            if datatype == 'geom':
                objs.append(row[col])
                continue
            geom = row[col]
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
