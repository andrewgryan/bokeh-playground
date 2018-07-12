"""Prototype to play with HTML bokeh elements"""
import bokeh.plotting
import bokeh.models
import bokeh.layouts

import datetime as dt
from functools import wraps
class throttle(object):
    def __init__(self, milliseconds=0, seconds=0):
        self.period = dt.timedelta(milliseconds=milliseconds,
                                   seconds=seconds,
                                   minutes=0,
                                   hours=0)
        self.last_call = dt.datetime.min

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            now = dt.datetime.now()
            duration = now - self.last_call
            if duration > self.period:
                self.last_call = now
                return fn(*args, **kwargs)
        return wrapper


class Zoom(object):
    def __init__(self, figure):
        self.figure = figure
        self.figure.x_range.on_change("start", self.on_change_x)
        self.figure.x_range.on_change("end", self.on_change_x)
        self.figure.y_range.on_change("start", self.on_change_y)
        self.figure.y_range.on_change("end", self.on_change_y)

    def on_change_x(self, attr, old, new):
        self.render()

    def on_change_y(self, attr, old, new):
        self.render()

    @throttle(700)
    def render(self):
        self.draw(self.figure.x_range.start,
                  self.figure.x_range.end,
                  self.figure.y_range.start,
                  self.figure.y_range.end)

    def draw(self, x_min, x_max, y_min, y_max):
        stamp = dt.datetime.now().strftime("%H:%M:%S.%f")
        print(stamp, x_min, x_max, y_min, y_max)


def main(bokeh_id):
    figure = bokeh.plotting.figure(sizing_mode="stretch_both",
                                   match_aspect=True)
    zoom = Zoom(figure)

    figure.circle([1, 2, 3], [1, 2, 3])

    # Make a bokeh document and serve it
    page = bokeh.layouts.column(figure)
    if bokeh_id == "__main__":
        bokeh.plotting.show(page)
    else:
        bokeh.io.curdoc().add_root(page)

main(__name__)
