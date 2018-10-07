import bokeh.plotting
import bokeh.models


class Paragraph(object):
    def __init__(self, text):
        self.text = text
        self.text.register(self)
        self.widget = bokeh.models.widgets.Paragraph(text=text.value)

    def notify(self):
        self.widget.text = self.text.value


class Text(object):
    def __init__(self):
        self.value = ""
        self.subscribers = []

    def register(self, subscriber):
        self.subscribers.append(subscriber)

    def plus(self):
        self.value = "Plus"
        for subscriber in self.subscribers:
            subscriber.notify()

    def minus(self):
        self.value = "Minus"
        for subscriber in self.subscribers:
            subscriber.notify()


text = Text()
paragraph = Paragraph(text)

plus_btn = bokeh.models.Button(label="+")
plus_btn.on_click(text.plus)

minus_btn = bokeh.models.Button(label="-")
minus_btn.on_click(text.minus)

document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.row(paragraph.widget, plus_btn, minus_btn))
