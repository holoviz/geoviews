from __future__ import division

import warnings

import param
import numpy as np
import shapely.geometry as sgeom

from cartopy import crs as ccrs
from shapely.geometry import (MultiLineString, LineString, MultiPolygon,
                              Polygon, LinearRing, Point, MultiPoint)
from shapely.ops import cascaded_union
from holoviews.core.util import basestring

geom_types = (MultiLineString, LineString, MultiPolygon, Polygon,
              LinearRing, Point, MultiPoint)
line_types = (MultiLineString, LineString)
poly_types = (MultiPolygon, Polygon, LinearRing)


def wrap_lons(lons, base, period):
    """
    Wrap longitude values into the range between base and base+period.
    """
    lons = lons.astype(np.float64)
    return ((lons - base + period * 2) % period) + base


def project_extents(extents, src_proj, dest_proj, tol=1e-6):
    x1, y1, x2, y2 = extents

    if (isinstance(src_proj, ccrs.PlateCarree) and
        not isinstance(dest_proj, ccrs.PlateCarree) and
        src_proj.proj4_params['lon_0'] != 0):
        xoffset = src_proj.proj4_params['lon_0']
        x1 = x1 - xoffset
        x2 = x2 - xoffset
        src_proj = ccrs.PlateCarree()

    # Limit latitudes
    cy1, cy2 = src_proj.y_limits
    if y1 < cy1: y1 = cy1
    if y2 > cy2:  y2 = cy2

    # Offset with tolerances
    x1 += tol
    x2 -= tol
    y1 += tol
    y2 -= tol

    # Wrap longitudes
    cx1, cx2 = src_proj.x_limits
    if isinstance(src_proj, ccrs._CylindricalProjection):
        lons = wrap_lons(np.linspace(x1, x2, 10000), -180., 360.)
        x1, x2 = lons.min(), lons.max()
    else:
        if x1 < cx1: x1 = cx1
        if x2 > cx2: x2 = cx2

    domain_in_src_proj = Polygon([[x1, y1], [x2, y1],
                                  [x2, y2], [x1, y2],
                                  [x1, y1]])
    boundary_poly = Polygon(src_proj.boundary)
    dest_poly = src_proj.project_geometry(Polygon(dest_proj.boundary), dest_proj).buffer(0)
    if src_proj != dest_proj:
        # Erode boundary by threshold to avoid transform issues.
        # This is a workaround for numerical issues at the boundary.
        eroded_boundary = boundary_poly.buffer(-src_proj.threshold)
        geom_in_src_proj = eroded_boundary.intersection(
            domain_in_src_proj)
        try:
            geom_clipped_to_dest_proj = dest_poly.intersection(
                geom_in_src_proj)
        except:
            geom_clipped_to_dest_proj = None
        if geom_clipped_to_dest_proj:
            geom_in_src_proj = geom_clipped_to_dest_proj
        try:
            geom_in_crs = dest_proj.project_geometry(geom_in_src_proj, src_proj)
        except ValueError:
            src_name =type(src_proj).__name__
            dest_name =type(dest_proj).__name__
            raise ValueError('Could not project data from %s projection '
                             'to %s projection. Ensure the coordinate '
                             'reference system (crs) matches your data '
                             'and the kdims.' %
                             (src_name, dest_name))
    else:
        geom_in_crs = boundary_poly.intersection(domain_in_src_proj)
    return geom_in_crs.bounds


def geom_dict_to_array_dict(geom_dict, coord_names=['Longitude', 'Latitude']):
    """
    Converts a dictionary containing an geometry key to a dictionary
    of x- and y-coordinate arrays and if present a list-of-lists of
    hole array.
    """
    x, y = coord_names
    geom = geom_dict['geometry']
    new_dict = {k: v for k, v in geom_dict.items() if k != 'geometry'}
    array = geom_to_array(geom)
    new_dict[x] = array[:, 0]
    new_dict[y] = array[:, 1]
    if geom.geom_type == 'Polygon':
        holes = []
        for interior in geom.interiors:
            holes.append(geom_to_array(interior))
        if holes:
            new_dict['holes'] = [holes]
    elif geom.geom_type == 'MultiPolygon':
        outer_holes = []
        for g in geom:
            holes = []
            for interior in g.interiors:
                holes.append(geom_to_array(interior))
            outer_holes.append(holes)
        if any(hs for hs in outer_holes):
            new_dict['holes'] = outer_holes
    return new_dict


