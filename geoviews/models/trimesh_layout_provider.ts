import * as p from "@bokehjs/core/properties"
import {StaticLayoutProvider} from "@bokehjs/models/graphs/static_layout_provider"
import {ColumnarDataSource} from "@bokehjs/models/sources/columnar_data_source"

export namespace TriMeshLayoutProvider {
  export type Attrs = p.AttrsOf<Props>

  export type Props = StaticLayoutProvider.Props & {
    graph_layout: p.Property<{[key: string]: [number, number]}>
  }
}

export interface TriMeshLayoutProvider extends TriMeshLayoutProvider.Attrs {}

export class TriMeshLayoutProvider extends StaticLayoutProvider {
  properties: TriMeshLayoutProvider.Props

  static __module__ = "geoviews.models.graphs"

  constructor(attrs?: Partial<TriMeshLayoutProvider.Attrs>) {
    super(attrs)
  }

  get_edge_coordinates(edge_source: ColumnarDataSource): [any, any] {
    const xs: [number, number, number, number][] = []
    const ys: [number, number, number, number][] = []
    const n1 = edge_source.data.v1
    const n2 = edge_source.data.v2
    const n3 = edge_source.data.v3
    for (let i = 0, endi = n1.length; i < endi; i++) {
      const in_layout = ((this.graph_layout[n1[i]] != null) &&
						 (this.graph_layout[n2[i]] != null) &&
						 (this.graph_layout[n3[i]] != null))
      let v1, v2, v3
      if (in_layout)
        [v1, v2, v3] = [this.graph_layout[n1[i]], this.graph_layout[n2[i]], this.graph_layout[n3[i]]]
      else
        [v1, v2, v3] = [[NaN, NaN], [NaN, NaN], [NaN, NaN]]
      xs.push([v1[0], v2[0], v3[0], v1[0]])
      ys.push([v1[1], v2[1], v3[1], v1[1]])
    }
    return [xs, ys]
  }
}
