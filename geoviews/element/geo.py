import param
import numpy as np
from cartopy import crs as ccrs
from cartopy.feature import Feature as cFeature
from cartopy.io.img_tiles import GoogleTiles as cGoogleTiles
from cartopy.io.shapereader import Reader
from holoviews.core import Element2D, Dimension, Dataset, NdOverlay
from holoviews.core.util import basestring
from holoviews.element import (Text as HVText, Path as HVPath,
                               Polygons as HVPolygons)

from shapely.geometry.base import BaseGeometry
from shapely.geometry import (MultiLineString, LineString,
                              MultiPolygon, Polygon)

try:
    from iris.cube import Cube
except ImportError:
    Cube = None

try:
    from bokeh.models import WMTSTileSource
except:
    WMTSTileSource = None

geographic_types = (cGoogleTiles, cFeature)

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

    if len(kdims) != 2:
        return False
    if Cube and isinstance(element.data, Cube):
        return all(element.data.coord(kd.name).coord_system for kd in kdims)
    elif isinstance(element.data, geographic_types) or isinstance(element, WMTS):
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

    crs = param.ClassSelector(class_=ccrs.CRS, doc="""
        Cartopy coordinate-reference-system specifying the
        coordinate system of the data. Inferred automatically
        when _Element wraps cartopy Feature object.""")

    kdims = param.List(default=[Dimension('Longitude'), Dimension('Latitude')])

    def __init__(self, data, **kwargs):
        crs = None
        crs_data = data.data if isinstance(data, Dataset) else data
        if isinstance(crs_data, Cube):
            coord_sys = crs_data.coord_system()
            if hasattr(coord_sys, 'as_cartopy_projection'):
                crs = coord_sys.as_cartopy_projection()
        elif isinstance(crs_data, (cFeature, cGoogleTiles)):
            crs = crs_data.crs

        supplied_crs = kwargs.get('crs', None)
        if supplied_crs and crs and crs != supplied_crs:
            raise ValueError('Supplied coordinate reference '
                             'system must match crs of the data.')
        elif crs:
            kwargs['crs'] = crs
        super(_Element, self).__init__(data, **kwargs)
        if not is_geographic(self, self.kdims):
            self.crs = None


    def clone(self, data=None, shared_data=True, new_type=None,
              *args, **overrides):
        if 'crs' not in overrides:
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

    def __init__(self, data, **params):
        if not isinstance(data, cFeature):
            raise TypeError('%s data has to be an cartopy Feature type'
                            % type(data).__name__)
        super(Feature, self).__init__(data, **params)


class WMTS(_GeoFeature):
    """
    The WMTS Element represents a Web Map Tile Service
    specified as a tuple of the API URL and
    """

    group = param.String(default='WMTS')

    layer = param.String(doc="The layer on the tile service")

    def __init__(self, data, **params):
        if isinstance(data, tuple):
            data = data
        else:
            data = (data,)

        for d in data:
            if WMTSTileSource and isinstance(d, WMTSTileSource):
                if 'crs' not in params:
                    params['crs'] = ccrs.GOOGLE_MERCATOR
            elif not isinstance(data, basestring):
                raise TypeError('%s data has to be a tile service URL'
                                % type(data).__name__)
        super(WMTS, self).__init__(data, **params)


class Tiles(_GeoFeature):
    """
    Tiles represents an image tile source to dynamically
    load data from depending on the zoom level.
    """

    group = param.String(default='Tiles')

    def __init__(self, data, **params):
        if not isinstance(data, cGoogleTiles):
            raise TypeError('%s data has to be a cartopy GoogleTiles type'
                            % type(data).__name__)
        super(Tiles, self).__init__(data, **params)


class Points(_Element, Dataset):
    """
    Points represent a collection of points with
    an associated cartopy coordinate-reference system.
    """

    group = param.String(default='Points')


class LineContours(_Element, Dataset):
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


class Image(_Element, Dataset):
    """
    Image represents a 2D array of some quantity with
    some associated coordinates.
    """

    vdims = param.List(default=[Dimension('z')], bounds=(1, 1))

    group = param.String(default='Image')


class Text(HVText, _Element):
    """
    An annotation containing some text at an x, y coordinate
    along with a coordinate reference system.
    """


class Path(_Element, HVPath):
    """
    The Path Element contains a list of Paths stored as Nx2 numpy
    arrays along with a coordinate reference system.
    """

    def geom(self):
        """
        Returns Path as a shapely geometry.
        """
        lines = []
        for path in self.data:
            lines.append(LineString(path))
        return MultiLineString(lines)


class Polygons(_Element, HVPolygons):
    """
    Polygons is a Path Element type that may contain any number of
    closed paths with an associated value and a coordinate reference
    system.
    """

    def geom(self):
        """
        Returns Polygons as a shapely geometry.
        """
        polys = []
        for poly in self.data:
            polys.append(Polygon(poly))
        return MultiPolygon(polys)


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

    def __init__(self, data, **params):
        if not isinstance(data, BaseGeometry):
            raise TypeError('%s data has to be a shapely geometry type.'
                            % type(data).__name__)
        super(Shape, self).__init__(data, **params)


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
                     value=None, index=[], **kwargs):
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

        Returns an NdOverlay of Shapes.
        """
        if dataset and not on:
            raise ValueError('To merge dataset with shapes mapping '
                             'must define attribute(s) to merge on.')

        if not isinstance(on, (dict, list)):
            on = [on]
        if on and not isinstance(on, dict):
            on = {o: o for o in on}
        if not isinstance(index, list):
            index = [index]

        if dataset:
            index = [dataset.get_dimension(ind) for ind in index]
            vdim = dataset.get_dimension(value)
            kwargs['vdims'] = [vdim]
            not_found = [dim.name for dim in index+[vdim]
                         if dim is None]
            if not_found:
                dim_str = ', '.join(not_found)
                raise ValueError('Following dimensions not found '
                                 'in dataset: {}'.format(dim_str))

        chloropleth = NdOverlay(kdims=index if index else ['Index'])
        for i, rec in enumerate(records):
            if dataset:
                selection = {dim: rec.attributes.get(attr, None)
                             for attr, dim in on.items()}
                row = dataset.select(**selection)
                if not len(row):
                    continue
                if value:
                    value = row[vdim.name][0]
                    kwargs['level'] = value
                if index:
                    key = tuple(row[d.name][0] for d in index)
                else:
                    key = i
            else:
                key = i
            chloropleth[key] = Shape(rec.geometry, **kwargs)
        return chloropleth


    def dimension_values(self, dimension):
        """
        Shapes do not support convert to array values.
        """
        dim = self.get_dimension(dimension)
        if dim in self.vdims:
            return [self.level]
        else:
            return []


    def range(self, dimension):
        dim = self.get_dimension(dimension)
        if dim.range != (None, None):
            return dim.range

        idx = self.get_dimension_index(dimension)
        if idx == 2:
            return self.level, self.level
        if idx in [0, 1]:
            l, b, r, t = self.data.bounds
            if idx == 0:
                return l, r
            elif idx == 1:
                return b, t
        else:
            return (np.NaN, np.NaN)


    def geom(self):
        """
        Returns Shape as a shapely geometry
        """
        return self.data
