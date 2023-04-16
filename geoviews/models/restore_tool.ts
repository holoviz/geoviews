import * as p from "@bokehjs/core/properties"
import {ActionTool, ActionToolView} from "@bokehjs/models/tools/actions/action_tool"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"
import {tool_icon_undo} from "@bokehjs/styles/icons.css"


export class RestoreToolView extends ActionToolView {
  model: RestoreTool

  doit(): void {
    const sources: any = this.model.sources;
    for (const source of sources) {
      if (!source.buffer || (source.buffer.length == 0)) { continue; }
      source.data = source.buffer.pop();
      source.change.emit();
      source.properties.data.change.emit();
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
  properties: RestoreTool.Props

  constructor(attrs?: Partial<RestoreTool.Attrs>) {
    super(attrs)
  }

  static __module__ = "geoviews.models.custom_tools"

  static {
    this.prototype.default_view = RestoreToolView

    this.define<RestoreTool.Props>(({Array, Ref}) => ({
      sources: [ Array(Ref(ColumnDataSource)), [] ],
    }))
  }

  tool_name = "Restore"
  tool_icon = tool_icon_undo
}
