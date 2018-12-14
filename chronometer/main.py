import numpy as np
import datetime as dt
import bokeh.plotting
import bokeh.models
import bokeh.events
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from functools import partial
import rx


def main(
        plus_button=None,
        minus_button=None):
    document = bokeh.plotting.curdoc()
    source = bokeh.models.ColumnDataSource({
        "valid": [],
        "offset": [],
        "z": []
        })
    widgets = chronometer(
            valid="valid",
            offset="offset",
            start="z",
            source=source,
            plus_button=plus_button,
            minus_button=minus_button)
    figure, radio_group, plus_button, minus_button = widgets
    layout = bokeh.layouts.layout([
        [radio_group, plus_button, minus_button],
        [figure]])

    div = bokeh.models.Div()
    def view(div):
        def wrapper(state):
            x, y, z = state
            template = "<p>Valid date: {}</br>Start date: {}</br>Offset: {}</p>"
            msg = template.format(x, z, "T+{}".format(str(y)))
            div.text = msg
        return wrapper

    def model(source,
            valid="x",
            offset="y"):
        def wrapper(new):
            i = new[0]
            x, y, z = (
                    source.data[valid][i],
                    source.data[offset][i],
                    source.data["z"][i])
            if not isinstance(x, dt.datetime):
                x = dt.datetime.fromtimestamp(x / 1000.)
            if not isinstance(z, dt.datetime):
                z = dt.datetime.fromtimestamp(z / 1000.)
            return x, y, z
        return wrapper

    stream = rx.Stream()
    source.selected.on_change('indices', rx.callback(stream))
    stream = stream.map(model(
        source,
        valid="valid",
        offset="offset")).map(view(div))

    def add_time(source):
        i = 0
        def wrapper():
            nonlocal i
            start = dt.datetime(2018, 12, 1)
            offset = i * 12
            valid = start + dt.timedelta(hours=offset)
            source.stream({
                    "valid": [valid],
                    "offset": [offset],
                    "z": [start]
                    })
            i += 1
        return wrapper

    start_button = bokeh.models.Button(label="Add time")
    start_button.on_click(add_time(source))

    document.add_root(start_button)
    document.add_root(bokeh.layouts.widgetbox(div))
    document.add_root(layout)


