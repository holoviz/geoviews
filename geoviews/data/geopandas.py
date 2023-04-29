import sys
import warnings

from collections import defaultdict

import numpy as np
import pandas as pd

from holoviews.core.util import isscalar, unique_iterator, unique_array
from holoviews.core.data import Dataset, Interface, MultiInterface, PandasAPI
from holoviews.core.data.interface import DataError
from holoviews.core.data import PandasInterface
from holoviews.core.data.spatialpandas import get_value_array
from holoviews.core.dimension import dimension_name
from holoviews.element import Path

from ..util import asarray, geom_to_array, geom_types, geom_length
from .geom_dict import geom_from_dict


class GeoPandasInterface(PandasAPI, MultiInterface):

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
        from geopandas import GeoDataFrame, GeoSeries
        return isinstance(obj, (GeoDataFrame, GeoSeries))

    @classmethod
    def geo_column(cls, data):
        try:
            return data.geometry.name
        except AttributeError:
            if len(data):
                raise ValueError('No geometry column found in geopandas.DataFrame, '
                                 'use the PandasInterface instead.')
            return None

    @classmethod
    def init(cls, eltype, data, kdims, vdims):
        import pandas as pd
        from geopandas import GeoDataFrame, GeoSeries

        if kdims is None:
            kdims = eltype.kdims

        if isinstance(data, GeoSeries):
            data = data.to_frame()

        if isinstance(data, list):
            if all(isinstance(d, geom_types) for d in data):
                data = [{'geometry': d} for d in data]
            if all(isinstance(d, dict) and 'geometry' in d and isinstance(d['geometry'], geom_types)
                   for d in data):
                data = GeoDataFrame(data)
            if not isinstance(data, GeoDataFrame):
                vdims = vdims or eltype.vdims
                data = from_multi(eltype, data, kdims, vdims)
        elif not isinstance(data, GeoDataFrame):
            raise ValueError("GeoPandasInterface only support geopandas "
                             "DataFrames not %s." % type(data))
        elif 'geometry' not in data:
            cls.geo_column(data)

        if vdims is None:
            vdims = [col for col in data.columns if not isinstance(data[col], GeoSeries)]

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

        try:
            shp_types = {gt[5:] if 'Multi' in gt else gt for gt in data.geom_type}
        except Exception:
            shp_types = []
        if len(shp_types) > 1:
            raise DataError('The GeopandasInterface can only read dataframes which '
                            'share a common geometry type, found %s types.' % shp_types,
                            cls)

        return data, {'kdims': kdims, 'vdims': vdims}, {}

    @classmethod
    def validate(cls, dataset, vdims=True):
        dim_types = 'key' if vdims else 'all'
        geom_dims = cls.geom_dims(dataset)
        if len(geom_dims) > 0 and len(geom_dims) != 2:
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
                for g in geom.geoms:
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
                holes += [[[geom_to_array(h) for h in g.interiors] for g in geom.geoms]]
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
            raise ValueError(
                f"Only slicing is supported on geometries, {xdim} "
                f"selection is of type {type(xsel).__name__}."
            )

        if ysel is None:
            y0, y1 = cls.range(dataset, ydim)
        elif isinstance(ysel, slice):
            y0, y1 = ysel.start, ysel.stop
        elif isinstance(ysel, tuple):
            y0, y1 = ysel
        else:
            raise ValueError(
                f"Only slicing is supported on geometries, {ydim} "
                f"selection is of type {type(ysel).__name__}."
            )

        bounds = box(x0, y0, x1, y1)
        col = cls.geo_column(dataset.data)
        df = dataset.data.copy()
        df[col] = df[col].intersection(bounds)
        return df[df[col].area > 0]

    @classmethod
    def select_mask(cls, dataset, selection):
        mask = np.ones(len(dataset.data), dtype=np.bool_)
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
                    mask = np.zeros(len(dataset), dtype=np.bool_)
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
        geom_dims = cls.geom_dims(dataset)
        if dim in geom_dims:
            return float
        elif len(dataset.data):
            return type(dataset.data[dim.name].iloc[0])
        else:
            return float

    @classmethod
    def isscalar(cls, dataset, dim, per_geom=False):
        """
        Tests if dimension is scalar in each subpath.
        """
        dim = dataset.get_dimension(dim)
        geom_dims = cls.geom_dims(dataset)
        if dim in geom_dims:
            return False
        elif per_geom:
            return all(isscalar(v) or len(list(unique_array(v))) == 1
                       for v in dataset.data[dim.name])
        dim = dataset.get_dimension(dim)
        return len(dataset.data[dim.name].unique()) == 1

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
    def add_dimension(cls, dataset, dimension, dim_pos, values, vdim):
        data = dataset.data.copy()
        geom_col = cls.geo_column(dataset.data)
        if dim_pos >= list(data.columns).index(geom_col):
            dim_pos -= 1
        if dimension.name not in data:
            data.insert(dim_pos, dimension.name, values)
        return data

    @classmethod
    def groupby(cls, dataset, dimensions, container_type, group_type, **kwargs):
        geo_dims = cls.geom_dims(dataset)
        if any(d in geo_dims for d in dimensions):
            raise DataError("GeoPandasInterface does not allow grouping "
                            "by geometry dimension.", cls)

        return PandasInterface.groupby(dataset, dimensions, container_type, group_type, **kwargs)

    @classmethod
    def reindex(cls, dataset, kdims=None, vdims=None):
        return dataset.data

    @classmethod
    def sample(cls, columns, samples=[]):
        raise NotImplementedError


    @classmethod
    def sort(cls, dataset, by=[], reverse=False):
        geo_dims = cls.geom_dims(dataset)
        if any(d in geo_dims for d in by):
            raise DataError("SpatialPandasInterface does not allow sorting "
                            "by geometry dimension.", cls)
        return PandasInterface.sort(dataset, by, reverse)

    @classmethod
    def shape(cls, dataset):
        return (cls.length(dataset), len(dataset.dimensions()))

    @classmethod
    def length(cls, dataset):
        geom_type = cls.geom_type(dataset)
        if geom_type != 'Point':
            return len(dataset.data)
        return sum([geom_length(g) for g in dataset.data.geometry])

    @classmethod
    def nonzero(cls, dataset):
        return bool(cls.length(dataset))

    @classmethod
    def redim(cls, dataset, dimensions):
        return PandasInterface.redim(dataset, dimensions)

    @classmethod
    def values(cls, dataset, dimension, expanded=True, flat=True, compute=True, keep_index=False):
        dimension = dataset.get_dimension(dimension)
        geom_dims = dataset.interface.geom_dims(dataset)
        data = dataset.data
        isgeom = (dimension in geom_dims)
        geom_col = cls.geo_column(dataset.data)
        is_points = cls.geom_type(dataset) == 'Point'
        if not len(data):
            dtype = float if isgeom else dataset.data[dimension.name].dtype
            return np.array([], dtype=dtype)

        col = cls.geo_column(dataset.data)
        if isgeom and keep_index:
            return data[col]
        elif not isgeom:
            return get_value_array(data, dimension, expanded, keep_index,
                                   geom_col, is_points, geom_length)
            column = data[dimension.name]
            if not expanded or keep_index or not len(data):
                return column if keep_index else column.values
            else:
                arrays = []
                for i, geom in enumerate(data[col]):
                    length = geom_length(geom)
                    arrays.append(np.full(length, column.iloc[i]))
                return np.concatenate(arrays) if len(arrays) > 1 else arrays[0]

        # There's special handling of the geometry column in the event
        # that it's not name `geometry` in the geodataframe. Since we
        # serialize each row to a geom_dictionary that requires a
        # `geometry` key.
        dict_data = data.iloc[0].to_dict()
        default_geo_name = new_geo_col_name= 'geometry'
        geom_col = data.geometry.name
        if geom_col != default_geo_name:
            if default_geo_name in dict_data:
                # When there's a 'geometry' column that is not THE geometry column,
                # we create a temporary name that will be used to 1) create a new
                # dimension in the dataset and 2) add the data of this dimension
                # in the dict used to serialize each row of the geodataframe.
                while new_geo_col_name in dict_data:
                    new_geo_col_name += '_'

        if new_geo_col_name != default_geo_name:
            dict_data[new_geo_col_name] = dict_data.pop(default_geo_name)
            dataset = dataset.redim(**{default_geo_name: new_geo_col_name})

        dict_data['geometry'] = dict_data.pop(data.geometry.name)

        ds = dataset.clone(dict_data, datatype=['geom_dictionary'])
        values = []
        geom_type = data.geom_type.iloc[0]
        for i, row in data.iterrows():
            ds.data = row.to_dict()
            if new_geo_col_name != default_geo_name:
                ds.data[new_geo_col_name] = ds.data.pop(default_geo_name)
            ds.data['geometry'] = ds.data.pop(data.geometry.name)
            values.append(ds.interface.values(ds, dimension))
            if 'Point' not in geom_type and expanded:
                values.append([np.NaN])
        values = values if 'Point' in geom_type or not expanded else values[:-1]
        if not values:
            return np.array([])
        elif not expanded:
            array = np.empty(len(values), dtype=object)
            array[:] = values
            return array
        elif len(values) == 1:
            return values[0]
        else:
            return np.concatenate(values)

    @classmethod
    def iloc(cls, dataset, index):
        from geopandas import GeoSeries
        from shapely.geometry import MultiPoint
        rows, cols = index
        geom_dims = cls.geom_dims(dataset)
        geom_col = cls.geo_column(dataset.data)
        scalar = False
        columns = list(dataset.data.columns)
        if isinstance(cols, slice):
            cols = [d.name for d in dataset.dimensions()][cols]
        elif np.isscalar(cols):
            scalar = np.isscalar(rows)
            cols = [dataset.get_dimension(cols).name]
        else:
            cols = [dataset.get_dimension(d).name for d in index[1]]
        if not all(d in cols for d in geom_dims):
            raise DataError("Cannot index a dimension which is part of the "
                            "geometry column of a spatialpandas DataFrame.", cls)
        cols = list(unique_iterator([
            columns.index(geom_col) if c in geom_dims else columns.index(c) for c in cols
        ]))

        geom_type = dataset.data[geom_col].geom_type.iloc[0]
        if geom_type != 'MultiPoint':
            if scalar:
                return dataset.data.iloc[rows[0], cols[0]]
            elif isscalar(rows):
                rows = [rows]
            return dataset.data.iloc[rows, cols]

        geoms = dataset.data[geom_col]
        count = 0
        new_geoms, indexes = [], []
        for i, geom in enumerate(geoms):
            length = len(geom.geoms)
            if np.isscalar(rows):
                if count <= rows < (count+length):
                    new_geoms.append(geom.geoms[rows-count])
                    indexes.append(i)
                    break
            elif isinstance(rows, slice):
                if rows.start is not None and rows.start > (count+length):
                    continue
                elif rows.stop is not None and rows.stop < count:
                    break
                start = None if rows.start is None else max(rows.start - count, 0)
                stop = None if rows.stop is None else min(rows.stop - count, length)
                if rows.step is not None:
                    dataset.param.warning(".iloc step slicing currently not supported for"
                                          "the multi-tabular data format.")
                indexes.append(i)
                new_geoms.append(geom.geoms[start:stop])
            elif isinstance(rows, (list, set)):
                sub_rows = [(r-count) for r in rows if count <= r < (count+length)]
                if not sub_rows:
                    continue
                indexes.append(i)
                new_geoms.append(MultiPoint([geom.geoms[r] for r in sub_rows]))
            count += length

        new = dataset.data.iloc[indexes].copy()
        new[geom_col] = GeoSeries(new_geoms)
        return new

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
        geom_type = cls.geom_type(dataset)
        ds = dataset.clone([d], datatype=['multitabular'])
        for i, row in dataset.data.iterrows():
            if datatype == 'geom':
                objs.append(row[col])
                continue
            geom = row[col]
            gt = geom_type or get_geom_type(geom)

            arr = geom_to_array(geom)
            d = {xdim.name: arr[:, 0], ydim.name: arr[:, 1]}
            d.update({vd.name: row[vd.name] for vd in dataset.vdims})
            ds.data = [d]
            if datatype == 'array':
                obj = ds.array(**kwargs)
            elif datatype == 'dataframe':
                obj = ds.dframe(**kwargs)
            elif datatype in ('columns', 'dictionary'):
                d['geom_type'] = gt
                obj = d
            elif datatype is None:
                obj = ds.clone()
            else:
                raise ValueError("%s datatype not support" % datatype)
            objs.append(obj)
        return objs