def path_to_geom(path, multi=True, skip_invalid=True):
    lines = []
    datatype = 'geom' if path.interface.datatype == 'geodataframe' else 'array'
    for path in path.split(datatype=datatype):
        if datatype == 'array':
            splits = np.where(np.isnan(path[:, :2].astype('float')).sum(axis=1))[0]
            paths = np.split(path, splits+1) if len(splits) else [path]
            for i, path in enumerate(paths):
                if i != (len(paths)-1):
                    path = path[:-1]
                if len(path) < 2:
                    continue
                lines.append(LineString(path[:, :2]))
            continue
        elif path.geom_type == 'MultiPolygon':
            for geom in path:
                lines.append(geom.exterior)
            continue
        elif path.geom_type == 'Polygon':
            path = path.exterior
        else:
            path = path
        if path.geom_type == 'MultiLineString':
            for geom in path:
                lines.append(geom)
        else:
            lines.append(path)
    return MultiLineString(lines) if multi else lines


def polygon_to_geom(poly, multi=True, skip_invalid=True):
    lines = []
    datatype = 'geom' if poly.interface.datatype == 'geodataframe' else 'array'
    for path in poly.split(datatype=datatype):
        if datatype == 'array':
            splits = np.where(np.isnan(path[:, :2].astype('float')).sum(axis=1))[0]
            paths = np.split(path, splits+1) if len(splits) else [path]
            for i, path in enumerate(paths):
                if i != (len(paths)-1):
                    path = path[:-1]
                geom = Polygon
                if len(path) < 3:
                    if skip_invalid:
                        continue
                    geom = LineString
                lines.append(geom(path[:, :2]))
        elif path.geom_type == 'MultiLineString':
            for geom in path:
                lines.append(geom.convex_hull)
        elif path.geom_type == 'MultiPolygon':
            for geom in path:
                lines.append(geom)
        elif path.geom_type == 'LineString':
            lines.append(path.convex_hull)
        else:
            lines.append(path)
    return MultiPolygon(lines) if multi else lines


def polygons_to_geom_dicts(polygons, skip_invalid=True):
    """
    Converts a Polygons element into a list of geometry dictionaries,
    preserving all value dimensions.

    For array conversion the following conventions are applied:

    * Any nan separated array are converted into a MultiPolygon
    * Any array without nans is converted to a Polygon
    * If there are holes associated with a nan separated array
      the holes are assigned to the polygons by testing for an
      intersection
    * If any single array does not have at least three coordinates
      it is skipped by default
    * If skip_invalid=False and an array has less than three
      coordinates it will be converted to a LineString
    """
    interface = polygons.interface.datatype
    if interface == 'geodataframe':
        return [row.to_dict() for _, row in polygons.data.iterrows()]
    elif interface == 'geom_dictionary':
        return polygons.data

    polys = []
    xdim, ydim = polygons.kdims
    has_holes = polygons.has_holes
    holes = polygons.holes() if has_holes else None
    for i, polygon in enumerate(polygons.split(datatype='columns')):
        array = np.column_stack([polygon.pop(xdim.name), polygon.pop(ydim.name)])
        splits = np.where(np.isnan(array[:, :2].astype('float')).sum(axis=1))[0]
        arrays = np.split(array, splits+1) if len(splits) else [array]

        invalid = False
        subpolys = []
        subholes = None
        if has_holes:
            subholes = [[LinearRing(h) for h in hs] for hs in holes[i]]
        for j, arr in enumerate(arrays):
            if j != (len(arrays)-1):
                arr = arr[:-1] # Drop nan

            if len(arr) == 0:
                continue
            elif len(arr) == 1:
                if skip_invalid:
                    continue
                poly = Point(arr[0])
                invalid = True
            elif len(arr) == 2:
                if skip_invalid:
                    continue
                poly = LineString(arr)
                invalid = True
            elif not len(splits):
                poly = Polygon(arr, (subholes[j] if has_holes else []))
            else:
                poly = Polygon(arr)
                hs = [h for h in subholes[j]] if has_holes else []
                poly = Polygon(poly.exterior, holes=hs)
            subpolys.append(poly)

        if invalid:
            polys += [dict(polygon, geometry=sp) for sp in subpolys]
            continue
        elif len(subpolys) == 1:
            geom = subpolys[0]
        elif subpolys:
            geom = MultiPolygon(subpolys)
        else:
            continue
        polygon['geometry'] = geom
        polys.append(polygon)
    return polys


