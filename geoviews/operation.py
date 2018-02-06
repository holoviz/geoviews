import param
import numpy as np

from cartopy import crs as ccrs
from cartopy.img_transform import warp_array, _determine_bounds
from holoviews.core import Element
from holoviews.core.util import cartesian_product, get_param_values
from holoviews.operation import Operation
from shapely.geometry import Polygon, LineString

from . import element as gv_element
from .element import (Image, Shape, Polygons, Path, Points, Contours,
                      RGB, _Element)
from .util import project_extents, geom_to_array

geo_ops = []
try:
    from holoviews.operation.datashader import (
        ResamplingOperation, shade, stack, dynspread)
    geo_ops += [ResamplingOperation, shade, stack, dynspread]
except:
    pass

from holoviews.operation.element import contours
from holoviews.operation.stats import bivariate_kde

geo_ops += [contours, bivariate_kde]

def convert_to_geotype(element, crs=None):
    """
    Converts a HoloViews element type to the equivalent GeoViews
    element if given a coordinate reference system.
    """
    geotype = getattr(gv_element, type(element).__name__, None)
    if crs is None or geotype is None or isinstance(element, _Element):
        return element
    return geotype(element, crs=crs)


def find_crs(element):
    """
    Traverses the supplied object looking for coordinate reference
    systems (crs). If multiple clashing reference systems are found
    it will throw an error.
    """
    crss = element.traverse(lambda x: x.crs, [_Element])
    crss = [crs for crs in crss if crs is not None]
    if any(crss[0] != crs for crs in crss[1:] if crs is not None):
        raise ValueError('Cannot datashade Elements in different '
                         'coordinate reference systems.')
    return {'crs': crss[0] if crss else None}


def add_crs(element, **kwargs):
    """
    Converts any elements in the input to their equivalent geotypes
    if given a coordinate reference system.
    """
    return element.map(lambda x: convert_to_geotype(x, kwargs.get('crs')), Element)


for op in geo_ops:
    op._preprocess_hooks = op._preprocess_hooks + [find_crs]
    op._postprocess_hooks = op._postprocess_hooks + [add_crs]


class project_path(Operation):
    """
    Projects Polygons and Path Elements from their source coordinate
    reference system to the supplied projection.
    """

    projection = param.ClassSelector(default=ccrs.GOOGLE_MERCATOR,
                                     class_=ccrs.Projection,
                                     instantiate=False, doc="""
        Projection the shape type is projected to.""")

    supported_types = [Polygons, Path, Contours]

    def _process_element(self, element):
        if not len(element):
            return element.clone(crs=self.p.projection)
        elif element.interface.datatype == 'geodataframe':
            geoms = element.split(datatype='geom')
            projected = [self.p.projection.project_geometry(geom, element.crs)
                         for geom in geoms]
            new_data = element.data.copy()
            new_data['geometry'] = projected
            return element.clone(new_data, crs=self.p.projection)

        geom_type = Polygon if isinstance(element, Polygons) else LineString
        xdim, ydim = element.kdims[:2]
        projected = []
        for geom in element.split(datatype='columns'):
            xs, ys = geom[xdim.name], geom[ydim.name]
            path = geom_type(np.column_stack([xs, ys]))
            proj = self.p.projection.project_geometry(path, element.crs)
            proj_arr = geom_to_array(proj)
            geom[xdim.name] = proj_arr[:, 0]
            geom[ydim.name] = proj_arr[:, 1]
            projected.append(geom)
        return element.clone(projected, crs=self.p.projection)

    def _process(self, element, key=None):
        return element.map(self._process_element, self.supported_types)


class project_shape(Operation):
    """
    Projects Shape Element from the source coordinate reference system
    to the supplied projection.
    """

    projection = param.ClassSelector(default=ccrs.GOOGLE_MERCATOR,
                                     class_=ccrs.Projection,
                                     instantiate=False, doc="""
        Projection the shape type is projected to.""")

    supported_types = [Shape]

    def _process_element(self, element):
        if not len(element):
            return element.clone(crs=self.p.projection)
        geom = self.p.projection.project_geometry(element.geom(), element.crs)
        return element.clone(geom, crs=self.p.projection)

    def _process(self, element, key=None):
        return element.map(self._process_element, self.supported_types)


class project_points(Operation):

    projection = param.ClassSelector(default=ccrs.GOOGLE_MERCATOR,
                                     class_=ccrs.Projection,
                                     instantiate=False, doc="""
        Projection the shape type is projected to.""")

    supported_types = [Points]

    def _process_element(self, element):
        if not len(element):
            return element.clone(crs=self.p.projection)
        xdim, ydim = element.dimensions()[:2]
        xs, ys = (element.dimension_values(i) for i in range(2))
        coordinates = self.p.projection.transform_points(element.crs, xs, ys)
        new_data = element.columns()
        new_data[xdim.name] = coordinates[:, 0]
        new_data[ydim.name] = coordinates[:, 1]
        datatype = [element.interface.datatype]+element.datatype
        return element.clone(new_data, crs=self.p.projection,
                             datatype=datatype)

    def _process(self, element, key=None):
        return element.map(self._process_element, self.supported_types)


class project_image(Operation):
    """
    Projects an geoviews Image to the specified projection,
    returning a regular HoloViews Image type. Works by
    regridding the data along projected bounds. Only supports
    rectangular projections.
    """

    projection = param.ClassSelector(default=ccrs.GOOGLE_MERCATOR,
                                     class_=ccrs.Projection,
                                     instantiate=False, doc="""
        Projection the image type is projected to.""")

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
                         vdims=img.vdims, crs=proj)


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

    def _process(self, element, key=None):
        element = element.map(project_path, project_path.supported_types)
        element = element.map(project_image, project_image.supported_types)
        element = element.map(project_shape, project_shape.supported_types)
        return element.map(project_points, project_points.supported_types)
