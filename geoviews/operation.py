import param
import numpy as np
from cartopy import crs as ccrs
from cartopy.img_transform import warp_array

from holoviews.operation import ElementOperation

from .element import Image, Shape, Polygons, Path, Points
from .util import project_extents

class project_shape(ElementOperation):
    """
    Projects Shape, Polygons and Path Elements from their source
    coordinate reference system to the supplied projection.
    """

    projection = param.ClassSelector(default=ccrs.GOOGLE_MERCATOR,
                                     class_=ccrs.Projection,
                                     instantiate=False, doc="""
        Projection the shape type is projected to.""")

    supported_types = [Shape, Polygons, Path]

    def _process_element(self, element):
        geom = self.p.projection.project_geometry(element.geom(),
                                                  element.crs)
        return element.clone(geom, crs=self.p.projection)

    def _process(self, element, key=None):
        return element.map(self._process_element, self.supported_types)


class project_points(ElementOperation):

    projection = param.ClassSelector(default=ccrs.GOOGLE_MERCATOR,
                                     class_=ccrs.Projection,
                                     instantiate=False, doc="""
        Projection the shape type is projected to.""")

    supported_types = [Points]

    def _process_element(self, element):
        xdim, ydim = element.dimensions()[:2]
        xs, ys = (element.dimension_values(i) for i in range(2))
        coordinates = self.p.projection.transform_points(element.crs, xs, ys)
        new_data = element.columns()
        new_data[xdim.name] = coordinates[:, 0]
        new_data[ydim.name] = coordinates[:, 1]
        return element.clone(new_data, crs=self.p.projection)

    def _process(self, element, key=None):
        return element.map(self._process_element, self.supported_types)


class project_image(ElementOperation):
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

    supported_types = [Image]

    def _process(self, img, key=None):
        proj = self.p.projection
        if proj == img.crs:
            return img
        arr = img.dimension_values(2, flat=False)
        x0, x1 = img.range(0)
        y0, y1 = img.range(1)
        xn, yn = arr.shape
        px0, py0, px1, py1 = project_extents((x0, y0, x1, y1),
                                             img.crs, proj)
        src_ext, trgt_ext = (x0, x1, y0, y1), (px0, px1, py0, py1)
        projected, extents = warp_array(arr, proj, img.crs, (xn, yn),
                                        src_ext, trgt_ext)
        bounds = (extents[0], extents[2], extents[1], extents[3])
        data = np.flipud(projected)
        return Image(data, bounds=bounds, kdims=img.kdims,
                     vdims=img.vdims, crs=proj)


class project(ElementOperation):
    """
    Projects GeoViews Element types to the specified projection.
    """

    projection = param.ClassSelector(default=ccrs.GOOGLE_MERCATOR,
                                     class_=ccrs.Projection,
                                     instantiate=False, doc="""
        Projection the image type is projected to.""")

    def _process(self, element, key=None):
        element = element.map(project_image, project_image.supported_types)
        element = element.map(project_shape, project_shape.supported_types)
        return element.map(project_points, project_points.supported_types)