def get_geom_type(geom):
    """Returns the HoloViews geometry type.

    Args:
        geom: A shapely geometry

    Returns:
        A string representing type of the geometry.
    """
    from shapely.geometry import (
        Point, LineString, Polygon, Ring, MultiPoint, MultiPolygon, MultiLineString
    )
    if isinstance(geom, (Point, MultiPoint)):
        return 'Point'
    elif isinstance(geom, (LineString, MultiLineString)):
        return 'Line'
    elif isinstance(geom, Ring):
        return 'Ring'
    elif isinstance(geom, (Polygon, MultiPolygon)):
        return 'Polygon'


def to_geopandas(data, xdim, ydim, columns=[], geom='point'):
    """Converts list of dictionary format geometries to spatialpandas line geometries.

    Args:
        data: List of dictionaries representing individual geometries
        xdim: Name of x-coordinates column
        ydim: Name of y-coordinates column
        ring: Whether the data represents a closed ring

    Returns:
        A spatialpandas.GeoDataFrame version of the data
    """
    from geopandas import GeoDataFrame
    from shapely.geometry import (
        Point, LineString, Polygon, MultiPoint, MultiPolygon, MultiLineString
    )
    poly = any('holes' in d for d in data) or geom == 'Polygon'
    if poly:
        single_type, multi_type = Polygon, MultiPolygon
    elif geom == 'Line':
        single_type, multi_type = LineString, MultiLineString
    else:
        single_type, multi_type = Point, MultiPoint

    converted = defaultdict(list)
    for geom_dict in data:
        geom_dict = dict(geom_dict)
        geom = geom_from_dict(geom_dict, xdim, ydim, single_type, multi_type)
        for c, v in geom_dict.items():
            converted[c].append(v)
        converted['geometry'].append(geom)

    return GeoDataFrame(converted, columns=['geometry']+columns)


