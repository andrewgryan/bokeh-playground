import bokeh.plotting
import bokeh.models
from functools import partial


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

    def filter(self, criteria):
        return Filter(self, criteria)


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


class Filter(Stream):
    def __init__(self, stream, criteria):
        self.criteria = criteria
        stream.register(self)
        super().__init__()

    def notify(self, value):
        if not self.criteria(value):
            self.emit(value)


def to_text(number):
    return "Number: {}".format(number)


import datetime as dt
def to_time(times, index):
    return times[index % len(times)]


def format_time(time):
    return "{:%Y%m%d %H:%M}".format(time)


def main():
    times = [dt.datetime(2018, 1, 1),
             dt.datetime(2018, 1, 2),
             dt.datetime(2018, 1, 3)]

    numbers = Stream()
    def list_bounds(items, total, value):
        if (total + value) >= len(items):
            return total
        if (total + value) < 0:
            return total
        return total + value
    time_bounds = partial(list_bounds, times)
    totals = numbers.scan(0, time_bounds)
    text = totals.map(to_text)
    p = bokeh.models.widgets.Paragraph(text="")
    Paragraph(p, text)

    plus_btn = bokeh.models.Button(label="+")
    plus_btn.on_click(lambda: numbers.emit(+1))

    minus_btn = bokeh.models.Button(label="-")
    minus_btn.on_click(lambda: numbers.emit(-1))

    time_getter = partial(to_time, times)
    text = totals.map(time_getter).map(format_time)
    current_p = bokeh.models.widgets.Paragraph(text="")
    current_date = Paragraph(current_p, text)

    document = bokeh.plotting.curdoc()
    document.add_root(current_p)
    document.add_root(bokeh.layouts.row(p, plus_btn, minus_btn))


if __name__ == '__main__' or __name__.startswith("bk"):
    main()
