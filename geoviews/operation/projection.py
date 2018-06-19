import param
import numpy as np

from cartopy import crs as ccrs
from cartopy.img_transform import warp_array, _determine_bounds
from holoviews.core.util import cartesian_product, get_param_values
from holoviews.operation import Operation
from shapely.geometry import Polygon, LineString, MultiPolygon, MultiLineString

from ..element import (Image, Shape, Polygons, Path, Points, Contours,
                       RGB, Graph, Nodes, EdgePaths, QuadMesh, VectorField,
                       HexTiles, Labels)
from ..util import (
    project_extents, geom_to_array, wrap_path_data, is_multi_geometry,
    polygon_to_geom, path_to_geom
)


class _project_operation(Operation):
    """
    Baseclass for projection operations, projecting elements from their
    source coordinate reference system to the supplied projection.
    """

    projection = param.ClassSelector(default=ccrs.GOOGLE_MERCATOR,
                                     class_=ccrs.Projection,
                                     instantiate=False, doc="""
        Projection the shape type is projected to.""")

    # Defines the types of elements supported by the operation
    supported_types = []

    def _process(self, element, key=None):
        return element.map(self._process_element, self.supported_types)


class project_path(_project_operation):
    """
    Projects Polygons and Path Elements from their source coordinate
    reference system to the supplied projection.
    """

    supported_types = [Polygons, Path, Contours, EdgePaths]

    def _project_path(self, element, path, data, boundary, geom_type, multi_type):
        """
        Handle case of continuously varying path
        """
        xdim, ydim = path.kdims[:2]
        xs, ys = (path.dimension_values(i) for i in range(2))
        if not len(xs):
            return []

        proj_arr = self.p.projection.quick_vertices_transform(
            np.column_stack([xs, ys]), element.crs)

        if proj_arr is None:
            vertices = np.column_stack([xs, ys])
            if hasattr(element.crs, '_bbox_and_offset'):
                vertices = wrap_path_data(vertices, element.crs, element.crs)
            path = geom_type(vertices)
            if boundary:
                path = path.intersection(boundary)
            if not path:
                return []
            proj = self.p.projection.project_geometry(path, element.crs)
            proj_arr = geom_to_array(proj)
        data[xdim.name] = proj_arr[:, 0]
        data[ydim.name] = proj_arr[:, 1]
        return [data]

    def _project_contour(self, element, contour, data, boundary, geom_type, multi_type):
        """
        Handle case of iso-contour
        """
        xdim, ydim = contour.kdims[:2]
        data = {k: vals[0] for k, vals in data.items()}

        # Wrap longitudes
        vertices = contour.array([0, 1])
        if hasattr(element.crs, '_bbox_and_offset'):
            vertices = wrap_path_data(vertices, element.crs, element.crs)
        element = type(element)([vertices])
        to_geom = polygon_to_geom if isinstance(element, Polygon) else path_to_geom

        # Clip path to projection boundaries
        geoms = []
        for g in to_geom(element, multi=False, skip_invalid=False):
            if np.isinf(np.array(g.array_interface_base['data'])).sum():
                # Skip if infinity in path
                continue
            try:
                # Compute boundary intersections
                if boundary:
                    g = g.intersection(boundary)
            except:
                continue
            if is_multi_geometry(g):
                for p in g:
                    try:
                        geoms.append(geom_type(p))
                    except:
                        continue
            else:
                geoms.append(g)

        # Project geometry
        projected = []
        for g in geoms:
            proj = self.p.projection.project_geometry(g, contour.crs)
            proj = proj if is_multi_geometry(proj) else [proj]
            for geom in proj:
                vertices = np.array(geom.array_interface_base['data']).reshape(-1, 2)
                xs, ys = vertices.T
                if len(xs):
                    projected.append(dict(data, **{xdim.name: xs, ydim.name: ys}))
        return projected

    def _project_geodataframe(self, element):
        geoms = element.split(datatype='geom')
        projected = [self.p.projection.project_geometry(geom, element.crs)
                     for geom in geoms]
        new_data = element.data.copy()
        new_data['geometry'] = projected
        return element.clone(new_data, crs=self.p.projection)

    def _process_element(self, element):
        if not len(element):
            return element.clone(crs=self.p.projection)
        elif element.interface.datatype == 'geodataframe':
            return self._project_geodataframe(element)

        boundary = element.crs.project_geometry(Polygon(self.p.projection.boundary),
                                                self.p.projection)


        if isinstance(element, Polygons):
            multi_type, geom_type = MultiPolygon, Polygon
        else:
            multi_type, geom_type = MultiLineString, LineString

        projected = []
        paths = element.split()
        for path in paths:
            data = {vd.name: path.dimension_values(vd, expanded=False) for vd in path.vdims}
            if any(len(vals) > 1 for vals in data.values()):
                projected += self._project_path(element, path, data, boundary, geom_type, multi_type)
            else:
                projected += self._project_contour(element, path, data, boundary, geom_type, multi_type)

        if len(paths) and len(projected) == 0:
            self.warning('While projecting a %s element from a %s coordinate '
                         'reference system (crs) to a %s projection none of '
                         'the projected paths were contained within the bounds '
                         'specified by the projection. Ensure you have specified '
                         'the correct coordinate system for your data.' %
                         (type(element).__name__, type(element.crs).__name__,
                          type(self.p.projection).__name__))

        return element.clone(projected, crs=self.p.projection)


