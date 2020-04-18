import param
import panel as pn
import numpy as np
import pandas as pd

from holoviews.core import DynamicMap
from holoviews.element import Segments
from holoviews.streams import BoundsXY, Selection1D, Stream

from  .element import TriMesh
from .streams import TriMeshEdit



def connect_tri_edges_pd(trimesh):
    """
    Given a TriMesh element containing abstract edges compute edge
    segments directly connecting the source and target nodes. This
    operation depends on pandas and is a lot faster than the pure
    NumPy equivalent.
    """
    edges = trimesh.dframe().copy()
    edges.index.name = 'trimesh_edge_index'
    edges = edges.reset_index()
    node_index = trimesh.nodes.kdims[2].name
    nodes = trimesh.nodes.dframe().set_index(node_index)
    v1, v2, v3 = trimesh.kdims
    x, y, idx = trimesh.nodes.kdims[:3]

    df = pd.merge(edges, nodes, left_on=[v1.name], right_on=[node_index])
    df = df.rename(columns={x.name: 'x0', y.name: 'y0'})
    df = pd.merge(df, nodes, left_on=[v2.name], right_on=[node_index])
    df = df.rename(columns={x.name: 'x1', y.name: 'y1'})
    df = pd.merge(df, nodes, left_on=[v3.name], right_on=[node_index])
    df = df.rename(columns={x.name: 'x2', y.name: 'y2'})
    df = df.sort_values('trimesh_edge_index').drop(['trimesh_edge_index'], axis=1)
    segs1 = df[['x0', 'y0', 'x1', 'y1', 'v0', 'v1']]
    segs2 = df[['x1', 'y1', 'x2', 'y2', 'v1', 'v2']].rename(columns={
        'x1': 'x0', 'y1': 'y0', 'x2': 'x1',
        'y2': 'y1', 'v1': 'v0', 'v2': 'v1'
    })
    segs3 = df[['x2', 'y2', 'x0', 'y0', 'v2', 'v0']].rename(columns={
        'x2': 'x0', 'y2': 'y0', 'x0': 'x1',
        'y0': 'y1', 'v2': 'v0', 'v0': 'v1'
    })
    return pd.concat([segs1, segs2, segs3])


class TriMeshEditor(param.Parameterized):

    apply_edits = param.Action(default=lambda self: self.param.trigger('apply_edits'))

    object = param.ClassSelector(class_=TriMesh, doc="""
        The Element to edit and annotate.""")

    def __init__(self, trimesh, **params):
        from holoviews.operation.datashader import datashade
        super(TriMeshEditor, self).__init__(object=trimesh, **params)
        self._object = DynamicMap(self._get_object)
        self._bounds = BoundsXY(source=self._object)
        self._vertex_selection = Selection1D()
        self.selected = self._object.apply(
            self.subselect, bounds=self._bounds.param.bounds,
            vertices=self._vertex_selection.param.index
        )
        self._stream = TriMeshEdit(source=self.selected)
        self._trigger = Stream.define('Trigger', active=False)(transient=True)
        self.selected_vertices = self.selected.apply(
            self._get_vertices, link_inputs=False, streams=[self._stream, self._trigger]
        )
        self._vertex_selection.source = self.selected_vertices
        self._simplex_edits = []
        self._nodes = None
        self._simplices = None
        self._temp = None
        self._prev_bounds = None
        self.shaded = datashade(self._object, aggregator='any', interpolation=None, link_inputs=False)

    def _get_vertices(self, trimesh, data, active):
        if self._stream._triggering or active:
            nodes, simplices = self._edit_nodes(self._nodes, self._simplices)
            nodes = trimesh.nodes.clone(nodes, vdims=trimesh.nodes.vdims)
            trimesh = trimesh.clone((simplices, nodes))
        if hasattr(trimesh, '_wireframe'):
            segments = element._wireframe.data
        else:
            segments = connect_tri_edges_pd(trimesh)
        self._vertices = segments
        return Segments(segments).opts(
            selection_color='red', line_width=4, tools=['tap'],
            selected=[]
        )

    @param.depends('object')
    def _get_object(self):
        return self.object

    @param.depends('apply_edits', watch=True)
    def _edit(self):
        tri = self.object if self._temp is None else self._temp
        self._temp = None
        nodes = tri.nodes
        nodes, simplices = self._edit_nodes(nodes.dframe(), tri.data)
        self.object = tri.clone((simplices, nodes))

    def _edit_nodes(self, nodes, simplices):
        index = self.object.nodes.kdims[2].name
        edited = self._stream.element.dframe().set_index(index)
        original = nodes.set_index(index)
        original.update(edited)
        if len(edited) and len(edited) != len(self._nodes):
            deleted = set(self._nodes[index].values) - set(edited.index.values)
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
        return original, simplices

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

    @classmethod
    def _flip_simplex(cls, tri, v0, v1):
        vs = v0, v1
        vn1, vn2, vn3 = vns = [d.name for d in tri.kdims[:3]]
        ts = np.where((
            tri.data[vn1].isin(vs).astype(int) +
            tri.data[vn2].isin(vs).astype(int) +
            tri.data[vn3].isin(vs).astype(int)) == 2
        )[0]
        if len(ts) != 2:
            return tri
        simplices = tri.data.copy()
        tris = simplices[vns].iloc[ts]
        c1, c2 = [list(r).index(True) for i, r in (~tris.isin([v0, v1])).iterrows()]
        o1, o2 = tris.iloc[0, c1].item(), tris.iloc[1, c2].item()
        inds = [list(simplices.columns).index(v) for v in vns]
        simplices.iloc[ts[0], inds] = [o1, v0, o2]
        simplices.iloc[ts[1], inds] = [o2, v1, o1]
        return tri.clone((simplices, tri.nodes))

    def subselect(self, tri, bounds, vertices=[]):
        if self._temp is not None:
            tri = self._temp
        opts = dict(node_color='red', node_size=10, tools=['hover', 'lasso_select'])
        if bounds is None:
            return tri.clone(([], tri.nodes.clone([], vdims=tri.nodes.vdims))).opts(**opts)
        if vertices:
            self._vertex_selection.update(index=[])
            df = self._vertices.iloc[vertices[0]]
            self._temp = tri = self._flip_simplex(tri, df.v0.item(), df.v1.item())
        x0, y0, x1, y1 = bounds
        simplices, nodes = self.spatial_select(tri, (x0, x1), (y0, y1))
        self._nodes = nodes
        self._simplices = simplices
        if vertices:
            self._trigger.event(active=True)
        if bounds == self._prev_bounds:
            nodes, simplices = self._edit_nodes(nodes, simplices)
        self._prev_bounds = bounds
        return tri.clone((simplices, tri.nodes.clone(nodes, vdims=tri.nodes.vdims))).opts(**opts)

    def panel(self):
        return pn.Column(
            self.param.apply_edits,
            (self.shaded * self.selected_vertices * self.selected).opts(
                responsive=True, min_height=1000, projection=self.object.crs
            ),
            sizing_mode='stretch_width'
        )
