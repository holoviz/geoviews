from unittest import TestCase

from holoviews.element.comparison import Comparison as HvComparison

from .geo import Image, Points, LineContours, FilledContours

class Comparison(HvComparison):

    @classmethod
    def register(cls):
        super().register()
        cls.equality_type_funcs[Image] = cls.compare_dataset
        cls.equality_type_funcs[Points] = cls.compare_dataset
        cls.equality_type_funcs[LineContours] = cls.compare_dataset
        cls.equality_type_funcs[FilledContours] = cls.compare_dataset
        return cls.equality_type_funcs


class ComparisonTestCase(Comparison, TestCase):
    """
    Class to integrate the Comparison class with unittest.TestCase.
    """

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        registry = Comparison.register()
        for k, v in registry.items():
            self.addTypeEqualityFunc(k, v)