def path_to_geom_dicts(path, skip_invalid=True):
    """
    Converts a Path element into a list of geometry dictionaries,
    preserving all value dimensions.
    """
    interface = path.interface.datatype
    if interface == 'geodataframe':
        return [row.to_dict() for _, row in path.data.iterrows()]
    elif interface == 'geom_dictionary':
        return path.data

    geoms = []
    invalid = False
    xdim, ydim = path.kdims
    for i, path in enumerate(path.split(datatype='columns')):
        array = np.column_stack([path.pop(xdim.name), path.pop(ydim.name)])
        splits = np.where(np.isnan(array[:, :2].astype('float')).sum(axis=1))[0]
        arrays = np.split(array, splits+1) if len(splits) else [array]
        subpaths = []
        for j, arr in enumerate(arrays):
            if j != (len(arrays)-1):
                arr = arr[:-1] # Drop nan

            if len(arr) == 0:
                continue
            elif len(arr) == 1:
                if skip_invalid:
                    continue
                g = Point(arr[0])
                invalid = True
            else:
                g = LineString(arr)
            subpaths.append(g)

        if invalid:
            geoms += [dict(path, geometry=sp) for sp in subpaths]
            continue
        elif len(subpaths) == 1:
            geom = subpaths[0]
        elif subpaths:
            geom = MultiLineString(subpaths)
        path['geometry'] = geom
        geoms.append(path)
    return geoms


def to_ccw(geom):
    """
    Reorients polygon to be wound counter-clockwise.
    """
    if isinstance(geom, sgeom.Polygon) and not geom.exterior.is_ccw:
        geom = sgeom.polygon.orient(geom)
    return geom


def geom_to_arr(geom):
    try:
        xy = getattr(geom, 'xy', None)
    except NotImplementedError:
        xy = None
    if xy is not None:
        return np.column_stack(xy)
    if hasattr(geom, 'array_interface'):
        data = geom.array_interface()
        return np.array(data['data']).reshape(data['shape'])[:, :2]
    arr = geom.array_interface_base['data']
    if (len(arr) % 2) != 0:
        arr = arr[:-1]
    return np.array(arr).reshape(int(len(arr)/2), 2)


def geom_length(geom):
    """
    Calculates the length of coordinates in a shapely geometry.
    """
    if geom.geom_type == 'Point':
        return 1
    if hasattr(geom, 'exterior'):
        geom = geom.exterior
    if not geom.geom_type.startswith('Multi') and hasattr(geom, 'array_interface_base'):
        return len(geom.array_interface_base['data'])//2
    else:
        length = 0
        for g in geom:
            length += geom_length(g)
        return length


def geom_to_array(geom):
    if geom.geom_type == 'Point':
        return np.array([[geom.x, geom.y]])
    if hasattr(geom, 'exterior'):
        if geom.exterior is None:
            xs, ys = np.array([]), np.array([])
        else:
            xs = np.array(geom.exterior.coords.xy[0])
            ys = np.array(geom.exterior.coords.xy[1])
    elif geom.geom_type in ('LineString', 'LinearRing'):
        arr = geom_to_arr(geom)
        return arr
    else:
        xs, ys = [], []
        for g in geom:
            arr = geom_to_arr(g)
            xs.append(arr[:, 0])
            ys.append(arr[:, 1])
            xs.append([np.NaN])
            ys.append([np.NaN])
        xs = np.concatenate(xs[:-1]) if xs else np.array([])
        ys = np.concatenate(ys[:-1]) if ys else np.array([])
    return np.column_stack([xs, ys])


def geo_mesh(element):
    """
    Get mesh data from a 2D Element ensuring that if the data is
    on a cylindrical coordinate system and wraps globally that data
    actually wraps around.
    """
    if len(element.vdims) > 1:
        xs, ys = (element.dimension_values(i, False, False)
                  for i in range(2))
        zs = np.dstack([element.dimension_values(i, False, False)
                        for i in range(2, 2+len(element.vdims))])
    else:
        xs, ys, zs = (element.dimension_values(i, False, False)
                      for i in range(3))
    lon0, lon1 = element.range(0)
    if isinstance(element.crs, ccrs._CylindricalProjection) and (lon1 - lon0) == 360:
        xs = np.append(xs, xs[0:1] + 360, axis=0)
        zs = np.ma.concatenate([zs, zs[:, 0:1]], axis=1)
    return xs, ys, zs


