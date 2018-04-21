import param
import numpy as np
from cartopy import crs as ccrs
from cartopy.feature import Feature as cFeature
from cartopy.io.img_tiles import GoogleTiles
from cartopy.io.shapereader import Reader
from holoviews.core import Element2D, Dimension, Dataset as HvDataset, NdOverlay
from holoviews.core.util import (basestring, pd, max_extents,
                                 dimension_range, get_param_values)
from holoviews.element import (
    Contours as HvContours, Graph as HvGraph, Image as HvImage,
    Nodes as HvNodes, Path as HvPath, Polygons as HvPolygons,
    RGB as HvRGB, Text as HvText, TriMesh as HvTriMesh,
    QuadMesh as HvQuadMesh, Points as HvPoints,
    VectorField as HvVectorField, HexTiles as HvHexTiles,
    Labels as HvLabels)

from shapely.geometry.base import BaseGeometry

try:
    from iris.cube import Cube
except ImportError:
    Cube = None

try:
    from bokeh.models import MercatorTileSource
except:
    MercatorTileSource = None

try:
    from owslib.wmts import WebMapTileService
except:
    WebMapTileService = None

from ..util import path_to_geom, polygon_to_geom, geom_to_array

geographic_types = (GoogleTiles, cFeature, BaseGeometry)

def is_geographic(element, kdims=None):
    """
    Utility to determine whether the supplied element optionally
    a subset of its key dimensions represent a geographic coordinate
    system.
    """
    if isinstance(element, NdOverlay):
        element = element.last

    if kdims:
        kdims = [element.get_dimension(d) for d in kdims]
    else:
        kdims = element.kdims

    if len(kdims) != 2 and not isinstance(element, (Graph, Nodes)):
        return False
    if isinstance(element.data, geographic_types) or isinstance(element, (WMTS, Feature)):
        return True
    elif isinstance(element, _Element):
        return kdims == element.kdims and element.crs
    else:
        return False


class _Element(Element2D):
    """
    Baseclass for Element2D types with associated cartopy
    coordinate reference system.
    """

    _abstract = True

    crs = param.ClassSelector(default=ccrs.PlateCarree(), class_=ccrs.CRS, doc="""
        Cartopy coordinate-reference-system specifying the
        coordinate system of the data. Inferred automatically
        when _Element wraps cartopy Feature object.""")

    kdims = param.List(default=[Dimension('Longitude'), Dimension('Latitude')],
                       bounds=(2, 2), constant=True)

    def __init__(self, data, kdims=None, vdims=None, **kwargs):
        crs = None
        crs_data = data.data if isinstance(data, HvDataset) else data
        if Cube and isinstance(crs_data, Cube):
            coord_sys = crs_data.coord_system()
            if hasattr(coord_sys, 'as_cartopy_projection'):
                crs = coord_sys.as_cartopy_projection()
        elif isinstance(crs_data, (cFeature, GoogleTiles)):
            crs = crs_data.crs

        supplied_crs = kwargs.get('crs', None)
        if supplied_crs and crs and crs != supplied_crs:
            raise ValueError('Supplied coordinate reference '
                             'system must match crs of the data.')
        elif crs:
            kwargs['crs'] = crs
        super(_Element, self).__init__(data, kdims=kdims, vdims=vdims, **kwargs)


    def clone(self, data=None, shared_data=True, new_type=None,
              *args, **overrides):
        if 'crs' not in overrides and (not new_type or isinstance(new_type, _Element)):
            overrides['crs'] = self.crs
        return super(_Element, self).clone(data, shared_data, new_type,
                                           *args, **overrides)


class _GeoFeature(_Element):
    """
    Baseclass for geographic types without their own data.
    """

    _auxiliary_component = True

    def dimension_values(self, dim):
        """
        _GeoFeature types do not contain actual data.
        """
        return []


class Feature(_GeoFeature):
    """
    A Feature represents a geographical feature
    specified as a cartopy Feature type.
    """

    group = param.String(default='Feature')

    def __init__(self, data, kdims=None, vdims=None, **params):
        if not isinstance(data, cFeature):
            raise TypeError('%s data has to be an cartopy Feature type'
                            % type(data).__name__)
        super(Feature, self).__init__(data, kdims=kdims, vdims=vdims, **params)

    def range(self, dim, data_range=True):
        didx = self.get_dimension_index(dim)
        if didx in [0, 1] and data_range:
            dim = self.get_dimension(dim)
            l, b, r, t = max_extents([geom.bounds for geom in self.data.geometries()])
            lower, upper = (b, t) if didx else (l, r)
            return dimension_range(lower, upper, dim)
        return super(Feature, self).range(dim, data_range)


