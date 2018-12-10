import {InputWidget, InputWidgetView} from "models/widgets/input_widget"
import {div, label} from "core/dom"

export class ChronometerView extends InputWidgetView {
    model: Chronometer
    render() {
        this.el.appendChild(div({class: "chronometer"}, "Hello, world!"))
        return this
    }
}

export class Chronometer extends InputWidget {
    default_view = ChronometerView
    type = "Chronometer"
}
