import warnings

import numpy as np
import param
import shapely
import shapely.geometry as sgeom
from cartopy import crs as ccrs
from cartopy.io.img_tiles import GoogleTiles, QuadtreeTiles
from holoviews.element import Tiles
from packaging.version import Version
from shapely.geometry import (
    LinearRing, LineString, MultiLineString, MultiPoint,
    MultiPolygon, Point, Polygon, box
)
from shapely.geometry.base import BaseMultipartGeometry
from shapely.ops import transform

from ._warnings import deprecated

geom_types = (MultiLineString, LineString, MultiPolygon, Polygon,
              LinearRing, Point, MultiPoint)
line_types = (MultiLineString, LineString)
poly_types = (MultiPolygon, Polygon, LinearRing)


shapely_version = Version(shapely.__version__)
shapely_v2 = shapely_version >= Version("2")


def wrap_lons(lons, base, period):
    """
    Wrap longitude values into the range between base and base+period.
    """
    lons = lons.astype(np.float64)
    return ((lons - base + period * 2) % period) + base


def expand_geoms(geoms):
    """
    Expands multi-part geometries in a list of geometries.
    """
    expanded = []
    for geom in geoms:
        if isinstance(geom, BaseMultipartGeometry):
            expanded.extend(list(geom))
        else:
            expanded.append(geom)
    return expanded


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
        except Exception:
            geom_clipped_to_dest_proj = None
        if geom_clipped_to_dest_proj:
            geom_in_src_proj = geom_clipped_to_dest_proj
        try:
            geom_in_crs = dest_proj.project_geometry(geom_in_src_proj, src_proj)
        except ValueError:
            src_name =type(src_proj).__name__
            dest_name =type(dest_proj).__name__
            raise ValueError(
                f'Could not project data from {src_name} projection '
                f'to {dest_name} projection. Ensure the coordinate '
                'reference system (crs) matches your data and the kdims.'
            )
    else:
        geom_in_crs = boundary_poly.intersection(domain_in_src_proj)
    return geom_in_crs.bounds


def zoom_level(bounds, width, height):
    """
    Compute zoom level given bounds and the plot size.
    """
    w, s, e, n = bounds
    max_width, max_height = 256, 256
    ZOOM_MAX = 21
    ln2 = np.log(2)

    def latRad(lat):
        sin = np.sin(lat * np.pi / 180)
        radX2 = np.log((1 + sin) / (1 - sin)) / 2
        return np.max([np.min([radX2, np.pi]), -np.pi]) / 2

    def zoom(mapPx, worldPx, fraction):
        return np.floor(np.log(mapPx / worldPx / fraction) / ln2)

    latFraction = (latRad(n) - latRad(s)) / np.pi

    lngDiff = e - w
    lngFraction = ((lngDiff + 360) if lngDiff < 0 else lngDiff) / 360

    latZoom = zoom(height, max_height, latFraction)
    lngZoom = zoom(width, max_width, lngFraction)
    zoom = np.min([latZoom, lngZoom, ZOOM_MAX])
    return int(zoom) if np.isfinite(zoom) else 0


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
        for g in geom.geoms:
            holes = []
            for interior in g.interiors:
                holes.append(geom_to_array(interior))
            outer_holes.append(holes)
        if any(hs for hs in outer_holes):
            new_dict['holes'] = outer_holes
    return new_dict