class project_shape(_project_operation):
    """
    Projects Shape Element from the source coordinate reference system
    to the supplied projection.
    """

    supported_types = [Shape]

    def _process_element(self, element):
        if not len(element):
            return element.clone(crs=self.p.projection)
        geom = element.geom()
        vertices = geom_to_array(geom)
        if isinstance(geom, (MultiPolygon, Polygon)):
            obj = Polygons([vertices])
        else:
            obj = Path([vertices])
        geom = project_path(obj, projection=self.p.projection).geom()
        return element.clone(geom, crs=self.p.projection)


class project_points(_project_operation):

    supported_types = [Points, Nodes, VectorField, HexTiles, Labels]

    def _process_element(self, element):
        if not len(element):
            return element.clone(crs=self.p.projection)
        xdim, ydim = element.dimensions()[:2]
        xs, ys = (element.dimension_values(i) for i in range(2))
        coordinates = self.p.projection.transform_points(element.crs, xs, ys)
        mask = np.isfinite(coordinates[:, 0])
        new_data = {k: v[mask] for k, v in element.columns().items()}
        new_data[xdim.name] = coordinates[mask, 0]
        new_data[ydim.name] = coordinates[mask, 1]
        datatype = [element.interface.datatype]+element.datatype

        if len(new_data[xdim.name]) == 0:
            self.warning('While projecting a %s element from a %s coordinate '
                         'reference system (crs) to a %s projection none of '
                         'the projected paths were contained within the bounds '
                         'specified by the projection. Ensure you have specified '
                         'the correct coordinate system for your data.' %
                         (type(element).__name__, type(element.crs).__name__,
                          type(self.p.projection).__name__))

        return element.clone(new_data, crs=self.p.projection,
                             datatype=datatype)


class project_graph(_project_operation):

    supported_types = [Graph]

    def _process_element(self, element):
        nodes = project_points(element.nodes, projection=self.projection)
        data = (element.data, nodes)
        if element._edgepaths:
            data = data + (project_path(element.edgepaths, projection=self.projection),)
        return element.clone(data, crs=self.projection)


class project_quadmesh(_project_operation):

    supported_types = [QuadMesh]

    def _process_element(self, element):
        proj = self.p.projection
        irregular = any(element.interface.irregular(element, kd)
                        for kd in element.kdims)
        zs = element.dimension_values(2, flat=False)
        if irregular:
            X, Y = [np.asarray(element.interface.coords(element, kd, expanded=True))
                    for kd in element.kdims]
        else:
            X = element.dimension_values(0, expanded=True)
            Y = element.dimension_values(1, expanded=True)
            zs = zs.T

        coords = proj.transform_points(element.crs, X, Y)
        PX, PY = coords[..., 0], coords[..., 1]

        # Mask quads which are wrapping around the x-axis
        wrap_proj_types = (ccrs._RectangularProjection,
                           ccrs._WarpedRectangularProjection,
                           ccrs.InterruptedGoodeHomolosine,
                           ccrs.Mercator)
        if isinstance(proj, wrap_proj_types):
            with np.errstate(invalid='ignore'):
                edge_lengths = np.hypot(
                    np.diff(PX , axis=1),
                    np.diff(PY, axis=1)
                )
                to_mask = (
                    (edge_lengths >= abs(proj.x_limits[1] -
                                         proj.x_limits[0]) / 2) |
                    np.isnan(edge_lengths)
                )
            if np.any(to_mask):
                mask = np.zeros(zs.shape, dtype=np.bool)
                mask[:, 1:][to_mask] = True
                mask[:, 2:][to_mask[:, :-1]] = True
                mask[:, :-1][to_mask] = True
                mask[:, :-2][to_mask[:, 1:]] = True
                mask[1:, 1:][to_mask[:-1]] = True
                mask[1:, :-1][to_mask[:-1]] = True
                mask[:-1, 1:][to_mask[1:]] = True
                mask[:-1, :-1][to_mask[1:]] = True
                zs[mask] = np.NaN

        params = get_param_values(element)
        if PX.ndim < 2:
            PX = PX.reshape(zs.shape)
        if PY.ndim < 2:
            PY = PY.reshape(zs.shape)
        return QuadMesh((PX, PY, zs), crs=self.projection, **params)


