from holoviews.testing._testing import _ElementComparison as _EC

from ..element.geo import (
    FilledContours,
    Image,
    ImageStack,
    LineContours,
    Points,
    WindBarbs,
)

# TODO: Think more about this
_EC.register()
_EC.equality_funcs[Image] = _EC.compare_dataset
_EC.equality_funcs[ImageStack] = _EC.compare_dataset
_EC.equality_funcs[Points] = _EC.compare_dataset
_EC.equality_funcs[LineContours] = _EC.compare_dataset
_EC.equality_funcs[FilledContours] = _EC.compare_dataset
_EC.equality_funcs[WindBarbs] = _EC.compare_dataset
