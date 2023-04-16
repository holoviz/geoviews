import * as p from "@bokehjs/core/properties"
import {ActionTool, ActionToolView} from "@bokehjs/models/tools/actions/action_tool"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"
import {tool_icon_reset} from "@bokehjs/styles/icons.css"


export class ClearToolView extends ActionToolView {
  model: ClearTool

  doit(): void {
    for (var source of this.model.sources) {
      for (const column in source.data) {
        source.data[column] = []
      }
      source.change.emit();
      source.properties.data.change.emit();
    }
  }
}

export namespace ClearTool {
  export type Attrs = p.AttrsOf<Props>
  export type Props = ActionTool.Props & {
    sources: p.Property<ColumnDataSource[]>
  }
}

export interface ClearTool extends ClearTool.Attrs {}

export class ClearTool extends ActionTool {
  properties: ClearTool.Props

  constructor(attrs?: Partial<ClearTool.Attrs>) {
    super(attrs)
  }

  static __module__ = "geoviews.models.custom_tools"

  static {
    this.prototype.default_view = ClearToolView

    this.define<ClearTool.Props>(({Array, Ref}) => ({
      sources: [ Array(Ref(ColumnDataSource)), [] ],
    }))
  }

  tool_name = "Clear data"
  tool_icon = tool_icon_reset
}
