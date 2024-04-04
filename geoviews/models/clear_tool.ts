import type * as p from "@bokehjs/core/properties"
import {ActionTool, ActionToolView} from "@bokehjs/models/tools/actions/action_tool"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"
import {tool_icon_reset} from "@bokehjs/styles/icons.css"

export class ClearToolView extends ActionToolView {
  declare model: ClearTool

  doit(): void {
    for (const source of this.model.sources) {
      source.clear()
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
  declare properties: ClearTool.Props

  constructor(attrs?: Partial<ClearTool.Attrs>) {
    super(attrs)
  }

  static override __module__ = "geoviews.models.custom_tools"

  static {
    this.prototype.default_view = ClearToolView

    this.define<ClearTool.Props>(({Array, Ref}) => ({
      sources: [ Array(Ref(ColumnDataSource)), [] ],
    }))
  }

  override tool_name = "Clear data"
  override tool_icon = tool_icon_reset
}