class WMTS(_GeoFeature):
    """
    The WMTS Element represents a Web Map Tile Service specified as a
    URL containing {x}, {y}, and {z} templating variables, e.g.:

    https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}@2x.png
    """

    group = param.String(default='WMTS')

    layer = param.String(doc="The layer on the tile service")

    def __init__(self, data, kdims=None, vdims=None, **params):
        if ((MercatorTileSource and isinstance(data, MercatorTileSource)) or
            (GoogleTiles and isinstance(data, GoogleTiles))):
            data = data.url
        elif WebMapTileService and isinstance(data, WebMapTileService):
            pass
        elif not isinstance(data, basestring):
            raise TypeError('%s data should be a tile service URL not a %s type.'
                            % (type(self).__name__, type(data).__name__) )
        super(WMTS, self).__init__(data, kdims=kdims, vdims=vdims, **params)


class Tiles(WMTS):
    """
    Tiles represents an image tile source to dynamically
    load data from depending on the zoom level.
    """

    group = param.String(default='Tiles')


class Dataset(_Element, HvDataset):
    """
    Coordinate system aware version of a HoloViews dataset.
    """

    kdims = param.List(default=[Dimension('Longitude'), Dimension('Latitude')],
                       constant=True)

    group = param.String(default='Dataset')


class Points(_Element, HvPoints):
    """
    Points represent a collection of points with
    an associated cartopy coordinate-reference system.
    """

    group = param.String(default='Points')


class HexTiles(_Element, HvHexTiles):
    """
    Points represent a collection of points with
    an associated cartopy coordinate-reference system.
    """

    group = param.String(default='HexTiles')



class Labels(_Element, HvLabels):
    """
    Points represent a collection of points with
    an associated cartopy coordinate-reference system.
    """

    group = param.String(default='Labels')


class VectorField(_Element, HvVectorField):
    """
    A VectorField contains is a collection of vectors where each
    vector has an associated position. The vectors should be specified
    by defining an angle in radians and a magnitude.
    """

    group = param.String(default='VectorField', constant=True)

    vdims = param.List(default=[Dimension('Angle', cyclic=True, range=(0,2*np.pi)),
                                Dimension('Magnitude')], bounds=(1, None))



class LineContours(_Element, HvImage):
    """
    Contours represents a 2D array of some quantity with
    some associated coordinates, which may be discretized
    into one or more line contours.
    """

    vdims = param.List(default=[Dimension('z')], bounds=(1, 1))

    group = param.String(default='LineContours')


class FilledContours(LineContours):
    """
    Contours represents a 2D array of some quantity with
    some associated coordinates, which may be discretized
    into one or more filled contours.
    """

    group = param.String(default='FilledContours')


class Image(_Element, HvImage):
    """
    Image represents a 2D array of some quantity with
    some associated coordinates.
    """

    vdims = param.List(default=[Dimension('z')], bounds=(1, 1))

    group = param.String(default='Image')


class QuadMesh(_Element, HvQuadMesh):
    """
    QuadMesh is a Raster type to hold x- and y- bin values
    with associated values. The x- and y-values of the QuadMesh
    may be supplied either as the edges of each bin allowing
    uneven sampling or as the bin centers, which will be converted
    to evenly sampled edges.

    As a secondary but less supported mode QuadMesh can contain
    a mesh of quadrilateral coordinates that is not laid out in
    a grid. The data should then be supplied as three separate
    2D arrays for the x-/y-coordinates and grid values.
    """

    datatype = param.List(default=['grid', 'xarray'])

    vdims = param.List(default=[Dimension('z')], bounds=(1, 1))

    group = param.String(default='QuadMesh')

    _binned = True

    def trimesh(self):
        trimesh = super(QuadMesh, self).trimesh()
        node_params = get_param_values(trimesh.nodes)
        nodes = TriMesh.node_type(trimesh.nodes.data, **node_params)
        return TriMesh((trimesh.data, nodes), crs=self.crs,
                       **get_param_values(trimesh))


class RGB(_Element, HvRGB):
    """
    An RGB element is a Image containing channel data for the the
    red, green, blue and (optionally) the alpha channels. The values
    of each channel must be in the range 0.0 to 1.0.

    In input array may have a shape of NxMx4 or NxMx3. In the latter
    case, the defined alpha dimension parameter is appended to the
    list of value dimensions.
    """

    group = param.String(default='RGB', constant=True)

    vdims = param.List(
        default=[Dimension('R', range=(0,1)), Dimension('G',range=(0,1)),
                 Dimension('B', range=(0,1)), Dimension('A', range=(0,1))],
        bounds=(3, 4), doc="""
        The dimension description of the data held in the matrix.

        If an alpha channel is supplied, the defined alpha_dimension
        is automatically appended to this list.""")



