import {AbstractButton, AbstractButtonView} from "models/widgets/abstract_button"
import {ButtonClick} from "core/bokeh_events"
import * as p from "core/properties"

// Extra imports
import {button, i} from "core/dom"
import {bk_btn, bk_btn_type} from "styles/buttons"


export class FontAwesomeButtonView extends AbstractButtonView {
  model: FontAwesomeButton

  _render_button(...children: (string | HTMLElement)[]): HTMLButtonElement {
      let fontAwesomeClass = children[0]
      return button({
          type: "button",
          disabled: this.model.disabled,
          class: [bk_btn, bk_btn_type(this.model.button_type)]
      }, i({class: ["fas", fontAwesomeClass]}))
  }

  click(): void {
    this.model.clicks = this.model.clicks + 1
    this.model.trigger_event(new ButtonClick())
    super.click()
  }
}

export namespace FontAwesomeButton {
  export type Attrs = p.AttrsOf<Props>

  export type Props = AbstractButton.Props & {
    clicks: p.Property<number>
  }
}

export interface FontAwesomeButton extends FontAwesomeButton.Attrs {}

export class FontAwesomeButton extends AbstractButton {
  static __name__ = "FontAwesomeButton"
  properties: FontAwesomeButton.Props

  constructor(attrs?: Partial<FontAwesomeButton.Attrs>) {
    super(attrs)
  }

  static init_FontAwesomeButton(): void {
    this.prototype.default_view = FontAwesomeButtonView

    this.override({
      label: "fa-cog",
    })
  }
}
