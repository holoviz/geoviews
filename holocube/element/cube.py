from itertools import product
import iris
import numpy as np

import param
from holoviews.core.dimension import Dimension
from holoviews.core.data import DataColumns, GridColumns
from holoviews.core.ndmapping import (NdMapping, item_check,
                                      sorted_context)
from holoviews.core.spaces import HoloMap
from holoviews.element.tabular import Table, TableConversion
from . import util



class HoloCube(Table):
    """
    The HoloCube Element provides an interface to wrap and display
    :class:`Iris.cube.Cube` objects. The Cube automatically
    infers the key and value dimensions of the iris data
    and provides useful methods for accessing, grouping
    and slicing the data.
    """

    datatype = param.List(default=Table.datatype+['cube'])

    group = param.String(default='HoloCube')

    @property
    def to(self):
        """
        Property to create a conversion table with methods to convert
        to any type.
        """
        return CubeConversion(self)



class CubeConversion(TableConversion):
    """
    CubeConversion is a very simple container object which can
    be given an existing HoloCube and provides methods to convert
    the HoloCube into most other Element types. If the requested
    key dimensions correspond to geographical coordinates the
    conversion interface will automatically use a geographical
    Element type while all other plot will use regular HoloViews
    Elements.
    """

    def __init__(self, cube):
        self._table = cube

    def contours(self, kdims=None, vdims=None, mdims=None, **kwargs):
        from .geo import Contours
        return self(Contours, kdims, vdims, mdims, **kwargs)

    def image(self, kdims=None, vdims=None, mdims=None, **kwargs):
        from .geo import Image
        return self(Image, kdims, vdims, mdims, **kwargs)

    def points(self, kdims=None, vdims=None, mdims=None, **kwargs):
        if kdims is None: kdims = self._table.kdims
        kdims = [self._table.get_dimension(d) for d in kdims]
        geo = all(self._table.data.coord(kd.name).coord_system for kd in kdims)
        if len(kdims) == 2 and geo:
            from .geo import Points as Points
        else:
            from holoviews.element import Points
        return self(Points, kdims, vdims, mdims, **kwargs)



class CubeInterface(GridColumns):
    """
    The CubeInterface provides allows HoloViews to interact
    with iris Cube data. When passing an iris Cube to a
    HoloViews Element the init method will infer the
    dimensions of the HoloCube from its coordinates.
    Currently the interface only provides the basic methods
    required for HoloViews to work with an object.
    """

    types = (iris.cube.Cube,)

    datatype = 'cube'

    @classmethod
    def init(cls, eltype, data, kdims, vdims):
        if not isinstance(data, iris.cube.Cube):
            raise TypeError('HoloCube data must be be an iris HoloCube type.')

        if kdims:
            if len(kdims) != len(data.dim_coords):
                raise ValueError('Supplied key dimensions must match '
                                 'HoloCube dim_coords.')
            coords = []
            for kd in kdims:
                coord = data.coords(kd.name if isinstance(kd, Dimension) else kd)
                if len(coord) == 0:
                    raise ValueError('Key dimension %s not found in '
                                     'Iris cube.' % kd)
                coords.append(coord[0])
        else:
            coords = data.dim_coords
            coords = sorted(coords, key=util.sort_coords)
        kdims = [util.coord_to_dimension(crd) for crd in coords]
        if vdims is None:
            vdims = [Dimension(data.name(), unit=str(data.units))]

        return data, kdims, vdims


    @classmethod
    def validate(cls, holocube):
        pass


    @classmethod
    def values(cls, holocube, dim, expanded=True, flat=True):
        """
        Returns an array of the values along the supplied dimension.
        """
        dim = holocube.get_dimension(dim)
        if dim in holocube.vdims:
            data = holocube.data.copy().data
        elif expanded:
            idx = holocube.get_dimension_index(dim)
            data = util.cartesian_product([holocube.data.coords(d.name)[0].points
                                           for d in holocube.kdims])[idx]
        else:
            data = holocube.data.coords(dim.name)[0].points
        return data.flatten() if flat else data


    @classmethod
    def reindex(cls, holocube, kdims=None, vdims=None):
        """
        Since cubes are never indexed directly the data itself
        does not need to be reindexed, the Element can simply
        reorder its key dimensions.
        """
        return holocube


    @classmethod
    def groupby(cls, holocube, dims, container_type=HoloMap, group_type=None, **kwargs):
        """
        Groups the data by one or more dimensions returning a container
        indexed by the grouped dimensions containing slices of the
        cube wrapped in the group_type. This makes it very easy to
        break up a high-dimensional HoloCube into smaller viewable chunks.
        """
        if not isinstance(dims, list): dims = [dims]
        dims = [holocube.get_dimension(d) for d in dims]
        constraints = [d.name for d in dims]
        slice_dims = [d for d in holocube.kdims if d not in dims]
        unique_coords = product(*[cls.values(holocube, d, expanded=False)
                                 for d in dims])
        data = []
        for key in unique_coords:
            constraint = iris.Constraint(**dict(zip(constraints, key)))
            cube = holocube.clone(holocube.data.extract(constraint),
                                  new_type=group_type,
                                  **dict(kwargs, kdims=slice_dims))
            data.append((key, cube))
        if issubclass(container_type, NdMapping):
            with item_check(False), sorted_context(False):
                return container_type(data, kdims=dims)
        else:
            return container_type(data)


    @classmethod
    def range(cls, holocube, dimension):
        """
        Computes the range along a particular dimension.
        """
        dim = holocube.get_dimension(dimension)
        values = holocube.dimension_values(dim, False)
        return (np.nanmin(values), np.nanmax(values))


    @classmethod
    def length(cls, holocube):
        """
        Returns the total number of samples in the HoloCube.
        """
        return np.product([len(d.points) for d in holocube.data.coords()])


DataColumns.register(CubeInterface)
