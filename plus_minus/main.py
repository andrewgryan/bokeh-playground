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

    def unique(self):
        return Unique(self)

    def log(self):
        return Log(self)


class Log(Stream):
    def __init__(self, stream):
        stream.register(self)
        super().__init__()

    def notify(self, value):
        print(value)
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


class Filter(Stream):
    def __init__(self, stream, criteria):
        self.criteria = criteria
        stream.register(self)
        super().__init__()

    def notify(self, value):
        if not self.criteria(value):
            self.emit(value)


class Unique(Stream):
    def __init__(self, stream):
        stream.register(self)
        super().__init__()

    def notify(self, value):
        if not hasattr(self, 'current'):
            self.current = value
            self.emit(value)
        elif value != self.current:
            self.current = value
            self.emit(value)


def to_text(number):
    return "Number: {}".format(number)


import datetime as dt
def to_time(times, index):
    return times[index % len(times)]


def format_time(time):
    return "{:%Y%m%d %H:%M}".format(time)


def bounded_sum(minimum, maximum, total, value):
    if (total + value) >= maximum:
        return total
    if (total + value) < minimum:
        return total
    return total + value


def plus_button(stream):
    btn = bokeh.models.Button(label="+")
    btn.on_click(lambda: stream.emit(+1))
    return btn


def minus_button(stream):
    btn = bokeh.models.Button(label="-")
    btn.on_click(lambda: stream.emit(-1))
    return btn


def main():
    times = [dt.datetime(2018, 1, 1),
             dt.datetime(2018, 1, 2),
             dt.datetime(2018, 1, 3)]
    numbers = Stream()
    totals = numbers.scan(0, partial(bounded_sum, 0, len(times)))
    totals = totals.unique().log()
    text = totals.map(to_text)
    p = bokeh.models.widgets.Paragraph(text="")
    Paragraph(p, text)

    time_getter = partial(to_time, times)
    text = totals.map(time_getter).map(format_time)
    current_p = bokeh.models.widgets.Paragraph(text="")
    current_date = Paragraph(current_p, text)

    document = bokeh.plotting.curdoc()
    document.add_root(bokeh.layouts.row(current_p, p))

    plus_btn = plus_button(numbers)
    minus_btn = minus_button(numbers)
    document.add_root(bokeh.layouts.row(plus_btn, minus_btn))

    plus_btn = plus_button(numbers)
    minus_btn = minus_button(numbers)
    document.add_root(bokeh.layouts.row(plus_btn, minus_btn))

    plus_btn = plus_button(numbers)
    minus_btn = minus_button(numbers)
    document.add_root(bokeh.layouts.row(plus_btn, minus_btn))


if __name__ == '__main__' or __name__.startswith("bk"):
    main()
