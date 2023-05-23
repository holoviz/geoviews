import param
import numpy as np

from bokeh.models import MercatorTileSource
from cartopy import crs as ccrs
from cartopy.feature import Feature as cFeature
from cartopy.io.img_tiles import GoogleTiles
from cartopy.io.shapereader import Reader
from holoviews.core import Element2D, Dimension, Dataset as HvDataset, NdOverlay, Overlay
from holoviews.core import util
from holoviews.element import (
    Contours as HvContours, Graph as HvGraph, Image as HvImage,
    Nodes as HvNodes, Path as HvPath, Polygons as HvPolygons,
    RGB as HvRGB, Text as HvText, TriMesh as HvTriMesh,
    QuadMesh as HvQuadMesh, Points as HvPoints,
    VectorField as HvVectorField, HexTiles as HvHexTiles,
    Labels as HvLabels, Rectangles as HvRectangles,
    Segments as HvSegments
)

from shapely.geometry.base import BaseGeometry
from shapely.geometry import (
    box, GeometryCollection, MultiPolygon, LineString, MultiLineString,
    Point, MultiPoint
)
from shapely.ops import unary_union

try:
    from iris.cube import Cube
except (ImportError, OSError):
    # OSError because environment variable $UDUNITS2_XML_PATH
    # is sometimes not set. Should be done automatically
    # when installing the package.
    Cube = None



try:
    from owslib.wmts import WebMapTileService
except ImportError:
    WebMapTileService = None

from ..util import (
    path_to_geom_dicts, polygons_to_geom_dicts, load_tiff, from_xarray,
    poly_types, expand_geoms, transform_shapely
)

geographic_types = (GoogleTiles, cFeature, BaseGeometry)

def is_geographic(element, kdims=None):
    """
    Utility to determine whether the supplied element optionally
    a subset of its key dimensions represent a geographic coordinate
    system.
    """
    if isinstance(element, (Overlay, NdOverlay)):
        return any(element.traverse(is_geographic, [_Element]))

    if kdims:
        kdims = [element.get_dimension(d) for d in kdims]
    else:
        kdims = element.kdims

    if len(kdims) != 2 and not isinstance(element, (Graph, Nodes, Rectangles, Segments)):
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
        if isinstance(data, HvDataset):
            crs_data = data.data
        else:
            crs_data = data
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
        elif isinstance(data, _Element):
            kwargs['crs'] = data.crs
        super().__init__(data, kdims=kdims, vdims=vdims, **kwargs)


    def clone(self, data=None, shared_data=True, new_type=None,
              *args, **overrides):
        if 'crs' not in overrides and (not new_type or isinstance(new_type, _Element)):
            overrides['crs'] = self.crs
        return super().clone(data, shared_data, new_type,
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
        super().__init__(data, kdims=kdims, vdims=vdims, **params)

    def __call__(self, *args, **kwargs):
        return self.clone().opts(*args, **kwargs)

    def geoms(self, scale=None, bounds=None, as_element=True):
        """
        Returns the geometries held by the Feature.

        Parameters
        ----------
        scale: str
          Scale of the geometry to return expressed as string.
          Available scales depends on the Feature type.

          NaturalEarthFeature:
           '10m', '50m', '110m'

          GSHHSFeature:
           'auto', 'coarse', 'low', 'intermediate', 'high', 'full'

        bounds: tuple
          Tuple of a bounding region to query for geometries in
        as_element: boolean
          Whether to wrap the geometries in an element

        Returns
        -------
        geometries: Polygons/Path
          Polygons or Path object wrapping around returned geometries
        """
        feature = self.data
        if scale is not None:
            feature = feature.with_scale(scale)

        if bounds:
            extent = (bounds[0], bounds[2], bounds[1], bounds[3])
        else:
            extent = None
        geoms = [g for g in feature.intersecting_geometries(extent) if g is not None]
        if not as_element:
            return geoms
        elif not geoms or 'Polygon' in geoms[0].geom_type:
            return Polygons(geoms, crs=feature.crs)
        elif 'Point' in geoms[0].geom_type:
            return Points(geoms, crs=feature.crs)
        else:
            return Path(geoms, crs=feature.crs)

    def range(self, dim, data_range=True, dimension_range=True):
        didx = self.get_dimension_index(dim)
        if didx in [0, 1] and data_range:
            dim = self.get_dimension(dim)
            l, b, r, t = util.max_extents([geom.bounds for geom in self.data.geometries()])
            lower, upper = (b, t) if didx else (l, r)
            if dimension_range:
                return util.dimension_range(lower, upper, dim.range, dim.soft_range)
            else:
                return lower, upper
        return super().range(dim, data_range, dimension_range)


class WMTS(_GeoFeature):
    """
    The WMTS Element represents a Web Map Tile Service specified as a
    URL containing {x}, {y}, and {z} templating variables, e.g.:

    https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}@2x.png
    """

    crs = param.ClassSelector(default=ccrs.GOOGLE_MERCATOR, class_=ccrs.CRS, doc="""
        Cartopy coordinate-reference-system specifying the
        coordinate system of the data. Inferred automatically
        when _Element wraps cartopy Feature object.""")

    group = param.String(default='WMTS')

    layer = param.String(doc="The layer on the tile service")

    def __init__(self, data, kdims=None, vdims=None, **params):
        if ((MercatorTileSource and isinstance(data, MercatorTileSource)) or
            (GoogleTiles and isinstance(data, GoogleTiles))):
            data = data.url
        elif WebMapTileService and isinstance(data, WebMapTileService):
            pass
        elif not isinstance(data, str):
            raise TypeError(
                f'{type(self).__name__} data should be a tile service '
                f'URL not a {type(data).__name__} type.'
            )
        super().__init__(data, kdims=kdims, vdims=vdims, **params)

    def __call__(self, *args, **kwargs):
        return self.opts(*args, **kwargs)


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
                       bounds=(0, None),
                       constant=True)

    group = param.String(default='Dataset')


