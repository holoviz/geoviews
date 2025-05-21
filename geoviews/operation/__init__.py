from holoviews.core import Element
from holoviews.operation.element import contours
from holoviews.operation.stats import bivariate_kde

from .. import element as gv_element
from ..element import _Element
from .projection import (  # noqa: F401
    project,
    project_geom,
    project_graph,
    project_image,
    project_path,
    project_points,
    project_quadmesh,
    project_shape,
    project_vectorfield,
    project_windbarbs,
)
from .resample import resample_geometry  # noqa: F401

geo_ops = [contours, bivariate_kde]
try:
    from holoviews.operation.datashader import dynspread, shade, stack
    from holoviews.operation.resample import ResampleOperation2D
    geo_ops += [ResampleOperation2D, shade, stack, dynspread]
except ImportError:
    pass

def convert_to_geotype(element, crs=None):
    """Converts a HoloViews element type to the equivalent GeoViews
    element if given a coordinate reference system.
    """
    geotype = getattr(gv_element, type(element).__name__, None)
    if crs is None or geotype is None or isinstance(element, _Element):
        return element
    return element.clone(new_type=geotype, crs=crs)


def find_crs(op, element):
    """Traverses the supplied object looking for coordinate reference
    systems (crs). If multiple clashing reference systems are found
    it will throw an error.
    """
    crss = [crs for crs in element.traverse(lambda x: x.crs, [_Element])
            if crs is not None]
    if not crss:
        return {}
    crs = crss[0]
    if any(crs != ocrs for ocrs in crss[1:]):
        raise ValueError(f'Cannot {type(op).__name__} Elements in different '
                         'coordinate reference systems.')
    return {'crs': crs}


def add_crs(op, element, **kwargs):
    """Converts any elements in the input to their equivalent geotypes
    if given a coordinate reference system.
    """
    return element.map(lambda x: convert_to_geotype(x, kwargs.get('crs')), Element)


for op in geo_ops:
    op._preprocess_hooks = op._preprocess_hooks + [find_crs]
    op._postprocess_hooks = op._postprocess_hooks + [add_crs]
