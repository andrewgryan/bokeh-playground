import bokeh.models
from bokeh.core.properties import Override, Int
from bokeh.events import ButtonClick


class FontAwesomeButton(bokeh.models.AbstractButton):
    __implementation__ = 'font_awesome_button.ts'

    label = Override(default="FontAwesomeButton")
    clicks = Int(0)
    def on_click(self, handler):
        ''' Set up a handler for button clicks.

        Args:
            handler (func) : handler function to call when button is clicked.

        Returns:
            None

        '''
        self.on_event(ButtonClick, handler)


    def js_on_click(self, handler):
        ''' Set up a JavaScript handler for button clicks. '''
        self.js_on_event(ButtonClick, handler)
