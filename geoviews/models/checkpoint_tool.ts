import * as p from "@bokehjs/core/properties"
import {copy} from "@bokehjs/core/util/array"
import {ActionTool, ActionToolView} from "@bokehjs/models/tools/actions/action_tool"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"
import {tool_icon_save} from "@bokehjs/styles/icons.css"


export class CheckpointToolView extends ActionToolView {
  model: CheckpointTool

  doit(): void {
    const sources: any = this.model.sources;
    for (const source of sources) {
      if (!source.buffer) { source.buffer = [] }
      let data_copy: any = {};
      for (const key in source.data) {
        const column = source.data[key];
        const new_column = []
        for (const arr of column) {
          if (Array.isArray(arr) || (ArrayBuffer.isView(arr))) {
            new_column.push(copy((arr as any)))
          } else {
            new_column.push(arr)
          }
        }
        data_copy[key] = new_column;
      }
      source.buffer.push(data_copy)
    }
  }
}

export namespace CheckpointTool {
  export type Attrs = p.AttrsOf<Props>
  export type Props = ActionTool.Props & {
    sources: p.Property<ColumnDataSource[]>
  }
}

export interface CheckpointTool extends CheckpointTool.Attrs {}

export class CheckpointTool extends ActionTool {
  properties: CheckpointTool.Props

  constructor(attrs?: Partial<CheckpointTool.Attrs>) {
    super(attrs)
  }

  static __module__ = "geoviews.models.custom_tools"

  static {
    this.prototype.default_view = CheckpointToolView

    this.define<CheckpointTool.Props>(({Array, Ref}) => ({
      sources: [ Array(Ref(ColumnDataSource)), [] ],
    }))
  }

  tool_name = "Checkpoint"
  tool_icon = tool_icon_save
}