def chronometer(
        valid=None,
        offset=None,
        start=None,
        source=None,
        radio_group=None,
        plus_button=None,
        minus_button=None,
        selectors=None):
    """Time/forecast exploration widget

    Creates a figure with glyphs for each point in
    time/forecast space along with buttons and a radio
    group to navigate
    """
    msg = ("please specify 'valid', 'start' and 'offset' "
           "keywords")
    assert valid is not None, msg
    assert start is not None, msg
    assert offset is not None, msg
    if radio_group is None:
        radio_group = bokeh.models.RadioGroup(labels=[
            "Time", "Forecast", "Run"],
            inline=True,
            width=210)
    if selectors is None:
        strategy = partial(select_pts, valid=valid, start=start, offset=offset)
        select_valid = partial(strategy, method=valid_time)
        select_lead = partial(strategy, method=lead_time)
        select_run = partial(strategy, method=run)
        selectors = {
            0: select_valid,
            1: select_lead,
            2: select_run,
        }
    if plus_button is None:
        plus_button = bokeh.models.Button(
                label="+",
                width=50)
    if minus_button is None:
        minus_button = bokeh.models.Button(
                label="-",
                width=50)
    hover_tool = bokeh.models.HoverTool(
            tooltips=[
                ('valid', '@' + valid + '{%F %T}'),
                ('start', '@' + start + '{%F %T}'),
                ('length', 'T+@' + offset)
                ],
            formatters={
                valid: 'datetime',
                start: 'datetime'
                })
    pan_tool = bokeh.models.PanTool(dimensions="width")
    tap_tool = bokeh.models.TapTool()
    figure = bokeh.plotting.figure(x_axis_type='datetime',
                                   plot_height=200,
                                   plot_width=330,
                                   tools=[
                                       tap_tool,
                                       hover_tool,
                                       pan_tool,
                                       "xwheel_zoom"],
                                   active_scroll="xwheel_zoom",
                                   toolbar_location=None)
    figure.toolbar.active_inspect = hover_tool
    figure.ygrid.grid_line_color = None

    figure.xaxis.axis_label = "Validity time"
    figure.xaxis.axis_label_text_font_size = "10px"
    figure.yaxis.axis_label = "Forecast length"
    figure.yaxis.axis_label_text_font_size = "10px"
    offsets = source.data[offset][:]
    if len(offsets) > 0:
        figure.yaxis.ticker = ticks(max(offsets))
    renderer = figure.square(
            x=valid,
            y=offset,
            source=source,
            size=8,
            line_color=None,
            nonselection_alpha=1,
            nonselection_line_color=None)
    tap_tool.renderers = [renderer]

    second_source = bokeh.models.ColumnDataSource({
        valid: [],
        offset: [],
        start: []
        })
    renderer = figure.square(
            x=valid,
            y=offset,
            size=8,
            source=second_source)
    renderer.selection_glyph = bokeh.models.Square(
            fill_alpha=1,
            fill_color="Red",
            line_color="Black")
    renderer.nonselection_glyph = bokeh.models.Square(
            fill_alpha=1,
            fill_color="White",
            line_color="Black")

    selected = rx.Stream()
    source.selected.on_change('indices', rx.callback(selected))
    selected.log()

    def all_not_none(items):
        return all(item is not None for item in items)

    active = rx.Stream()
    radio_group.on_change("active", rx.callback(active))
    changes = rx.combine_latest(
            active.map(lambda i: selectors[i]),
            selected).filter(all_not_none)

    def render(
            source,
            highlight_source,
            valid="x",
            offset="y",
            start="z"):
        """Updates highlight column data source"""
        def wrapper(event):
            selector, indices = event
            if len(indices) == 0:
                highlight_source.data = {
                        valid: [],
                        offset: [],
                        start: []}
                highlight_source.selected.indices = []
            else:
                index = indices[0]
                pts = selector(source, index)
                indices = [pts[0].tolist().index(index)]
                x = np.asarray(source.data[valid])[pts]
                y = np.asarray(source.data[offset])[pts]
                z = np.asarray(source.data[start])[pts]
                highlight_source.data = {
                        valid: x,
                        offset: y,
                        start: z}
                highlight_source.selected.indices = indices
        return wrapper

    changes.map(render(source, second_source,
        valid=valid,
        offset=offset,
        start=start))

    second_selected = rx.Stream()
    second_source.selected.on_change('indices', rx.callback(second_selected))
    second_selected.log()

    plus = rx.Stream()
    plus_button.on_click(rx.click(plus))
    plus = plus.map(+1)

    minus = rx.Stream()
    minus_button.on_click(rx.click(minus))
    minus = minus.map(-1)

    steps = rx.Merge(plus, minus)
    steps.map(move(second_source, valid=valid)).map(sync(
        source,
        second_source,
        valid=valid,
        offset=offset))

    if len(source.data[valid]) > 0:
        source.selected.indices = [0]

    if radio_group.active is not None:
        active.emit(radio_group.active)
    return figure, radio_group, plus_button, minus_button


def ticks(max_hour):
    """Choose appropriate tick locations for forecasts"""
    step_size = 3
    while max_hour >= (4 * step_size):
        step_size *= 2
    hour = 0
    ticks = []
    while (hour <= max_hour):
        ticks.append(hour)
        hour += step_size
    return ticks


def sync(large, small, valid="x", offset="y"):
    def wrapper(event):
        if len(small.selected.indices) == 0:
            return
        si = small.selected.indices[0]
        li = large.selected.indices[0]
        sx = np.asarray(small.data[valid][:])
        sy = np.asarray(small.data[offset][:])
        lx = np.asarray(large.data[valid][:])
        ly = np.asarray(large.data[offset][:])
        if ((lx[li] == sx[si]) and (ly[li] == sy[si])):
            return
        pts = np.where((lx == sx[si]) & (ly == sy[si]))
        large.selected.indices = pts[0].tolist()
    return wrapper


def move(source, valid="x"):
    def wrapper(steps):
        if len(source.selected.indices) > 0:
            i = source.selected.indices[0]
            n = len(source.data[valid])
            source.selected.indices = [(i + steps) % n]
        return source.selected.indices
    return wrapper


def select_pts(source, index, valid="x", start="z", offset="y", method=None):
    x = np.asarray(source.data[valid])
    y = np.asarray(source.data[offset])
    z = np.asarray(source.data[start])
    return method(x, y, z, index)


def valid_time(x, y, z, i):
    return np.where(x == x[i])


def lead_time(x, y, z, i):
    return np.where(y == y[i])


def run(x, y, z, i):
    return np.where(z == z[i])


if __name__.startswith('bk'):
    main()
