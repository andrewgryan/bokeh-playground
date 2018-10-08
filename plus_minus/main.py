import bokeh.plotting
import bokeh.models


class Paragraph(object):
    def __init__(self, widget, stream):
        self.widget = widget
        stream.register(self)

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

    def map(self, transform):
        return Map(self, transform)

    def scan(self, initial, combine):
        return Scan(self, initial, combine)


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


def main():
    numbers = Stream()
    totals = numbers.scan(0, lambda x, y: x + y)
    text = totals.map(to_text)
    p = bokeh.models.widgets.Paragraph(text="")
    Paragraph(p, text)

    plus_btn = bokeh.models.Button(label="+")
    plus_btn.on_click(lambda: numbers.emit(+1))

    minus_btn = bokeh.models.Button(label="-")
    minus_btn.on_click(lambda: numbers.emit(-1))

    document = bokeh.plotting.curdoc()
    document.add_root(bokeh.layouts.row(p, plus_btn, minus_btn))


if __name__ == '__main__' or __name__.startswith("bk"):
    main()
