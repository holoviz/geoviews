from holoviews.core import Element
from holoviews.operation.element import contours
from holoviews.operation.stats import bivariate_kde

from .. import element as gv_element
from ..element import _Element
from .projection import (
    project_image, project_path, project_shape, project_points,
    project_graph, project_quadmesh, project
)

geo_ops = [contours, bivariate_kde]
try:
    from holoviews.operation.datashader import (
        ResamplingOperation, shade, stack, dynspread)
    geo_ops += [ResamplingOperation, shade, stack, dynspread]
except:
    pass

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
