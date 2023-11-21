from holoviews.streams import PolyEdit, PolyDraw


class PolyVertexEdit(PolyEdit):
    """
    Attaches a PolyVertexEditTool and syncs the datasource.

    shared: boolean
        Whether PolyEditTools should be shared between multiple elements

    node_style: dict
        A dictionary specifying the style options for the intermediate nodes.

    feature_style: dict
        A dictionary specifying the style options for the intermediate nodes.
    """

    def __init__(self, node_style=None, feature_style=None, **params):
        if feature_style is None:
            feature_style = {}
        if node_style is None:
            node_style = {}
        self.node_style = node_style
        self.feature_style = feature_style
        super().__init__(**params)


class PolyVertexDraw(PolyDraw):
    """
    Attaches a PolyVertexDrawTool and syncs the datasource.

    shared: boolean
        Whether PolyEditTools should be shared between multiple elements

    node_style: dict
        A dictionary specifying the style options for the intermediate nodes.

    feature_style: dict
        A dictionary specifying the style options for the intermediate nodes.
    """

    def __init__(self, node_style=None, feature_style=None, **params):
        if feature_style is None:
            feature_style = {}
        if node_style is None:
            node_style = {}
        self.node_style = node_style
        self.feature_style = feature_style
        super().__init__(**params)
