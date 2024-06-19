from holoviews import Store, extension
from holoviews.core.options import Compositor
from holoviews.operation.element import contours

from ..element import Contours, Polygons


def _load_bokeh():
    from geoviews.plotting import bokeh  # noqa: F401

extension.register_backend_callback('bokeh', _load_bokeh)

def _load_mpl():
    from geoviews.plotting import mpl  # noqa: F401
extension.register_backend_callback('matplotlib', _load_mpl)

backends = Store.loaded_backends()
if 'bokeh' in backends:
    _load_bokeh()
if 'matplotlib' in backends:
    _load_mpl()

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
