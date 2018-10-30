import time
import bokeh.models
import bokeh.layouts
import bokeh.plotting


class Bucket(object):
    def __init__(self):
        self.items = []

    def accumulate(self, item):
        self.items.append(item)

    def summary(self):
        return len(self.items)

    def reset(self):
        self.items = []


bucket = Bucket()
p = bokeh.models.Paragraph(text="No clicks")


def on_click_event():
    bucket.accumulate("event")


def on_click_reset():
    p.text = "{} click(s)".format(bucket.summary())
    bucket.reset()


buttons = [
    bokeh.models.Button(),
    bokeh.models.Button()
]
on_clicks = [
    on_click_event,
    on_click_reset,
]
for button, on_click in zip(buttons, on_clicks):
    button.on_click(on_click)

document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.column(
    p,
    *buttons))
