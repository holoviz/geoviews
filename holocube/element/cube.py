import iris
from iris.util import guess_coord_axis
import numpy as np

import param
from holoviews.core.dimension import Dimension
from holoviews.core.data import DataColumns
from holoviews.core.ndmapping import (NdMapping, item_check,
                                      sorted_context)
from holoviews.core.spaces import HoloMap
from holoviews.core import util
from holoviews.element.tabular import Table


def get_date_format(coord):
    def date_formatter(val, pos=None):
        return coord.units.num2date(val)
    return date_formatter

def coord_to_dimension(coord):
    """
    Converts an iris coordinate to a HoloViews dimension.
    """
    kwargs = {}
    if coord.units.is_time_reference():
        kwargs['value_format'] = get_date_format(coord)
    else:
        kwargs['unit'] = str(coord.units)
    return Dimension(coord.name(), **kwargs)

def sort_coords(coord):
    """
    Sorts a list of DimCoords trying to ensure that
    dates and pressure levels appear first and the
    longitude and latitude appear last in the correct
    order.
    """
    order = {'T': -2, 'Z': -1, 'X': 1, 'Y': 2}
    axis = guess_coord_axis(coord)
    return (order.get(axis, 0), coord and coord.name())


class Cube(Table):
    """
    The Cube Element provides an interface to wrap and display
    :class:`Iris.cube.Cube` objects. The Cube automatically
    infers the key and value dimensions of the iris data
    and provides useful methods for accessing, grouping
    and slicing the data.
    """

    datatype = param.List(default=['cube'])

    group = param.String(default='Cube')



class CubeData(DataColumns):

    types = (iris.cube.Cube,)

    datatype = 'cube'

    @classmethod
    def reshape(cls, eltype, data, kdims, vdims):
        if not isinstance(data, iris.cube.Cube):
            raise TypeError('Cube data must be be an iris Cube type.')

        if kdims:
            if len(kdims) != len(data.dim_coords):
                raise ValueError('Supplied key dimensions must match Cube dim_coords.')
            coords = []
            for kd in kdims:
                coord = data.coords(kd.name if isinstance(kd, Dimension) else kd)
                if len(coord) == 0:
                    raise ValueError('Key dimension %s not found in Iris cube.' % kd)
                coords.append(coord[0])
        else:
            coords = data.dim_coords
            coords = sorted(coords, key=sort_coords)
        kdims = [coord_to_dimension(crd) for crd in coords]
        if vdims is None:
            vdims = [Dimension(data.name(), unit=str(data.units))]

        return data, kdims, vdims


    @classmethod
    def validate(cls, columns):
        pass


    @classmethod
    def values(cls, columns, dim, expanded=True, flat=True):
        """
        Returns an array of the values along the supplied dimension.
        """
        dim = columns.get_dimension(dim)
        if dim in columns.vdims:
            data = columns.data.data
        elif expanded:
            idx = columns.get_dimension_index(dim)
            data = util.cartesian_product([columns.data.coords(d.name)[0].points
                                           for d in columns.kdims])[:, idx]
        else:
            data = columns.data.coords(dim.name)[0].points
        return data.flatten() if flat else data


    @classmethod
    def reindex(cls, columns, kdims=None, vdims=None):
        """
        Reorders the key dimensions of the Cube, does
        not support dropping dimensions.
        """
        return columns


    @classmethod
    def sort(cls, columns, dims):
        return columns


    @classmethod
    def groupby(cls, columns, dims, container_type=HoloMap, group_type=None, **kwargs):
        """
        Groups the data by one or more dimensions returning a container
        indexed by the grouped dimensions containing slices of the
        cube wrapped in the group_type. This makes it very easy to
        break up a high-dimensional Cube into smaller viewable chunks.
        """
        if not isinstance(dims, list): dims = [dims]
        dims = [columns.get_dimension(d) for d in dims]
        slice_dims = [d for d in columns.kdims if d not in dims]
        data = []
        for cube in columns.data.slices([d.name for d in slice_dims]):
            key = tuple(cube.coord(kd.name).points[0] for kd in dims)
            data.append((key, columns.clone(cube, new_type=group_type, **dict(kwargs, kdims=slice_dims))))
        if issubclass(container_type, NdMapping):
            with item_check(False), sorted_context(False):
                return container_type(data, kdims=dims)
        else:
            return container_type(data)


    @classmethod
    def range(cls, columns, dimension):
        """
        Computes the range along a particular dimension.
        """
        dim = columns.get_dimension(dimension)
        values = columns.dimension_values(dim)
        return (np.min(values), np.max(values))


    @classmethod
    def length(cls, columns):
        """
        Returns the total number of samples in the Cube.
        """
        return np.product([len(d.points) for d in columns.data.coords()])


DataColumns.register(CubeData)
