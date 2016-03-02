import iris
from iris.util import guess_coord_axis
import numpy as np

import param
from holoviews.core import Dimension, Element, HoloMap


def coord_to_dimension(coord):
    """
    Converts an iris coordinate to a HoloViews dimension.
    """
    kwargs = {}
    if coord.units.is_time_reference():
        kwargs['value_format'] = coord.units.num2date
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


class Cube(Element):
    """
    The Cube Element provides an interface to wrap and display
    :class:`Iris.cube.Cube` objects. The Cube automatically
    infers the key and value dimensions of the iris data
    and provides useful methods for accessing, grouping
    and slicing the data.
    """

    group = param.String(default='Cube')
    
    def __init__(self, data, **params):
        if not isinstance(data, iris.cube.Cube):
            raise TypeError('Cube data must be of Iris Cube type.')

        if 'kdims' in params:
            kdims = params['kdims']
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
        params['kdims'] = [coord_to_dimension(coord)
                           for coord in coords]
        if 'vdims' not in params:
            params['vdims'] = [Dimension(data.name(), unit=str(data.units))]
        super(Cube, self).__init__(data, **params)


    def dimension_values(self, dim, unique=True):
        """
        Returns an array of the values along the supplied dimension.
        """
        dim = self.get_dimension(dim)
        if dim in self.vdims:
            return self.data.data
        else:
            return self.data.coords(dim.name)[0].points


    def reindex(self, kdims=None):
        """
        Reorders the key dimensions of the Cube, does
        not support dropping dimensions.
        """
        if len(kdims) != self.ndims:
            raise ValueError('Reindexed dimensions must be same length as '
                             'existing dimensions.')
        kdims = [self.get_dimension(kd) for kd in kdims]
        return self.clone(kdims=kdims)


    def groupby(self, dims, container_type=HoloMap, group_type=None, **kwargs):
        """
        Groups the data by one or more dimensions returning a container
        indexed by the grouped dimensions containing slices of the
        cube wrapped in the group_type. This makes it very easy to
        break up a high-dimensional Cube into smaller viewable chunks.
        """
        if not isinstance(dims, list): dims = [dims]
        dims = [self.get_dimension(d) for d in dims]
        slice_dims = [d for d in self.kdims if d not in dims]
        data = []
        for cube in self.data.slices([d.name for d in slice_dims]):
            key = tuple(cube.coord(kd.name).points[0] for kd in dims)
            data.append((key, self.clone(cube, kdims=slice_dims, new_type=group_type, **kwargs)))
        return container_type(data, kdims=dims)


    def range(self, dimension):
        """
        Computes the range along a particular dimension.
        """
        dim = self.get_dimension(dimension)
        values = self.dimension_values(dim)
        return (np.min(values), np.max(values))


    def __len__(self):
        """
        Returns the total number of samples in the Cube.
        """
        return np.product([len(d.points) for d in self.data.coords()])
