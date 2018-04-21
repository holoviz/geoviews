import numpy as np
from cartopy import crs as ccrs
from shapely.geometry import (MultiLineString, LineString, MultiPolygon, Polygon)



def wrap_lons(lons, base, period):
    """
    Wrap longitude values into the range between base and base+period.
    """
    lons = lons.astype(np.float64)
    return ((lons - base + period * 2) % period) + base


def project_extents(extents, src_proj, dest_proj, tol=1e-6):
    x1, y1, x2, y2 = extents

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
    if src_proj != dest_proj:
        # Erode boundary by threshold to avoid transform issues.
        # This is a workaround for numerical issues at the boundary.
        eroded_boundary = boundary_poly.buffer(-src_proj.threshold)
        geom_in_src_proj = eroded_boundary.intersection(
            domain_in_src_proj)
        try:
            geom_in_crs = dest_proj.project_geometry(geom_in_src_proj, src_proj)
        except ValueError:
            src_name =type(src_proj).__name__
            dest_name =type(dest_proj).__name__
            raise ValueError('Could not project data from %s projection '
                             'to %s projection. Ensure the coordinate '
                             'reference system (crs) matches your data.' %
                             (src_name, dest_name))
    else:
        geom_in_crs = boundary_poly.intersection(domain_in_src_proj)
    return geom_in_crs.bounds


def path_to_geom(path, multi=True):
    lines = []
    datatype = 'geom' if path.interface.datatype == 'geodataframe' else 'array'
    for path in path.split(datatype=datatype):
        if datatype == 'array':
            splits = np.where(np.isnan(path).sum(axis=1))[0]
            paths = np.split(path, splits+1) if len(splits) else [path]
            for i, path in enumerate(paths):
                if i != (len(paths)-1):
                    path = path[:-1]
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


def polygon_to_geom(poly, multi=True):
    lines = []
    datatype = 'geom' if poly.interface.datatype == 'geodataframe' else 'array'
    for path in poly.split(datatype=datatype):
        if datatype == 'array':
            splits = np.where(np.isnan(path[:, :2]).sum(axis=1))[0]
            paths = np.split(path, splits+1) if len(splits) else [path]
            for i, path in enumerate(paths):
                if i != (len(paths)-1):
                    path = path[:-1]
                lines.append(Polygon(path[:, :2]))
            continue
        elif path.geom_type == 'MultiLineString':
            for geom in path:
                lines.append(geom.convex_hull)
            continue
        elif path.geom_type == 'MultiPolygon':
            for geom in path:
                lines.append(geom)
            continue
        elif path.geom_type == 'LineString':
            path = path.convex_hull
        else:
            path = path
        lines.append(path)
    return MultiPolygon(lines) if multi else lines


def geom_to_arr(geom):
    arr = geom.array_interface_base['data']
    return np.array(arr).reshape(int(len(arr)/2), 2)


def geom_to_array(geom):
    if hasattr(geom, 'exterior'):
        xs = np.array(geom.exterior.coords.xy[0])
        ys = np.array(geom.exterior.coords.xy[1])
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