class Points(_Element, HvPoints):
    """
    Points represent a collection of points with
    an associated cartopy coordinate-reference system.
    """

    group = param.String(default='Points')

    def geom(self, union=False, projection=None):
        """
        Converts the Points to a shapely geometry.

        Parameters
        ----------
        union: boolean (default=False)
            Whether to compute a union between the geometries
        projection : EPSG string | Cartopy CRS | None
            Whether to project the geometry to other coordinate system

        Returns
        -------
        A shapely geometry
        """
        points = [Point(x, y) for (x, y) in self.array([0, 1])]
        npoints = len(points)
        if not npoints:
            geom = GeometryCollection()
        elif len(points) == 1:
            geom = points[0]
        else:
            geom = MultiPoint(points)
        if projection:
            geom = transform_shapely(geom, self.crs, projection)
        return unary_union(geom) if union else geom


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


class Image(_Element, HvImage):
    """
    Image represents a 2D array of some quantity with
    some associated coordinates.
    """

    vdims = param.List(default=[Dimension('z')], bounds=(1, None))

    group = param.String(default='Image')

    @classmethod
    def load_tiff(cls, filename, crs=None, apply_transform=False,
                  nan_nodata=False, **kwargs):
        return load_tiff(filename, crs, apply_transform, **kwargs)

    @classmethod
    def from_xarray(cls, da, crs=None, apply_transform=False,
                    nan_nodata=False, **kwargs):
        return from_xarray(da, crs, apply_transform, **kwargs)



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

    vdims = param.List(default=[Dimension('z')], bounds=(1, None))

    group = param.String(default='QuadMesh')

    _binned = True

    @classmethod
    def load_tiff(cls, filename, crs=None, apply_transform=False,
                  nan_nodata=False, **kwargs):
        return load_tiff(filename, crs, apply_transform, **kwargs)

    @classmethod
    def from_xarray(cls, da, crs=None, apply_transform=False,
                    nan_nodata=False, **kwargs):
        return from_xarray(da, crs, apply_transform, **kwargs)

    def trimesh(self):
        trimesh = super().trimesh()
        node_params = util.get_param_values(trimesh.nodes)
        node_params['crs'] = self.crs
        nodes = TriMesh.node_type(trimesh.nodes.data, **node_params)
        return TriMesh((trimesh.data, nodes), crs=self.crs,
                       **util.get_param_values(trimesh))