def is_multi_geometry(geom):
    """
    Whether the shapely geometry is a Multi or Collection type.
    """
    return 'Multi' in geom.geom_type or 'Collection' in geom.geom_type


def check_crs(crs):
    """
    Checks if the crs represents a valid grid, projection or ESPG string.

    (Code copied from https://github.com/fmaussion/salem)

    Examples
    --------
    >>> p = check_crs('+units=m +init=epsg:26915')
    >>> p.srs
    '+units=m +init=epsg:26915 '
    >>> p = check_crs('wrong')
    >>> p is None
    True
    Returns
    -------
    A valid crs if possible, otherwise None
    """
    import pyproj
    if isinstance(crs, pyproj.Proj):
        out = crs
    elif isinstance(crs, dict) or isinstance(crs, basestring):
        try:
            out = pyproj.Proj(crs)
        except RuntimeError:
            try:
                out = pyproj.Proj(init=crs)
            except RuntimeError:
                out = None
    else:
        out = None
    return out


def proj_to_cartopy(proj):
    """
    Converts a pyproj.Proj to a cartopy.crs.Projection

    (Code copied from https://github.com/fmaussion/salem)

    Parameters
    ----------
    proj: pyproj.Proj
        the projection to convert
    Returns
    -------
    a cartopy.crs.Projection object
    """

    import cartopy.crs as ccrs
    try:
        from osgeo import osr
        has_gdal = True
    except ImportError:
        has_gdal = False

    proj = check_crs(proj)

    if proj.is_latlong():
        return ccrs.PlateCarree()

    srs = proj.srs
    if has_gdal:
        # this is more robust, as srs could be anything (espg, etc.)
        s1 = osr.SpatialReference()
        s1.ImportFromProj4(proj.srs)
        srs = s1.ExportToProj4()

    km_proj = {'lon_0': 'central_longitude',
               'lat_0': 'central_latitude',
               'x_0': 'false_easting',
               'y_0': 'false_northing',
               'k': 'scale_factor',
               'zone': 'zone',
               }
    km_globe = {'a': 'semimajor_axis',
                'b': 'semiminor_axis',
                }
    km_std = {'lat_1': 'lat_1',
              'lat_2': 'lat_2',
              }
    kw_proj = dict()
    kw_globe = dict()
    kw_std = dict()
    for s in srs.split('+'):
        s = s.split('=')
        if len(s) != 2:
            continue
        k = s[0].strip()
        v = s[1].strip()
        try:
            v = float(v)
        except:
            pass
        if k == 'proj':
            if v == 'tmerc':
                cl = ccrs.TransverseMercator
            if v == 'lcc':
                cl = ccrs.LambertConformal
            if v == 'merc':
                cl = ccrs.Mercator
            if v == 'utm':
                cl = ccrs.UTM
        if k in km_proj:
            kw_proj[km_proj[k]] = v
        if k in km_globe:
            kw_globe[km_globe[k]] = v
        if k in km_std:
            kw_std[km_std[k]] = v

    globe = None
    if kw_globe:
        globe = ccrs.Globe(**kw_globe)
    if kw_std:
        kw_proj['standard_parallels'] = (kw_std['lat_1'], kw_std['lat_2'])

    # mercatoooor
    if cl.__name__ == 'Mercator':
        kw_proj.pop('false_easting', None)
        kw_proj.pop('false_northing', None)

    return cl(globe=globe, **kw_proj)


