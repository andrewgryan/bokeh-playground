import {span, empty} from "core/dom"
import * as p from "core/properties"
import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"


export class CustomView extends LayoutDOMView {
    initialize(options) {
        super.initialize(options)
        this.render()
        this.connect(
            this.model.slider.change,
            () => this.render())
    }

    render() {
        empty(this.el)
        this.el.appendChild(
            span({
                style: {}
            }, `${this.model.text}: ${this.model.slider.value}`))
    }
}


export class Custom extends LayoutDOM {
    default_view = CustomView
    type = "Custom"
}
Custom.define({
    text: [ p.String ],
    slider: [ p.Any ]
})