class LineContours(QuadMesh):
    """
    LineContours represents a 2D array of some quantity with
    some associated coordinates, which may be discretized
    into one or more line contours.
    """

    group = param.String(default='LineContours')


class FilledContours(QuadMesh):
    """
    Contours represents a 2D array of some quantity with
    some associated coordinates, which may be discretized
    into one or more filled contours.
    """

    group = param.String(default='FilledContours')


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
                 Dimension('B', range=(0,1))],
        bounds=(3, 4), doc="""
        The dimension description of the data held in the matrix.

        If an alpha channel is supplied, the defined alpha_dimension
        is automatically appended to this list.""")

    @classmethod
    def load_tiff(cls, filename, crs=None, apply_transform=False,
                  nan_nodata=False, **kwargs):
        """
        Returns an RGB or Image element loaded from a geotiff file.

        The data is loaded using xarray and rasterio. If a crs attribute
        is present on the loaded data it will attempt to decode it into
        a cartopy projection otherwise it will default to a non-geographic
        HoloViews element.

        Parameters
        ----------
        filename: string
          Filename pointing to geotiff file to load
        crs: Cartopy CRS or EPSG string (optional)
          Overrides CRS inferred from the data
        apply_transform: boolean
          Whether to apply affine transform if defined on the data
        nan_nodata: boolean
          If data contains nodata values convert them to NaNs
        **kwargs:
          Keyword arguments passed to the HoloViews/GeoViews element

        Returns
        -------
        element: Image/RGB/QuadMesh element
        """
        return load_tiff(filename, crs, apply_transform, **kwargs)

    @classmethod
    def from_xarray(cls, da, crs=None, apply_transform=False,
                    nan_nodata=False, **kwargs):
        """
        Returns an RGB or Image element given an xarray DataArray
        loaded using xr.open_rasterio.

        If a crs attribute is present on the loaded data it will
        attempt to decode it into a cartopy projection otherwise it
        will default to a non-geographic HoloViews element.

        Parameters
        ----------
        da: xarray.DataArray
          DataArray to convert to element
        crs: Cartopy CRS or EPSG string (optional)
          Overrides CRS inferred from the data
        apply_transform: boolean
          Whether to apply affine transform if defined on the data
        nan_nodata: boolean
          If data contains nodata values convert them to NaNs
        **kwargs:
          Keyword arguments passed to the HoloViews/GeoViews element

        Returns
        -------
        element: Image/RGB/QuadMesh element
        """
        return from_xarray(da, crs, apply_transform, **kwargs)



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

    def geom(self, union=False, projection=None):
        """
        Converts the Path to a shapely geometry.

        Parameters
        ----------
        union: boolean (default=False)
            Whether to compute a union between the geometries
        projection : EPSG string | Cartopy CRS | None
            Whether to project the geometry to other coordinate system

        Returns
        -------
        A shapely geometry
        """
        geoms = expand_geoms([g['geometry'] for g in path_to_geom_dicts(self)])
        ngeoms = len(geoms)
        if not ngeoms:
            geom = GeometryCollection()
        elif ngeoms == 1:
            geom = geoms[0]
        else:
            geom = MultiLineString(geoms)
        if projection:
            geom = transform_shapely(geom, self.crs, projection)
        return unary_union(geom) if union else geom


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
            if nodes is not None and type(crs) != type(nodes.crs):  # noqa: E721
                mismatch = 'nodes'
            elif edges is not None and type(crs) != type(edges.crs):  # noqa: E721
                mismatch = 'edges'
            if mismatch:
                raise ValueError(
                    "Coordinate reference system supplied "
                    f"to {mismatch} element must match the crs of "
                    f"the {type(self).__name__}. Expected {nodes.crs} found {crs}."
                )
        elif nodes is not None:
            crs = nodes.crs
            params['crs'] = crs
        else:
            crs = self.crs

        super().__init__(data, kdims, vdims, **params)
        self.nodes.crs = crs


    @property
    def edgepaths(self):
        """
        Returns the fixed EdgePaths or computes direct connections
        between supplied nodes.
        """
        edgepaths = super().edgepaths
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
            if nodes is not None and type(crs) != type(nodes.crs):  # noqa: E721
                mismatch = 'nodes'
            elif edges is not None and type(crs) != type(edges.crs):  # noqa: E721
                mismatch = 'edges'
            if mismatch:
                raise ValueError(
                    "Coordinate reference system supplied "
                    f"to {mismatch} element must match the crs of "
                    f"the {type(self).__name__}. Expected {nodes.crs} found {crs}."
                )
        elif nodes is not None:
            crs = nodes.crs
            params['crs'] = crs
        else:
            crs = self.crs

        super().__init__(data, kdims, vdims, **params)
        self.nodes.crs = crs

    @property
    def edgepaths(self):
        """
        Returns the fixed EdgePaths or computes direct connections
        between supplied nodes.
        """
        edgepaths = super().edgepaths
        edgepaths.crs = self.crs
        return edgepaths