def process_crs(crs):
    """
    Parses cartopy CRS definitions defined in one of a few formats:

      1. EPSG codes:   Defined as string of the form "EPSG: {code}" or an integer
      2. proj.4 string: Defined as string of the form "{proj.4 string}"
      3. cartopy.crs.CRS instance
      4. None defaults to crs.PlateCaree
    """
    try:
        import cartopy.crs as ccrs
        import geoviews as gv # noqa
        import pyproj
    except:
        raise ImportError('Geographic projection support requires GeoViews and cartopy.')

    if crs is None:
        return ccrs.PlateCarree()

    if isinstance(crs, basestring) and crs.lower().startswith('epsg'):
        try:
            crs = ccrs.epsg(crs[5:].lstrip().rstrip())
        except:
            raise ValueError("Could not parse EPSG code as CRS, must be of the format 'EPSG: {code}.'")
    elif isinstance(crs, int):
        crs = ccrs.epsg(crs)
    elif isinstance(crs, (basestring, pyproj.Proj)):
        try:
            crs = proj_to_cartopy(crs)
        except:
            raise ValueError("Could not parse EPSG code as CRS, must be of the format 'proj4: {proj4 string}.'")
    elif not isinstance(crs, ccrs.CRS):
        raise ValueError("Projection must be defined as a EPSG code, proj4 string, cartopy CRS or pyproj.Proj.")
    return crs


def load_tiff(filename, crs=None, apply_transform=False, nan_nodata=False, **kwargs):
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
    try:
        import xarray as xr
    except:
        raise ImportError('Loading tiffs requires xarray to be installed')

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        da = xr.open_rasterio(filename)
    return from_xarray(da, crs, apply_transform, nan_nodata, **kwargs)


def from_xarray(da, crs=None, apply_transform=False, nan_nodata=False, **kwargs):
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
    if crs:
        kwargs['crs'] = crs
    elif hasattr(da, 'crs'):
        try:
            kwargs['crs'] = process_crs(da.crs)
        except:
            param.main.warning('Could not decode projection from crs string %r, '
                               'defaulting to non-geographic element.' % da.crs)

    coords = list(da.coords)
    if coords not in (['band', 'y', 'x'], ['y', 'x']):
        from .element.geo import Dataset, HvDataset
        el = Dataset if 'crs' in kwargs else HvDataset
        return el(da, **kwargs)

    if len(coords) == 2:
        y, x = coords
        bands = 1
    else:
        y, x = coords[1:]
        bands = len(da.coords[coords[0]])

    if apply_transform:
        from affine import Affine
        transform = Affine.from_gdal(*da.attrs['transform'][:6])
        nx, ny = da.sizes[x], da.sizes[y]
        xs, ys = np.meshgrid(np.arange(nx)+0.5, np.arange(ny)+0.5) * transform
        data = (xs, ys)
    else:
        xres, yres = da.attrs['res'] if 'res' in da.attrs else (1, 1)
        xs = da.coords[x][::-1] if xres < 0 else da.coords[x]
        ys = da.coords[y][::-1] if yres < 0 else da.coords[y]

    data = (xs, ys)
    for b in range(bands):
        values = da[b].values
        if nan_nodata and da.attrs.get('nodatavals', []):

            values = values.astype(float)
            for d in da.attrs['nodatavals']:
                values[values==d] = np.NaN
        data += (values,)

    if 'datatype' not in kwargs:
        kwargs['datatype'] = ['xarray', 'grid', 'image']

    if xs.ndim > 1:
        from .element.geo import QuadMesh, HvQuadMesh
        el = QuadMesh if 'crs' in kwargs else HvQuadMesh
        el = el(data, [x, y], **kwargs)
    elif bands < 3:
        from .element.geo import Image, HvImage
        el = Image if 'crs' in kwargs else HvImage
        el = el(data, [x, y], **kwargs)
    else:
        from .element.geo import RGB, HvRGB
        el = RGB if 'crs' in kwargs else HvRGB
        vdims = el.vdims[:bands]
        el = el(data, [x, y], vdims, **kwargs)
    if hasattr(el.data, 'attrs'):
        el.data.attrs = da.attrs
    return el


def geohash_to_polygon(geo):
    """
    :param geo: String that represents the geohash.
    :return: Returns a Shapely's Polygon instance that represents the geohash.
    """
    import geohash
    
    lat_centroid, lng_centroid, lat_offset, lng_offset = geohash.decode_exactly(geo)

    corner_1 = (lat_centroid - lat_offset, lng_centroid - lng_offset)[::-1]
    corner_2 = (lat_centroid - lat_offset, lng_centroid + lng_offset)[::-1]
    corner_3 = (lat_centroid + lat_offset, lng_centroid + lng_offset)[::-1]
    corner_4 = (lat_centroid + lat_offset, lng_centroid - lng_offset)[::-1]

    return sgeom.Polygon([corner_1, corner_2, corner_3, corner_4, corner_1])
