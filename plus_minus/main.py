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


class Scan(Stream):
    def __init__(self, stream, initial, combine):
        self.state = initial
        self.combine = combine
        stream.register(self)
        super().__init__()

    def notify(self, value):
        self.state = self.combine(self.state, value)
        self.emit(self.state)


def to_text(number):
    return "Number: {}".format(number)


def add(a, b):
    return a + b

numbers = Stream()
totals = Scan(numbers, 0, add)
text = Map(totals, to_text)
paragraph = Paragraph(text)

plus_btn = bokeh.models.Button(label="+")
plus_btn.on_click(lambda: numbers.emit(+1))

minus_btn = bokeh.models.Button(label="-")
minus_btn.on_click(lambda: numbers.emit(-1))

document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.row(paragraph.widget, plus_btn, minus_btn))