def unpack_geoms(geom_el):
    """
    Unpacks the data in a geometry element if it is already in a
    geometry format.
    """
    interface = geom_el.interface
    if interface.datatype in  ('geodataframe', 'spatialpandas'):
        geom_col = interface.geo_column(geom_el.data)
        geoms = []
        for _, row in geom_el.data.iterrows():
            row = row.to_dict()
            if interface.datatype  == 'spatialpandas':
                row['geometry'] = row[geom_col].to_shapely()
            else:
                row['geometry'] = row[geom_col]
            geoms.append(row)
        return geoms
    elif interface.datatype == 'geom_dictionary':
        return [geom_el.data]
    elif (interface.datatype == 'multitabular' and
          all(isinstance(p, dict) and 'geometry' in p for p in geom_el.data)):
        return geom_el.data


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
    geoms = unpack_geoms(polygons)
    if geoms is not None:
        return geoms

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
    geoms = unpack_geoms(path)
    if geoms is not None:
        return geoms

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
        else:
            continue
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
    """
    LineString, LinearRing and Polygon (exterior only?)
    """
    # LineString and LinearRing geoms have an xy attribute
    try:
        xy = getattr(geom, 'xy', None)
    except NotImplementedError:
        xy = None
    if xy is not None:
        return np.column_stack(xy)

    # Polygon
    # shapely 1.8.0 deprecated `array_interface` and
    # unfortunately also introduced a bug in the `array_interface_base`
    # property which raised an error as soon as it was called.
    if shapely_version < Version('1.8.0'):
        if hasattr(geom, 'array_interface'):
            data = geom.array_interface()
            return np.array(data['data']).reshape(data['shape'])[:, :2]
        arr = geom.array_interface_base['data']
    else:
        arr = np.asarray(geom.exterior.coords)

    if (len(arr) % 2) != 0:
        arr = arr[:-1]
    return np.array(arr).reshape(-1, 2)


def geom_length(geom):
    """
    Calculates the length of coordinates in a shapely geometry.
    """
    if geom.geom_type == 'Point':
        return 1
    # Polygon
    if hasattr(geom, 'exterior'):
        geom = geom.exterior
    # As of shapely 1.8.0: LineString, LinearRing (and GeometryCollection?)
    if shapely_version < Version('1.8.0'):
        if not geom.geom_type.startswith('Multi') and hasattr(geom, 'array_interface_base'):
            return len(geom.array_interface_base['data'])//2
    elif not geom.geom_type.startswith('Multi'):
        return len(geom.coords)
    # MultiPolygon, MultiPoint, MultiLineString (recursively)
    glength = len(geom.geoms)
    length = 0
    for i, g in enumerate(geom.geoms):
        length += geom_length(g)
        if 'Point' not in geom.geom_type and (i+1 != glength):
            length += 1

    return length


def geom_to_array(geom):
    """
    Convert the coords of a shapely Geometry to a numpy array.
    """
    if geom.geom_type == 'Point':
        return np.array([[geom.x, geom.y]])
    # Only Polygon as of shapely 1.8.0
    if hasattr(geom, 'exterior'):
        if geom.exterior is None:
            xs, ys = np.array([]), np.array([])
        else:
            xs = np.array(geom.exterior.coords.xy[0])
            ys = np.array(geom.exterior.coords.xy[1])
    elif geom.geom_type in ('LineString', 'LinearRing'):
        return geom_to_arr(geom)
    elif geom.geom_type == 'MultiPoint':
        arrays = []
        for g in geom.geoms:
            if g.geom_type == 'Point':
                arrays.append(np.array(g.xy).T)
        return np.concatenate(arrays) if arrays else np.array([])
    else:
        # As of shapely 1.8.0, that would leave:
        # MultiLineString, MultiPolygon (and GeometryCollection?)
        arrays = []
        for g in geom.geoms:
            arrays.append(geom_to_arr(g))
            arrays.append(np.array([[np.nan, np.nan]]))
        return np.concatenate(arrays[:-1]) if arrays else np.array([])
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
    '+proj=utm +zone=15 +datum=NAD83 +units=m +no_defs'
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
    elif isinstance(crs, (str, dict)):
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

    if hasattr(proj, 'crs'):
        if proj.crs.is_geographic:
            return ccrs.PlateCarree()
    elif proj.is_latlong(): # pyproj < 2.0
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
    kw_proj = {}
    kw_globe = {}
    kw_std = {}
    for s in srs.split('+'):
        s = s.split('=')
        if len(s) != 2:
            continue
        k = s[0].strip()
        v = s[1].strip()
        try:
            v = float(v)
        except Exception:
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


