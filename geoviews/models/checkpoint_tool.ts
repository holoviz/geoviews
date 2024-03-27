import type * as p from "@bokehjs/core/properties"
import {entries} from "@bokehjs/core/util/object"
import type {Data} from "@bokehjs/core/types"
import {copy} from "@bokehjs/core/util/array"
import {ActionTool, ActionToolView} from "@bokehjs/models/tools/actions/action_tool"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"
import {tool_icon_save} from "@bokehjs/styles/icons.css"

type BufferedColumnDataSource = ColumnDataSource & {buffer?: Data[]}

export class CheckpointToolView extends ActionToolView {
  declare model: CheckpointTool

  doit(): void {
    const sources = this.model.sources as BufferedColumnDataSource[]
    for (const source of sources) {
      if (source.buffer == null) {
        source.buffer = []
      }
      const data_copy: Data = {}
      for (const [key, column] of entries(source.data)) {
        const new_column = []
        for (const arr of column) {
          if (Array.isArray(arr) || ArrayBuffer.isView(arr)) {
            new_column.push(copy(arr as any))
          } else {
            new_column.push(arr)
          }
        }
        data_copy[key] = new_column
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
  declare properties: CheckpointTool.Props

  constructor(attrs?: Partial<CheckpointTool.Attrs>) {
    super(attrs)
  }

  static override __module__ = "geoviews.models.custom_tools"

  static {
    this.prototype.default_view = CheckpointToolView

    this.define<CheckpointTool.Props>(({Array, Ref}) => ({
      sources: [ Array(Ref(ColumnDataSource)), [] ],
    }))
  }

  override tool_name = "Checkpoint"
  override tool_icon = tool_icon_save
}