class Contours(_Element, HvContours):
    """
    Contours is a Path Element type that may contain any number of
    closed paths with an associated value and a coordinate reference
    system.
    """

    group = param.String(default='Contours', constant=True)

    def geom(self, union=False, projection=None):
        """
        Converts the Contours to a shapely geometry.

        Parameters
        ----------
        union: boolean (default=False)
            Whether to compute a union between the geometries
        projection : EPSG string | Cartopy CRS | None
            Whether to project the geometry to other coordinate system

        Returns
        -------
        A shapely geometry
        """
        geoms = expand_geoms([g['geometry'] for g in path_to_geom_dicts(self)])
        ngeoms = len(geoms)
        if not ngeoms:
            geom = GeometryCollection()
        elif ngeoms == 1:
            geom = geoms[0]
        else:
            geom = MultiLineString(geoms)
        if projection:
            geom = transform_shapely(geom, self.crs, projection)
        return unary_union(geom) if union else geom


class Polygons(_Element, HvPolygons):
    """
    Polygons is a Path Element type that may contain any number of
    closed paths with an associated value and a coordinate reference
    system.
    """

    group = param.String(default='Polygons', constant=True)

    def geom(self, union=False, projection=None):
        """
        Converts the Path to a shapely geometry.

        Parameters
        ----------
        union: boolean (default=False)
            Whether to compute a union between the geometries
        projection : EPSG string | Cartopy CRS | None
            Whether to project the geometry to other coordinate system

        Returns
        -------
        A shapely geometry
        """
        geoms = expand_geoms([g['geometry'] for g in polygons_to_geom_dicts(self)])
        ngeoms = len(geoms)
        if not ngeoms:
            geom = GeometryCollection()
        elif ngeoms == 1:
            geom = geoms[0]
        else:
            geom = MultiPolygon(geoms)
        if projection:
            geom = transform_shapely(geom, self.crs, projection)
        return unary_union(geom) if union else geom