def from_multi(eltype, data, kdims, vdims):
    """Converts list formats into geopandas.GeoDataFrame.

    Args:
        eltype: Element type to convert
        data: The original data
        kdims: The declared key dimensions
        vdims: The declared value dimensions

    Returns:
        A GeoDataFrame containing the data in the list based format.
    """

    from geopandas import GeoDataFrame

    new_data = []
    types = []
    xname, yname = (kd.name for kd in kdims[:2])
    for d in data:
        types.append(type(d))
        if isinstance(d, dict):
            d = {k: v if isscalar(v) else asarray(v) for k, v in d.items()}
            new_data.append(d)
            continue
        new_el = eltype(d, kdims, vdims)
        if new_el.interface is GeoPandasInterface:
            types[-1] = GeoDataFrame
            new_data.append(new_el.data)
            continue
        new_dict = {}
        for d in new_el.dimensions():
            if d in (xname, yname):
                scalar = False
            else:
                scalar = new_el.interface.isscalar(new_el, d)
            vals = new_el.dimension_values(d, not scalar)
            new_dict[d.name] = vals[0] if scalar else vals
        new_data.append(new_dict)
    if len(set(types)) > 1:
        raise DataError('Mixed types not supported')
    if new_data and types[0] is GeoDataFrame:
        data = pd.concat(new_data)
    else:
        columns = [d.name for d in kdims+vdims if d not in (xname, yname)]
        geom = GeoPandasInterface.geom_type(eltype)
        if not len(data):
            return GeoDataFrame([], columns=['geometry']+columns)
        data = to_geopandas(new_data, xname, yname, columns, geom)
    return data


Interface.register(GeoPandasInterface)
Dataset.datatype = Dataset.datatype+['geodataframe']
Path.datatype = Path.datatype+['geodataframe']
