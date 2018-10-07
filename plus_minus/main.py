import bokeh.plotting
import bokeh.models


class Paragraph(object):
    def __init__(self, stream):
        stream.register(self)
        self.widget = bokeh.models.widgets.Paragraph(text="")

    def notify(self, value):
        self.widget.text = value


class Text(object):
    def __init__(self):
        self.subscribers = []

    def register(self, subscriber):
        self.subscribers.append(subscriber)

    def plus(self):
        for subscriber in self.subscribers:
            subscriber.notify("Plus")

    def minus(self):
        for subscriber in self.subscribers:
            subscriber.notify("Minus")


text = Text()
paragraph = Paragraph(text)

plus_btn = bokeh.models.Button(label="+")
plus_btn.on_click(text.plus)

minus_btn = bokeh.models.Button(label="-")
minus_btn.on_click(text.minus)

document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.row(paragraph.widget, plus_btn, minus_btn))
