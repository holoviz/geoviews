import numpy as np
from shapely.geometry import (MultiLineString, LineString,
                              MultiPolygon, Polygon)

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


def project_extents(extents, src_proj, dest_proj):
    x0, y0, x1, y1 = extents
    domain_in_crs = LineString([[x0, y0], [x1, y0], [x1, y1],
                                [x0, y1], [x0, y0]])
    projected = dest_proj.project_geometry(domain_in_crs, src_proj)
    if projected.bounds:
        return projected.bounds
    else:
        return (np.NaN,)*4


def geom_to_array(geoms):
    xs, ys = [], []
    for geom in geoms:
        if hasattr(geom, 'exterior'):
            xs.append(np.array(geom.exterior.coords.xy[0]))
            ys.append(np.array(geom.exterior.coords.xy[1]))
        else:
            geom_data = geom.array_interface()
            arr = np.array(geom_data['data']).reshape(geom_data['shape'])
            xs.append(arr[0, :])
            ys.append(arr[1, :])
    return xs, ys