class Rectangles(_Element, HvRectangles):
    """
    Rectangles represent a collection of axis-aligned rectangles in 2D space.
    """

    group = param.String(default='Rectangles', constant=True)

    kdims = param.List(default=[Dimension('lon0'), Dimension('lat0'),
                                Dimension('lon1'), Dimension('lat1')],
                       bounds=(4, 4), constant=True, doc="""
        The key dimensions of the Rectangles element represent the
        bottom-left (lon0, lat0) and top right (lon1, lat1) coordinates
        of each box.""")

    def geom(self, union=False, projection=None):
        """
        Converts the Rectangles to a shapely geometry.

        Parameters
        ----------
        union: boolean (default=False)
            Whether to compute a union between the geometries
        projection : EPSG string | Cartopy CRS | None
            Whether to project the geometry to other coordinate system

        Returns
        -------
        A shapely geometry
        """
        boxes = [box(*g) for g in self.array([0, 1, 2, 3])]
        nboxes = len(boxes)
        if not nboxes:
            geom = GeometryCollection()
        elif nboxes == 1:
            geom = boxes[0]
        else:
            geom = MultiPolygon(boxes)
        if projection:
            geom = transform_shapely(geom, self.crs, projection)
        return unary_union(geom) if union else geom


class Segments(_Element, HvSegments):
    """
    Segments represent a collection of lines in 2D space.
    """

    group = param.String(default='Segments', constant=True)

    kdims = param.List(default=[Dimension('lon0'), Dimension('lat0'),
                                Dimension('lon1'), Dimension('lat1')],
                       bounds=(4, 4), constant=True, doc="""
        The key dimensions of the Segments element represent the
        bottom-left (lon0, lat0) and top-right (lon1, lat1) coordinates
        of each segment.""")

    def geom(self, union=False, projection=None):
        """
        Converts the Segments to a shapely geometry.
        """
        lines = [LineString([(x0, y0), (x1, y1)]) for (x0, y0, x1, y1)
                 in self.array([0, 1, 2, 3])]
        nlines = len(lines)
        if not nlines:
            geom = GeometryCollection()
        elif nlines == 1:
            geom = lines[0]
        else:
            geom = MultiLineString(lines)
        if projection:
            geom = transform_shapely(geom, self.crs, projection)
        return unary_union(geom) if union else geom


