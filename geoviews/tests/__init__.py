from holoviews.testing import add_comparison

from ..element.geo import (
    FilledContours,
    Image,
    ImageStack,
    LineContours,
    Points,
    WindBarbs,
)

add_comparison(FilledContours, Image, ImageStack, LineContours, Points, WindBarbs)
