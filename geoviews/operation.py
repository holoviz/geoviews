import param
import numpy as np
from cartopy import crs as ccrs
from cartopy.img_transform import regrid

from holoviews.operation import ElementOperation

from .element import Image

from .util import project_extents


class ProjectImage(ElementOperation):
    """
    Projects an geoviews Image to the specified projection,
    returning a regular HoloViews Image type. Works by
    regridding the data along projected bounds. Only supports
    rectangular projections.
    """

    projection = param.ClassSelector(default=ccrs.GOOGLE_MERCATOR,
                                     class_=ccrs.Projection, doc="""
        Projection the image type is projected to.""")

    def _process(self, img, key=None):
        proj = self.p.projection
        if proj == img.crs:
            return img
        arr = img.dimension_values(2, flat=False).T
        xs = img.dimension_values(0).T
        ys = img.dimension_values(1).T
        x0, x1 = img.range(0)
        y0, y1 = img.range(1)
        xn, yn = arr.shape
        px0, py0, px1, py1 = project_extents((x0, y0, x1, y1),
                                             img.crs, proj)
        px = np.linspace(px0, px1, xn)
        py = np.linspace(py0, py1, yn)
        pxs, pys = np.meshgrid(px, py)
        pxs = pxs.reshape((yn, xn))
        pys = pys.reshape((yn, xn))
        parray = regrid(arr, xs, ys, img.crs, proj, pxs, pys)
        return Image((py, px, parray.T), kdims=img.kdims,
                     vdims=img.vdims, crs=proj)