class Shape(Dataset):
    """
    Shape wraps any shapely geometry type.
    """

    group = param.String(default='Shape')

    datatype = param.List(default=['geom_dictionary'])

    level = param.Number(default=None, doc="""
        Optional level associated with the set of Contours.""")

    vdims = param.List(default=[], doc="""
        Shape optionally accept a value dimension, corresponding
        to the supplied values.""", bounds=(0, None))

    def __init__(self, data, kdims=None, vdims=None, **params):
        if params.get('level') is not None:
            if vdims is None:
                vdims = [Dimension('Level')]
            self.param.warning('Supplying a level to a Shape is deprecated '
                         'provide the value as part of a dictionary of '
                         'the form {\'geometry\': <shapely.Geometry>, '
                         '\'level\': %s} instead' % params['level'])
        super().__init__(data, kdims=kdims, vdims=vdims, **params)


    @classmethod
    def from_shapefile(cls, shapefile, *args, **kwargs):
        """
        Loads a shapefile from disk and optionally merges
        it with a dataset. See ``from_records`` for full
        signature.

        Parameters
        ----------
        records: list of cartopy.io.shapereader.Record
           Iterator containing Records.
        dataset: holoviews.Dataset
           Any HoloViews Dataset type.
        on: str or list or dict
          A mapping between the attribute names in the records and the
          dimensions in the dataset.
        value: str
          The value dimension in the dataset the values will be drawn
          from.
        index: str or list
          One or more dimensions in the dataset the Shapes will be
          indexed by.
        drop_missing: boolean
          Whether to drop shapes which are missing from the provides
          dataset.

        Returns
        -------
        shapes: Polygons or Path object
          A Polygons or Path object containing the geometries
        """
        reader = Reader(shapefile)
        return cls.from_records(reader.records(), *args, **kwargs)


    @classmethod
    def from_records(cls, records, dataset=None, on=None, value=None,
                     index=[], drop_missing=False, element=None, **kwargs):
        """
        Load data from a collection of `cartopy.io.shapereader.Record`
        objects and optionally merge it with a dataset to assign
        values to each polygon and form a chloropleth. Supplying just
        records will return an NdOverlayof Shape Elements with a
        numeric index. If a dataset is supplied, a mapping between the
        attribute names in the records and the dimension names in the
        dataset must be supplied. The values assigned to each shape
        file can then be drawn from the dataset by supplying a
        ``value`` and keys the Shapes are indexed by specifying one or
        index dimensions.

        Parameters
        ----------
        records: list of cartopy.io.shapereader.Record
           Iterator containing Records.
        dataset: holoviews.Dataset
           Any HoloViews Dataset type.
        on: str or list or dict
          A mapping between the attribute names in the records and the
          dimensions in the dataset.
        value: str
          The value dimension in the dataset the values will be drawn
          from.
        index: str or list
          One or more dimensions in the dataset the Shapes will be
          indexed by.
        drop_missing: boolean
          Whether to drop shapes which are missing from the provides
          dataset.

        Returns
        -------
        shapes: Polygons or Path object
          A Polygons or Path object containing the geometries
        """
        if dataset is not None and not on:
            raise ValueError('To merge dataset with shapes mapping '
                             'must define attribute(s) to merge on.')

        if util.pd and isinstance(dataset, util.pd.DataFrame):
            dataset = Dataset(dataset)

        if not isinstance(on, (dict, list)):
            on = [on]
        if on and not isinstance(on, dict):
            on = {o: o for o in on}
        if not isinstance(index, list):
            index = [index]

        kdims = []
        for ind in index:
            if dataset and dataset.get_dimension(ind):
                dim = dataset.get_dimension(ind)
            else:
                dim = Dimension(ind)
            kdims.append(dim)


        ddims = []
        if dataset:
            if value:
                vdims = [dataset.get_dimension(value)]
            else:
                vdims = dataset.vdims
            ddims = dataset.dimensions()
            if None in vdims:
                raise ValueError('Value dimension {} not found '
                                 'in dataset dimensions {}'.format(value, ddims) )
        else:
            vdims = []

        data = []
        for i, rec in enumerate(records):
            geom = {}
            if dataset:
                selection = {dim: rec.attributes.get(attr, None)
                             for attr, dim in on.items()}
                row = dataset.select(**selection)
                if len(row):
                    values = {k: v[0] for k, v in row.iloc[0].columns().items()}
                elif drop_missing:
                    continue
                else:
                    values = {vd.name: np.nan for vd in vdims}
                geom.update(values)

            if index:
                for kdim in kdims:
                    if kdim in ddims and len(row):
                        k = row[kdim.name][0]
                    elif kdim.name in rec.attributes:
                        k = rec.attributes[kdim.name]
                    else:
                        k = None
                    geom[kdim.name] = k
            geom['geometry'] = rec.geometry
            data.append(geom)

        if element is not None:
            pass
        elif data and data[0]:
            if isinstance(data[0]['geometry'], poly_types):
                element = Polygons
            else:
                element = Path
        else:
            element = Polygons

        return element(data, vdims=kdims+vdims, **kwargs).opts(color=value)


    def geom(self, union=False, projection=None):
        """
        Returns the Shape as a shapely geometry

        Parameters
        ----------
        union: boolean (default=False)
            Whether to compute a union between the geometries
        projection : EPSG string | Cartopy CRS | None
            Whether to project the geometry to other coordinate system

        Returns
        -------
        A shapely geometry
        """
        geom = self.data['geometry']
        if projection:
            geom = transform_shapely(geom, self.crs, projection)
        return unary_union(geom) if union else geom
