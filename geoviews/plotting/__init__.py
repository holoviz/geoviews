from holoviews import Store, extension
from holoviews.core.options import Compositor
from holoviews.operation.element import contours

from ..element import Contours, Polygons


if hasattr(extension, 'register_backend_callback'):
    def _load_bokeh():
        from . import bokeh # noqa
    extension.register_backend_callback('bokeh', _load_bokeh)

    def _load_mpl():
        from . import mpl # noqa
    extension.register_backend_callback('matplotlib', _load_mpl)

    backends = Store.loaded_backends()
    if 'bokeh' in backends:
        _load_bokeh()
    if 'matplotlib' in backends:
        _load_mpl()
else:
    try:
        from . import mpl # noqa
    except ImportError:
        pass

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
