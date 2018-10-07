import bokeh.plotting
import bokeh.models


class Paragraph(object):
    def __init__(self, stream):
        stream.register(self)
        self.widget = bokeh.models.widgets.Paragraph(text="")

    def notify(self, value):
        self.widget.text = value


class Stream(object):
    def __init__(self):
        self.subscribers = []

    def register(self, subscriber):
        self.subscribers.append(subscriber)

    def emit(self, value):
        for subscriber in self.subscribers:
            subscriber.notify(value)


class Echo(Stream):
    def notify(self, value):
        self.emit(value)


class Map(Stream):
    def __init__(self, stream, transform):
        stream.register(self)
        self.transform = transform
        super().__init__()

    def notify(self, value):
        self.emit(self.transform(value))


class Numbers(Stream):
    def plus(self):
        self.emit(+1)

    def minus(self):
        self.emit(-1)


numbers = Numbers()
text = Map(numbers, str)
paragraph = Paragraph(text)

plus_btn = bokeh.models.Button(label="+")
plus_btn.on_click(numbers.plus)

minus_btn = bokeh.models.Button(label="-")
minus_btn.on_click(numbers.minus)

document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.row(paragraph.widget, plus_btn, minus_btn))
