import numpy as np
import datetime as dt
import bokeh.plotting
import bokeh.models
import bokeh.events
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
import rx


def main():
    dates = np.array([
        dt.datetime(2018, 11, 30),
        dt.datetime(2018, 11, 30, 12),
        dt.datetime(2018, 12, 3, 12),
        dt.datetime(2018, 12, 5, 12),
        dt.datetime(2018, 12, 6, 0),
    ], dtype=object)
    dates = np.array([
        dt.datetime(2018, 11, 30) + i * dt.timedelta(hours=12)
        for i in range(100)], dtype=object)
    forecast_hours = np.array([6 * i for i in range(12)])

    # Display all dates
    div = bokeh.models.Div()
    xs = []
    ys = []
    zs = []
    for date in dates:
        y = forecast_hours.tolist()
        x = [date + dt.timedelta(hours=float(h))
            for h in forecast_hours]
        z = len(forecast_hours) * [date]
        xs += x
        ys += y
        zs += z
    x, y, z = xs, ys, zs

    document = bokeh.plotting.curdoc()

    source = bokeh.models.ColumnDataSource({
        "valid": x,
        "y": y,
        "z": z
        })
    layout, stream = chronometer(
            valid="valid",
            offset="y",
            start="z",
            source=source)

    def view(div):
        def wrapper(state):
            x, y, z = state
            template = "<p>Valid date: {}</br>Start date: {}</br>Offset: {}</p>"
            msg = template.format(x, z, "T+{}".format(str(y)))
            div.text = msg
        return wrapper
    stream.map(view(div))

    document.add_root(bokeh.layouts.widgetbox(div))
    document.add_root(layout)


def chronometer(
        valid=None,
        offset=None,
        start=None,
        source=None):
    """Time/forecast exploration widget

    Creates a figure with glyphs for each point in
    time/forecast space along with buttons and a radio
    group to navigate
    """
    if source is None:
        msg = "please specify 'valid', 'start' and 'offset'"
        assert valid is not None, msg
        assert start is not None, msg
        assert offset is not None, msg
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
    renderer = figure.square(x=valid, y=offset, size=8,
            source=source,
            line_color=None,
            nonselection_alpha=1,
            nonselection_line_color=None)
    tap_tool.renderers = [renderer]

    second_source = bokeh.models.ColumnDataSource({
        "x": [],
        "y": [],
        "z": []
        })
    renderer = figure.square(x="x", y="y", size=8,
            source=second_source)
    renderer.selection_glyph = bokeh.models.Square(
            fill_alpha=1,
            fill_color="Red",
            line_color="Black")
    renderer.nonselection_glyph = bokeh.models.Square(
            fill_alpha=1,
            fill_color="White",
            line_color="Black")

    def model(source):
        def wrapper(new):
            i = new[0]
            x, y, z = (
                    source.data["x"][i],
                    source.data["y"][i],
                    source.data["z"][i])
            if not isinstance(x, dt.datetime):
                x = dt.datetime.fromtimestamp(x / 1000.)
            if not isinstance(z, dt.datetime):
                z = dt.datetime.fromtimestamp(z / 1000.)
            return x, y, z
        return wrapper

    selected = rx.Stream()
    source.selected.on_change('indices', rx.callback(selected))

    rdo_grp = bokeh.models.RadioGroup(labels=[
        "Time", "Forecast", "Run"],
        inline=True,
        width=210)

    def all_not_none(items):
        return all(item is not None for item in items)

    stream = rx.Stream()
    rdo_grp.on_change("active", rx.callback(stream))
    method_stream = rx.Merge(
            stream.filter(lambda i: i == 0).map(lambda i: valid_time),
            stream.filter(lambda i: i == 1).map(lambda i: lead_time),
            stream.filter(lambda i: i == 2).map(lambda i: run))
    states = rx.combine_latest(
            method_stream,
            selected).filter(all_not_none)

    def render(full_source, small_source):
        def wrapper(event):
            method, _ = event
            data, indices = method(full_source)
            small_source.data = data
            small_source.selected.indices = indices
        return wrapper
    states.map(render(source, second_source))

    second_selected = rx.Stream()
    second_source.selected.on_change('indices', rx.callback(second_selected))
    second_selected.log()

    plus_btn = bokeh.models.Button(label="+", width=50)
    minus_btn = bokeh.models.Button(label="-", width=50)

    plus = rx.Stream()
    plus_btn.on_click(rx.click(plus))
    plus = plus.map(+1)

    minus = rx.Stream()
    minus_btn.on_click(rx.click(minus))
    minus = minus.map(-1)

    steps = rx.Merge(plus, minus)
    steps.map(move(second_source)).map(sync(source, second_source))
    chronometer_stream = selected.map(model(source))

    rdo_grp.active = 1
    if len(source.data[valid]) > 0:
        source.selected.indices = [0]
    return bokeh.layouts.layout([
        [rdo_grp, plus_btn, minus_btn],
        [figure]]), chronometer_stream


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


def sync(large, small):
    def wrapper(event):
        li = large.selected.indices[0]
        si = small.selected.indices[0]
        lx = np.asarray(large.data["x"][:])
        ly = np.asarray(large.data["y"][:])
        sx = np.asarray(small.data["x"][:])
        sy = np.asarray(small.data["y"][:])
        print('sync called', li, lx[li])
        if ((lx[li] == sx[si]) and (ly[li] == sy[si])):
            return
        pts = np.where((lx == sx[si]) & (ly == sy[si]))
        large.selected.indices = pts[0].tolist()
    return wrapper

def move(source):
    def wrapper(steps):
        if len(source.selected.indices) > 0:
            i = source.selected.indices[0]
            n = len(source.data["x"])
            source.selected.indices = [(i + steps) % n]
        return source.selected.indices
    return wrapper


def valid_time(source):
    if len(source.selected.indices) > 0:
        i = source.selected.indices[0]
        x = np.asarray(source.data["x"])
        y = np.asarray(source.data["y"])
        z = np.asarray(source.data["z"])
        pts = np.where(x == x[i])
        x = x[pts]
        y = y[pts]
        z = z[pts]
        k = [pts[0].tolist().index(i)]
        return {"x": x, "y": y, "z": z}, k
    else:
        return {"x": [], "y": [], "z": []}, []


def lead_time(source):
    if len(source.selected.indices) > 0:
        i = source.selected.indices[0]
        x = np.asarray(source.data["x"])
        y = np.asarray(source.data["y"])
        z = np.asarray(source.data["z"])
        pts = np.where(y == y[i])
        x, y, z = x[pts], y[pts], z[pts]
        k = [pts[0].tolist().index(i)]
        return {"x": x, "y": y, "z": z}, k
    else:
        return {"x": [], "y": [], "z": []}, []


def run(source):
    if len(source.selected.indices) > 0:
        i = source.selected.indices[0]
        x = np.asarray(source.data["x"])
        y = np.asarray(source.data["y"])
        z = np.asarray(source.data["z"])
        pts = np.where(z == z[i])
        x = x[pts]
        y = y[pts]
        z = z[pts]
        k = [pts[0].tolist().index(i)]
        return {"x": x, "y": y, "z": z}, k
    else:
        return {"x": [], "y": [], "z": []}, []


if __name__.startswith('bk'):
    main()
