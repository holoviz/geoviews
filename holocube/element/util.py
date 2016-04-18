from iris.util import guess_coord_axis
from holoviews.core.dimension import Dimension
from holoviews.core.util import * # noqa (API import)

import datetime

def get_date_format(coord):
    def date_formatter(val, pos=None):
        date = coord.units.num2date(val)
        date_format = Dimension.type_formatters.get(datetime.datetime, None)
        if date_format:
            return date.strftime(date_format)
        else:
            return date

    return date_formatter

def coord_to_dimension(coord):
    """
    Converts an iris coordinate to a HoloViews dimension.
    """
    kwargs = {}
    if coord.units.is_time_reference():
        kwargs['value_format'] = get_date_format(coord)
    else:
        kwargs['unit'] = str(coord.units)
    return Dimension(coord.name(), **kwargs)

def sort_coords(coord):
    """
    Sorts a list of DimCoords trying to ensure that
    dates and pressure levels appear first and the
    longitude and latitude appear last in the correct
    order.
    """
    order = {'T': -2, 'Z': -1, 'X': 1, 'Y': 2}
    axis = guess_coord_axis(coord)
    return (order.get(axis, 0), coord and coord.name())