class Nodes(_Element, HvNodes):
    """
    Nodes is a simple Element representing Graph nodes as a set of
    Points.  Unlike regular Points, Nodes must define a third key
    dimension corresponding to the node index.
    """

    group = param.String(default='Nodes', constant=True)

    kdims = param.List(default=[Dimension('Longitude'), Dimension('Latitude'),
                                Dimension('index')], bounds=(3, 3))



class Text(HvText, _Element):
    """
    An annotation containing some text at an x, y coordinate
    along with a coordinate reference system.
    """


class Path(_Element, HvPath):
    """
    The Path Element contains a list of Paths stored as Nx2 numpy
    arrays along with a coordinate reference system.
    """

    group = param.String(default='Path', constant=True)

    def geom(self):
        """
        Returns Path as a shapely geometry.
        """
        return path_to_geom(self)


class EdgePaths(Path):
    """
    EdgePaths is a simple Element representing the paths of edges
    connecting nodes in a graph.
    """

    group = param.String(default='EdgePaths', constant=True)



class Graph(_Element, HvGraph):

    group = param.String(default='Graph', constant=True)

    node_type = Nodes

    edge_type = EdgePaths

    def __init__(self, data, kdims=None, vdims=None, **params):
        nodes, edges = None, None
        if isinstance(data, tuple):
            if len(data) > 1 and isinstance(data[1], self.node_type):
                nodes = data[1]
            elif len(data) > 2 and isinstance(data[2], self.edge_type):
                edges = data[2]

        if 'crs' in params:
            crs = params['crs']
            mismatch = None
            if nodes is not None and type(crs) != type(nodes.crs):
                mismatch = 'nodes'
            elif edges is not None and type(crs) != type(edges.crs):
                mismatch = 'edges'
            if mismatch:
                raise ValueError("Coordinate reference system supplied "
                                 "to %s element must match the crs of "
                                 "the %s. Expected %s found %s." %
                                 (mismatch, type(self).__name__, nodes.crs, crs))
        elif nodes is not None:
            crs = nodes.crs
            params['crs'] = crs
        else:
            crs = self.crs

        super(Graph, self).__init__(data, kdims, vdims, **params)
        self.nodes.crs = crs


    @property
    def edgepaths(self):
        """
        Returns the fixed EdgePaths or computes direct connections
        between supplied nodes.
        """
        edgepaths = super(Graph, self).edgepaths
        edgepaths.crs = self.crs
        return edgepaths



class TriMesh(HvTriMesh, Graph):

    group = param.String(default='TriMesh', constant=True)

    node_type = Nodes

    edge_type = EdgePaths

    point_type = Points

    def __init__(self, data, kdims=None, vdims=None, **params):
        nodes, edges = None, None
        if isinstance(data, tuple):
            if len(data) > 1 and isinstance(data[1], (self.node_type, self.point_type)):
                nodes = data[1]
            elif len(data) > 2 and isinstance(data[2], self.edge_type):
                edges = data[2]

        if 'crs' in params:
            crs = params['crs']
            mismatch = None
            if nodes is not None and type(crs) != type(nodes.crs):
                mismatch = 'nodes'
            elif edges is not None and type(crs) != type(edges.crs):
                mismatch = 'edges'
            if mismatch:
                raise ValueError("Coordinate reference system supplied "
                                 "to %s element must match the crs of "
                                 "the %s. Expected %s found %s." %
                                 (mismatch, type(self).__name__, nodes.crs, crs))
        elif nodes is not None:
            crs = nodes.crs
            params['crs'] = crs
        else:
            crs = self.crs

        super(TriMesh, self).__init__(data, kdims, vdims, **params)
        self.nodes.crs = crs


    @property
    def edgepaths(self):
        """
        Returns the fixed EdgePaths or computes direct connections
        between supplied nodes.
        """
        edgepaths = super(TriMesh, self).edgepaths
        edgepaths.crs = self.crs
        return edgepaths


class Contours(_Element, HvContours):
    """
    Contours is a Path Element type that may contain any number of
    closed paths with an associated value and a coordinate reference
    system.
    """

    group = param.String(default='Contours', constant=True)

    def geom(self):
        """
        Returns Path as a shapely geometry.
        """
        return path_to_geom(self)


class Polygons(_Element, HvPolygons):
    """
    Polygons is a Path Element type that may contain any number of
    closed paths with an associated value and a coordinate reference
    system.
    """

    group = param.String(default='Polygons', constant=True)

    def geom(self):
        """
        Returns Path as a shapely geometry.
        """
        return polygon_to_geom(self)


