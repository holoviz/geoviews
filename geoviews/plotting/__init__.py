from holoviews.core.options import Compositor
from holoviews.operation.element import contours

from ..element import Contours, Polygons
from . import mpl # noqa

try:
    from . import bokeh # noqa
except ImportError:
    pass

Compositor.register(Compositor("LineContours", contours, None,
                               'data', transfer_options=True,
                               transfer_parameters=True,
                               output_type=Contours,
                               backends=['bokeh', 'matplotlib']))
Compositor.register(Compositor("FilledContours", contours.instance(filled=True),
                               None, 'data', transfer_options=True,
                               transfer_parameters=True,
                               output_type=Polygons,
                               backends=['bokeh', 'matplotlib']))
