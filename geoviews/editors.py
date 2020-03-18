import param
import panel as pn
import numpy as np

from holoviews.core import DynamicMap
from holoviews.streams import BoundsXY

from  .element import TriMesh
from .streams import TriMeshEdit


class TriMeshEditor(param.Parameterized):

    apply_edits = param.Action(default=lambda self: self.param.trigger('apply_edits'))

    object = param.ClassSelector(class_=TriMesh, doc="""
        The Element to edit and annotate.""")

    def __init__(self, trimesh, **params):
        from holoviews.operation.datashader import datashade
        super(TriMeshEditor, self).__init__(object=trimesh, **params)
        self._object = DynamicMap(self._get_object)
        self._bounds = BoundsXY(source=self._object)
        self.selected = self._object.apply(self.subselect, bounds=self._bounds.param.bounds)
        self._stream = TriMeshEdit(source=self.selected)
        self._nodes = None
        self.shaded = datashade(self._object, aggregator='any', interpolation=None, link_inputs=False)

    @param.depends('object')
    def _get_object(self):
        return self.object

    @param.depends('apply_edits', watch=True)
    def _edit(self):
        nodes = self.object.nodes
        index = nodes.kdims[2].name
        simplices = self.object.data
        edited = self._stream.element.dframe().set_index(index)
        original = nodes.dframe().set_index(index)
        original.update(edited)
        if len(edited) != len(self._current):
            deleted = set(self._current['index'].values) - set(edited.index.values)
            deleted = list(deleted)
            original.drop(index=deleted, inplace=True)
            d1, d2, d3 = self.object.kdims
            indexes = original.index.values
            new_index = np.arange(len(indexes))
            mapping = dict(zip(indexes, new_index))
            simplices = simplices[
                ~simplices[d1.name].isin(deleted) &
                ~simplices[d2.name].isin(deleted) &
                ~simplices[d3.name].isin(deleted)
            ]
        nodes = nodes.clone(original)
        self.object = self.object.clone((simplices, nodes))

    @classmethod
    def spatial_select(cls, tri, x_range, y_range):
        d1, d2, d3 = tri.kdims
        index_col = tri.nodes.kdims[2].name
        nodes = tri.nodes[slice(*x_range), slice(*y_range)].data.copy()
        indexes = nodes[index_col].values
        old_indexes = np.array(indexes)
        simplices = tri.data[
            tri.data[d1.name].isin(indexes) &
            tri.data[d2.name].isin(indexes) &
            tri.data[d3.name].isin(indexes)
        ]
        return simplices, nodes

    def subselect(self, tri, bounds):
        opts = dict(node_color='red', node_size=10, tools=['hover', 'lasso_select'])
        if bounds is None:
            return tri.clone(([], tri.nodes.clone([], vdims=tri.nodes.vdims))).opts(**opts)
        x0, y0, x1, y1 = bounds
        simplices, nodes = self.spatial_select(tri, (x0, x1), (y0, y1))
        self._current = nodes
        return tri.clone((simplices, tri.nodes.clone(nodes, vdims=tri.nodes.vdims))).opts(**opts)

    def panel(self):
        return pn.Column(
            self.param.apply_edits,
            (self.shaded * self.selected).opts(responsive=True, min_height=1000, projection=self.object.crs),
            sizing_mode='stretch_width'
        )
