import {HoverTool, HoverToolView} from "models/tools/inspectors/hover_tool"
import {MoveEvent} from "core/ui_events"
import * as p from "core/properties"

class SlideToolView extends HoverToolView {
    model: SlideTool
    _move(ev: MoveEvent) {
        console.log(this.model.span)
        this.model.span.location = 2
        super(ev)
    }
}

export class SlideTool extends HoverTool {
    default_view = SlideToolView
    type = "SlideTool"
    tool_name = "Slide"
}
SlideTool.define({
    span: [p.Instance]
})
