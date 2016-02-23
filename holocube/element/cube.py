import iris
import param
import numpy as np

from holoviews.core import Dimension, Element, HoloMap


def coord_to_dimension(coord):
    kwargs = {}
    if coord.units.is_time_reference():
        kwargs['value_format'] = coord.units.num2date
    else:
        kwargs['unit'] = str(coord.units)
    return Dimension(coord.name(), **kwargs)


class Cube(Element):
    
    def __init__(self, data, **params):
        if isinstance(data, iris.cube.Cube):
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
            params['kdims'] = [coord_to_dimension(coord)
                               for coord in coords]
            if 'vdims' not in params:
                params['vdims'] = [Dimension(data.name(), unit=str(data.units))]
        else:
            raise ValueError('Cube data must be of Iris Cube type.')
        super(Cube, self).__init__(data, **params)

    def dimension_values(self, dim, unique=True):
        dim = self.get_dimension(dim)
        if dim in self.vdims:
            return self.data.data
        else:
            return self.data.coords(dim.name)[0].points
        
    def reindex(self, kdims=None):
        kdims = [self.get_dimension(kd) for kd in kdims]
        return self.clone(kdims=kdims)

    def groupby(self, dims, container_type=HoloMap, group_type=None, **kwargs):
        if not isinstance(dims, list): dims = [dims]
        dims = [self.get_dimension(d) for d in dims]
        slice_dims = [d for d in self.kdims if d not in dims]
        data = []
        for cube in self.data.slices([d.name for d in slice_dims]):
            key = tuple(cube.coord(kd.name).points[0] for kd in dims)
            data.append((key, self.clone(cube, kdims=slice_dims, new_type=group_type, **kwargs)))
        return container_type(data, kdims=dims)

    def range(self, dimension):
        dim = self.get_dimension(dimension)
        values = self.dimension_values(dim)
        return (np.min(values), np.max(values))

    def __len__(self):
        return np.product([len(d.points) for d in self.data.coords()])
