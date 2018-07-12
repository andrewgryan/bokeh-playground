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

def zoom(attr, old, new):
    stamp = dt.datetime.now().strftime("%H:%M:%S.%f")
    print("normal", stamp)

@throttle(100)
def wrapped_zoom(attr, old, new):
    stamp = dt.datetime.now().strftime("%H:%M:%S.%f")
    print("wrapped", stamp)

def main(bokeh_id):
    figure = bokeh.plotting.figure(sizing_mode="stretch_both",
                                   match_aspect=True)
    figure.x_range.on_change("start", zoom)
    figure.x_range.on_change("start", wrapped_zoom)

    figure.circle([1, 2, 3], [1, 2, 3])

    # Make a bokeh document and serve it
    page = bokeh.layouts.column(figure)
    if bokeh_id == "__main__":
        bokeh.plotting.show(page)
    else:
        bokeh.io.curdoc().add_root(page)

main(__name__)
