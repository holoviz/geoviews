import os

import param
import numpy as np
import xarray as xr

from holoviews.core.util import get_param_values
from holoviews.core.data import XArrayInterface
from holoviews.element import Image as HvImage, QuadMesh as HvQuadMesh
from holoviews.operation.datashader import regrid

from ..element import Image, QuadMesh, is_geographic


class weighted_regrid(regrid):
    """
    Implements weighted regridding of rectilinear and curvilinear
    grids using the xESMF library, supporting all the ESMF regridding
    algorithms including bilinear, conservative and nearest neighbour
    regridding. The operation will always store the sparse weight
    matrix to disk and reuse the weights for later aggregations. To
    delete the weight files call the clean_weight_files method on the
    operation.
    """

    interpolation = param.ObjectSelector(default='bilinear',
        objects=['bilinear', 'conservative', 'nearest_s2d', 'nearest_d2s'], doc="""
        Interpolation method""")

    reuse_weights = param.Boolean(default=True, doc="""
        Whether to cache the sparse regridding weights in memory.
        Can provide considerable speedups when exploring a larger
        dataset.""")

    save_weights = param.Boolean(default=False, doc="""
        Whether to save weight file to speed up future regridding
        operations.""")

    file_pattern = param.String(default='{method}_{x_range}_{y_range}_{width}x{height}.nc',
                                doc="""
        The file pattern used to store the regridding weights when the
        reuse_weights parameter is disabled. Note the files are not
        cleared automatically so make sure you clean up the cached
        files when you are done.""")

    _files = []

    _weights = {}

    _per_element = True

    def _get_regridder(self, element):
        try:
            import xesmf as xe
        except ImportError:
            raise ImportError("xESMF library required for weighted regridding.")
        x, y = element.kdims
        if self.p.target:
            tx, ty = self.p.target.kdims[:2]
            if issubclass(self.p.target.interface, XArrayInterface):
                ds_out = self.p.target.data
                ds_out = ds_out.rename({tx.name: 'lon', ty.name: 'lat'})
                height, width = ds_out[tx.name].shape
            else:
                xs = self.p.target.dimension_values(0, expanded=False)
                ys = self.p.target.dimension_values(1, expanded=False)
                ds_out = xr.Dataset({'lat': ys, 'lon': xs})
                height, width = len(ys), len(xs)
            x_range = ds_out[tx.name].min(), ds_out[tx.name].max()
            y_range = ds_out[ty.name].min(), ds_out[ty.name].max()
            xtype, ytype = 'numeric', 'numeric'
        else:
            info = self._get_sampling(element, x, y)
            (x_range, y_range), _, (width, height), (xtype, ytype) = info
            if x_range[0] > x_range[1]:
                x_range = x_range[::-1]
            element = element.select(**{x.name: x_range, y.name: y_range})
            ys = np.linspace(y_range[0], y_range[1], height)
            xs = np.linspace(x_range[0], x_range[1], width)
            ds_out = xr.Dataset({'lat': ys, 'lon': xs})

        irregular = any(element.interface.irregular(element, d)
                        for d in [x, y])
        coord_opts = {'flat': False} if irregular else {'expanded': False}
        coords = tuple(element.dimension_values(d, **coord_opts)
                       for d in [x, y])
        arrays = self._get_xarrays(element, coords, xtype, ytype)
        ds = xr.Dataset(arrays)
        ds = ds.rename({x.name: 'lon', y.name: 'lat'})

        x_range = str(tuple('%.3f' % r for r in x_range)).replace("'", '')
        y_range = str(tuple('%.3f' % r for r in y_range)).replace("'", '')
        filename = self.p.file_pattern.format(
            method=self.p.interpolation, width=width, height=height,
            x_range=x_range, y_range=y_range
        )
        reuse_weights = os.path.isfile(os.path.abspath(filename))
        save_filename = filename if self.p.save_weights or reuse_weights else None
        regridder = xe.Regridder(ds, ds_out, self.p.interpolation,
                                 reuse_weights=reuse_weights,
                                 weights=self._weights.get(filename),
                                 filename=save_filename)
        if save_filename:
            self._files.append(os.path.abspath(filename))
        if self.p.reuse_weights:
            self._weights[filename] = regridder.weights
        return regridder, arrays


    def _process(self, element, key=None):
        regridder, arrays = self._get_regridder(element)
        x, y = element.kdims
        ds = xr.Dataset({vd: regridder(arr) for vd, arr in arrays.items()})
        ds = ds.rename({'lon': x.name, 'lat': y.name})
        params = get_param_values(element)
        if is_geographic(element):
            try:
                return Image(ds, crs=element.crs, **params)
            except Exception:
                return QuadMesh(ds, crs=element.crs, **params)
        try:
            return HvImage(ds, **params)
        except Exception:
            return HvQuadMesh(ds, **params)


    @classmethod
    def clean_weight_files(cls):
        """
        Cleans existing weight files.
        """
        deleted = []
        for f in cls._files:
            try:
                os.remove(f)
                deleted.append(f)
            except FileNotFoundError:
                pass
        print('Deleted %d weight files' % len(deleted))
        cls._files = []
