import param
import numpy as np

from holoviews.core import CompositeOverlay, Element

from ..util import project_extents


def _get_projection(el):
    """
    Get coordinate reference system from non-auxiliary elements.
    Return value is a tuple of a precedence integer and the projection,
    to allow non-auxiliary components to take precedence.
    """
    result = None
    if hasattr(el, 'crs'):
        result = (int(el._auxiliary_component), el.crs)
    return result


class ProjectionPlot(param.Parameterized):
    """
    Implements custom _get_projection method to make the coordinate
    reference system available to HoloViews plots as a projection.
    """

    infer_projection = param.Boolean(default=True, doc="""
        Whether the projection should be inferred from the element crs.""")

    padding = param.ClassSelector(default=0.1, class_=(int, float, tuple), doc="""
        Fraction by which to increase auto-ranged extents to make
        datapoints more visible around borders.

        To compute padding, the axis whose screen size is largest is
        chosen, and the range of that axis is increased by the
        specified fraction along each axis.  Other axes are then
        padded ensuring that the amount of screen space devoted to
        padding is equal for all axes. If specified as a tuple, the
        int or float values in the tuple will be used for padding in
        each axis, in order (x,y or x,y,z).

        For example, for padding=0.2 on a 800x800-pixel plot, an x-axis
        with the range [0,10] will be padded by 20% to be [-1,11], while
        a y-axis with a range [0,1000] will be padded to be [-100,1100],
        which should make the padding be approximately the same number of
        pixels. But if the same plot is changed to have a height of only
        200, the y-range will then be [-400,1400] so that the y-axis
        padding will still match that of the x-axis.

        It is also possible to declare non-equal padding value for the
        lower and upper bound of an axis by supplying nested tuples,
        e.g. padding=(0.1, (0, 0.1)) will pad the x-axis lower and
        upper bound as well as the y-axis upper bound by a fraction of
        0.1 while the y-axis lower bound is not padded at all.""")

    def _get_projection(self, obj):
        # Look up custom projection in options
        isoverlay = lambda x: isinstance(x, CompositeOverlay)
        opts = self._traverse_options(obj, 'plot', ['projection', 'infer_projection'],
                                      [CompositeOverlay, Element],
                                      keyfn=isoverlay, defaults=False)
        from_overlay = not all(p is None for p in opts[True]['projection'])
        projections = opts[from_overlay]['projection']
        infer = any(opts[from_overlay]['infer_projection']) or self.infer_projection
        custom_projs = [p for p in projections if p is not None]

        if len(set([type(p) for p in custom_projs])) > 1:
            raise Exception("An axis may only be assigned one projection type")
        elif custom_projs:
            return custom_projs[0]
        if not infer:
            return self.projection

        # If no custom projection is supplied traverse object to get
        # the custom projections and sort by precedence
        projections = sorted([p for p in obj.traverse(_get_projection, [Element])
                              if p is not None and p[1] is not None])
        if projections:
            return projections[0][1]
        else:
            return None

    def get_extents(self, element, ranges, range_type='combined'):
        """
        Subclasses the get_extents method using the GeoAxes
        set_extent method to project the extents to the
        Elements coordinate reference system.
        """
        proj = self.projection
        if self.global_extent and range_type in ('combined', 'data'):
            (x0, x1), (y0, y1) = proj.x_limits, proj.y_limits
            return (x0, y0, x1, y1)
        extents = super(ProjectionPlot, self).get_extents(element, ranges, range_type)
        if not getattr(element, 'crs', None) or not self.geographic:
            return extents
        elif any(e is None or not np.isfinite(e) for e in extents):
            extents = None
        else:
            extents = project_extents(extents, element.crs, proj)
        return (np.NaN,)*4 if not extents else extents