class Shape(_Element):
    """
    Shape wraps any shapely geometry type.
    """

    group = param.String(default='Shape')

    level = param.Number(default=None, doc="""
        Optional level associated with the set of Contours.""")

    vdims = param.List(default=[Dimension('Level')], doc="""
        Contours optionally accept a value dimension, corresponding
        to the supplied values.""", bounds=(1,1))

    def __init__(self, data, kdims=None, vdims=None, **params):
        if not isinstance(data, BaseGeometry):
            raise TypeError('%s data has to be a shapely geometry type.'
                            % type(data).__name__)
        super(Shape, self).__init__(data, kdims=kdims, vdims=vdims, **params)


    @classmethod
    def from_shapefile(cls, shapefile, *args, **kwargs):
        """
        Loads a shapefile from disk and optionally merges
        it with a dataset. See ``from_records`` for full
        signature.
        """
        reader = Reader(shapefile)
        return cls.from_records(reader.records(), *args, **kwargs)


    @classmethod
    def from_records(cls, records, dataset=None, on=None,
                     value=None, index=[], drop_missing=False, **kwargs):
        """
        Load data from a collection of
        ``cartopy.io.shapereader.Record`` objects and optionally merge
        it with a dataset to assign values to each polygon and form a
        chloropleth. Supplying just records will return an NdOverlay
        of Shape Elements with a numeric index. If a dataset is
        supplied, a mapping between the attribute names in the records
        and the dimension names in the dataset must be supplied. The
        values assigned to each shape file can then be drawn from the
        dataset by supplying a ``value`` and keys the Shapes are
        indexed by specifying one or index dimensions.

        * records - An iterator of cartopy.io.shapereader.Record
                    objects.
        * dataset - Any HoloViews Dataset type.
        * on      - A mapping between the attribute names in
                    the records and the dimensions in the dataset.
        * value   - The value dimension in the dataset the
                    values will be drawn from.
        * index   - One or more dimensions in the dataset
                    the Shapes will be indexed by.
        * drop_missing - Whether to drop shapes which are missing from
                         the provided dataset.

        Returns an NdOverlay of Shapes.
        """
        if dataset is not None and not on:
            raise ValueError('To merge dataset with shapes mapping '
                             'must define attribute(s) to merge on.')

        if pd and isinstance(dataset, pd.DataFrame):
            dataset = Dataset(dataset)

        if not isinstance(on, (dict, list)):
            on = [on]
        if on and not isinstance(on, dict):
            on = {o: o for o in on}
        if not isinstance(index, list):
            index = [index]

        kdims = []
        for ind in (index if index else ['Index']):
            if dataset and dataset.get_dimension(ind):
                dim = dataset.get_dimension(ind)
            else:
                dim = Dimension(ind)
            kdims.append(dim)

        ddims = []
        if dataset:
            vdim = dataset.get_dimension(value)
            kwargs['vdims'] = [vdim]
            if not vdim:
                raise ValueError('Value dimension not found '
                                 'in dataset: {}'.format(vdim))
            ddims = dataset.dimensions()

        data = []
        notfound = False
        for i, rec in enumerate(records):
            if dataset:
                selection = {dim: rec.attributes.get(attr, None)
                             for attr, dim in on.items()}
                row = dataset.select(**selection)
                if len(row):
                    value = row[vdim.name][0]
                elif drop_missing:
                    continue
                else:
                    value = np.NaN
                kwargs['level'] = value
            if index:
                key = []
                for kdim in kdims:
                    if kdim in ddims and len(row):
                        k = row[kdim.name][0]
                    elif kdim.name in rec.attributes:
                        k = rec.attributes[kdim.name]
                    else:
                        k = None
                        notfound = True
                    key.append(k)
                key = tuple(key)
            else:
                key = (i,)
            data.append((key, Shape(rec.geometry, **kwargs)))
        if notfound:
            kdims = ['Index']+kdims
            data = [((i,)+subk, v) for i, (subk, v) in enumerate(data)]
        return NdOverlay(data, kdims=kdims)


    def dimension_values(self, dimension, expanded=True, flat=True):
        """
        Shapes do not support convert to array values.
        """
        dim = self.get_dimension(dimension)
        if dim in self.vdims:
            return np.full(len(self), self.level) if expanded else np.array([self.level])
        else:
            return []


    def range(self, dim, data_range=True):
        dim = self.get_dimension(dim)
        if dim.range != (None, None):
            return dim.range

        idx = self.get_dimension_index(dim)
        if idx == 2 and data_range:
            return self.level, self.level
        if idx in [0, 1] and data_range:
            l, b, r, t = self.data.bounds
            lower, upper = (b, t) if idx else (l, r)
            return dimension_range(lower, upper, dim)
        else:
            return super(Shape, self).range(dim, data_range)


    def geom(self):
        """
        Returns Shape as a shapely geometry
        """
        return self.data


    def __len__(self):
        return len(geom_to_array(self.data))
