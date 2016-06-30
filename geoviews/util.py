import numpy as np
from shapely.geometry import (MultiLineString, LineString,
                              MultiPolygon, Polygon)


def project_extents(extents, src_proj, dest_proj, tol=1e-6):
    x1, y1, x2, y2 = extents
    bx1, by1, bx2, by2 = src_proj.boundary.bounds
    y1, y2 = np.nanmax([y1, by1+tol]), np.nanmin([y2, by2-tol])
    domain_in_src_proj = Polygon([[x1, y1], [x2, y1],
                                  [x2, y2], [x1, y2],
                                  [x1, y1]])
    boundary_poly = Polygon(dest_proj.boundary)
    if src_proj != dest_proj:
        # Erode boundary by threshold to avoid transform issues.
        # This is a workaround for numerical issues at the boundary.
        eroded_boundary = boundary_poly.buffer(-dest_proj.threshold)
        geom_in_src_proj = eroded_boundary.intersection(
            domain_in_src_proj)
        geom_in_crs = dest_proj.project_geometry(geom_in_src_proj, src_proj)
    else:
        geom_in_crs = boundary_poly.intersection(domain_in_src_proj)
    return geom_in_crs.bounds


def path_to_geom(path):
    lines = []
    for path in path.data:
        lines.append(LineString(path))
    return MultiLineString(lines)


def polygon_to_geom(polygon):
    polys = []
    for poly in polygon.data:
        polys.append(Polygon(poly))
    return MultiPolygon(polys)


def geom_to_array(geoms):
    xs, ys = [], []
    for geom in geoms:
        if hasattr(geom, 'exterior'):
            xs.append(np.array(geom.exterior.coords.xy[0]))
            ys.append(np.array(geom.exterior.coords.xy[1]))
        else:
            geom_data = geom.array_interface()
            arr = np.array(geom_data['data']).reshape(geom_data['shape'])
            xs.append(arr[:, 0])
            ys.append(arr[:, 1])
    return xs, ys