class project_image(_project_operation):
    """
    Projects an geoviews Image to the specified projection,
    returning a regular HoloViews Image type. Works by
    regridding the data along projected bounds. Only supports
    rectangular projections.
    """

    fast = param.Boolean(default=False, doc="""
        Whether to enable fast reprojection with (much) better
        performance but poorer handling in polar regions.""")

    width = param.Integer(default=None, doc="""
        Width of the reprojectd Image""")

    height = param.Integer(default=None, doc="""
        Height of the reprojected Image""")

    link_inputs = param.Boolean(default=True, doc="""
        By default, the link_inputs parameter is set to True so that
        when applying project_image, backends that support linked streams
        update RangeXY streams on the inputs of the operation.""")

    supported_types = [Image]

    def _process(self, img, key=None):
        if self.p.fast:
            return self._fast_process(img, key)
        proj = self.p.projection
        if proj == img.crs:
            return img
        x0, x1 = img.range(0)
        y0, y1 = img.range(1)
        xn, yn = img.interface.shape(img, gridded=True)[:2]
        px0, py0, px1, py1 = project_extents((x0, y0, x1, y1),
                                             img.crs, proj)
        src_ext, trgt_ext = (x0, x1, y0, y1), (px0, px1, py0, py1)
        arrays = []
        for vd in img.vdims:
            arr = img.dimension_values(vd, flat=False)
            projected, extents = warp_array(arr, proj, img.crs, (xn, yn),
                                            src_ext, trgt_ext)
            arrays.append(projected)
        projected = np.dstack(arrays) if len(arrays) > 1 else arrays[0]
        data = np.flipud(projected)
        bounds = (extents[0], extents[2], extents[1], extents[3])
        return img.clone(data, bounds=bounds, kdims=img.kdims,
                         vdims=img.vdims, crs=proj, xdensity=None,
                         ydensity=None)

    def _fast_process(self, element, key=None):
        # Project coordinates
        proj = self.p.projection
        if proj == element.crs:
            return element

        h, w = element.interface.shape(element, gridded=True)[:2]
        xs = element.dimension_values(0)
        ys = element.dimension_values(1)
        if isinstance(element, RGB):
            rgb = element.rgb
            array = np.dstack([np.flipud(rgb.dimension_values(d, flat=False))
                               for d in rgb.vdims])
        else:
            array = element.dimension_values(2, flat=False)

        (x0, y0, x1, y1) = element.bounds.lbrt()
        width = int(w) if self.p.width is None else self.p.width
        height = int(h) if self.p.height is None else self.p.height

        bounds = _determine_bounds(xs, ys, element.crs)
        yb = bounds['y']
        resampled = []
        xvalues = []
        for xb in bounds['x']:
            px0, py0, px1, py1 = project_extents((xb[0], yb[0], xb[1], yb[1]), element.crs, proj)
            if len(bounds['x']) > 1:
                xfraction = (xb[1]-xb[0])/(x1-x0)
                fraction_width = int(width*xfraction)
            else:
                fraction_width = width
            xs = np.linspace(px0, px1, fraction_width)
            ys = np.linspace(py0, py1, height)
            cxs, cys = cartesian_product([xs, ys])

            pxs, pys, _ = element.crs.transform_points(proj, np.asarray(cxs), np.asarray(cys)).T
            icxs = (((pxs-x0) / (x1-x0)) * w).astype(int)
            icys = (((pys-y0) / (y1-y0)) * h).astype(int)
            xvalues.append(xs)

            icxs[icxs<0] = 0
            icys[icys<0] = 0
            icxs[icxs>=w] = w-1
            icys[icys>=h] = h-1
            resampled_arr = array[icys, icxs]
            if isinstance(element, RGB):
                nvdims = len(element.vdims)
                resampled_arr = resampled_arr.reshape((fraction_width, height, nvdims)).transpose([1, 0, 2])
            else:
                resampled_arr = resampled_arr.reshape((fraction_width, height)).T
            resampled.append(resampled_arr)
        xs = np.concatenate(xvalues[::-1])
        resampled = np.hstack(resampled[::-1])
        datatypes = [element.interface.datatype, 'xarray', 'grid']
        data = (xs, ys)
        for i in range(len(element.vdims)):
            if resampled.ndim > 2:
                data = data + (resampled[::-1, :, i],)
            else:
                data = data + (resampled,)
        return element.clone(data, crs=proj, bounds=None, datatype=datatypes)


class project(Operation):
    """
    Projects GeoViews Element types to the specified projection.
    """

    projection = param.ClassSelector(default=ccrs.GOOGLE_MERCATOR,
                                     class_=ccrs.Projection,
                                     instantiate=False, doc="""
        Projection the image type is projected to.""")

    _operations = [project_path, project_image, project_shape,
                   project_graph, project_quadmesh, project_points]

    def _process(self, element, key=None):
        for op in self._operations:
            element = element.map(op.instance(projection=self.p.projection),
                                  op.supported_types)
        return element
