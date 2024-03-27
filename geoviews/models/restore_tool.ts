import type * as p from "@bokehjs/core/properties"
import type {Data} from "@bokehjs/core/types"
import {ActionTool, ActionToolView} from "@bokehjs/models/tools/actions/action_tool"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"
import {tool_icon_undo} from "@bokehjs/styles/icons.css"

type BufferedColumnDataSource = ColumnDataSource & {buffer?: Data[]}

export class RestoreToolView extends ActionToolView {
  declare model: RestoreTool

  doit(): void {
    const sources = this.model.sources as BufferedColumnDataSource[]
    for (const source of sources) {
      const new_data = source.buffer?.pop()
      if (new_data == null) {
        continue
      }
      source.data = new_data
      source.change.emit()
      source.properties.data.change.emit()
    }
  }
}

export namespace RestoreTool {
  export type Attrs = p.AttrsOf<Props>
  export type Props = ActionTool.Props & {
    sources: p.Property<ColumnDataSource[]>
  }
}

export interface RestoreTool extends RestoreTool.Attrs {}

export class RestoreTool extends ActionTool {
  declare properties: RestoreTool.Props

  constructor(attrs?: Partial<RestoreTool.Attrs>) {
    super(attrs)
  }

  static override __module__ = "geoviews.models.custom_tools"

  static {
    this.prototype.default_view = RestoreToolView

    this.define<RestoreTool.Props>(({Array, Ref}) => ({
      sources: [ Array(Ref(ColumnDataSource)), [] ],
    }))
  }

  override tool_name = "Restore"
  override tool_icon = tool_icon_undo
}