def is_pyproj(crs):
    import pyproj
    return isinstance(crs, pyproj.Proj)


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
    except ImportError:
        raise ImportError('Geographic projection support requires GeoViews and cartopy.')

    if crs is None:
        return ccrs.PlateCarree()

    if isinstance(crs, str) and crs.lower().startswith('epsg'):
        try:
            crs = ccrs.epsg(crs[5:].lstrip().rstrip())
        except Exception:
            raise ValueError("Could not parse EPSG code as CRS, must be of the format 'EPSG: {code}.'")
    elif isinstance(crs, int):
        crs = ccrs.epsg(crs)
    elif isinstance(crs, str) or is_pyproj(crs):
        try:
            crs = proj_to_cartopy(crs)
        except Exception:
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
    new = (
        "geoviews.util.from_xarray(rioxarray.open_rasterio(filename))"
    )
    try:
        import xarray as xr
    except ImportError:
        raise ImportError('Loading tiffs requires xarray to be installed')
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            da = xr.open_rasterio(filename)
        deprecated("1.11", "load_tiff(filename)", new)
        return from_xarray(da, crs, apply_transform, nan_nodata, **kwargs)
    except AttributeError as e:
        raise ImportError(
            f"'load_tiff' is not supported anymore. Use {new!r} instead."
        ) from e

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
        except Exception:
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


def get_tile_rgb(tile_source, bbox, zoom_level, bbox_crs=ccrs.PlateCarree()):
    """
    Returns an RGB element given a tile_source, bounding box and zoom level.

    Parameters
    ----------
    tile_source: WMTS element or string URL
      The tile source to download the tiles from.
    bbox: tuple
      A four tuple specifying the (left, bottom, right, top) corners of the
      domain to download the tiles for.
    zoom_level: int
      The zoom level at which to download the tiles
    bbox_crs: ccrs.CRs
      cartopy CRS defining the coordinate system of the supplied bbox

    Returns
    -------
    RGB element containing the tile data in the specified bbox
    """

    from .element import RGB, WMTS
    if isinstance(tile_source, (WMTS, Tiles)):
        tile_source = tile_source.data

    if bbox_crs is not ccrs.GOOGLE_MERCATOR:
        bbox = project_extents(bbox, bbox_crs, ccrs.GOOGLE_MERCATOR)

    if '{Q}' in tile_source:
        tile_source = QuadtreeTiles(url=tile_source.replace('{Q}', '{tile}'))
    else:
        tile_source = GoogleTiles(url=tile_source)

    bounds = box(*bbox)
    rgb, extent, orient = tile_source.image_for_domain(bounds, zoom_level)
    if orient == 'lower':
        rgb = rgb[::-1]
    x0, x1, y0, y1 = extent
    l, b, r, t = bbox
    return RGB(
        rgb, bounds=(x0, y0, x1, y1), crs=ccrs.GOOGLE_MERCATOR, vdims=['R', 'G', 'B'],
    ).clone(datatype=['grid', 'xarray', 'iris'])[l:r, b:t]


def asarray(v):
    """Convert input to array

    First it tries with a normal `np.asarray(v)` if this does not work
    it tries with `np.asarray(v, dtype=object)`.

    The ValueError raised is because of an inhomogeneous shape of the input,
    which raises an error in numpy v1.24 and above.

    """
    try:
        return np.asarray(v)
    except ValueError:
        return np.asarray(v, dtype=object)


def transform_shapely(geom, crs_from, crs_to):
    from pyproj import Transformer

    if isinstance(crs_to, str):
        crs_to = ccrs.CRS(crs_to)
    if isinstance(crs_from, str):
        crs_from = ccrs.CRS(crs_from)
    project = Transformer.from_crs(crs_from, crs_to).transform
    return transform(project, geom)
