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
    forecast_hours = np.array([3 * i for i in range(12)])

    document = bokeh.plotting.curdoc()
    hover_tool = bokeh.models.HoverTool(
            tooltips=[
                ('valid', '@x{%F %T}'),
                ('start', '@z{%F %T}'),
                ('length', 'T+@y')
                ],
            formatters={
                'x': 'datetime',
                'z': 'datetime'
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
    figure.xaxis.axis_label_text_font_size = "8px"
    figure.yaxis.axis_label = "Forecast length"
    figure.yaxis.axis_label_text_font_size = "8px"
    figure.yaxis.ticker = [0, 12, 24, 48]

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

    source = bokeh.models.ColumnDataSource({
        "x": x,
        "y": y,
        "z": z
        })
    renderer = figure.square(x="x", y="y", size=8,
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

    def on_change(source, div):
        def wrapper(attr, old, new):
            if len(new) > 0:
                i = new[0]
                x, y, z = (
                        source.data["x"][i],
                        source.data["y"][i],
                        source.data["z"][i])
                if not isinstance(x, dt.datetime):
                    x = dt.datetime.fromtimestamp(x / 1000.)
                if not isinstance(z, dt.datetime):
                    z = dt.datetime.fromtimestamp(z / 1000.)
                template = "<p>Valid date: {}</br>Start date: {}</br>Offset: {}</p>"
                msg = template.format(x, z, "T+{}".format(str(y)))
                div.text = msg
        return wrapper
    source.selected.on_change('indices', on_change(source, div))

    selected = rx.Stream()
    source.selected.on_change('indices', rx.callback(selected))

    widgets = [div]

    plus_btn = bokeh.models.Button(label="+", width=50)
    minus_btn = bokeh.models.Button(label="-", width=50)

    plus = rx.Stream()
    plus_btn.on_click(rx.click(plus))
    plus = plus.map(+1)

    minus = rx.Stream()
    minus_btn.on_click(rx.click(minus))
    minus = minus.map(-1)

    steps = rx.Merge(plus, minus).log()

    rdo_grp = bokeh.models.RadioGroup(labels=[
        "Time", "Forecast", "Run"],
        inline=True,
        width=210)

    def update(source):
        def wrapper(event):
            data, indices = event
            source.data = data
            source.selected.indices = indices
            return event
        return wrapper

    def all_not_none(items):
        return all(item is not None for item in items)

    stream = rx.Stream()
    rdo_grp.on_change("active", rx.callback(stream))
    method_stream = rx.Merge(
            stream.filter(lambda i: i == 0).map(lambda i: valid_time),
            stream.filter(lambda i: i == 1).map(lambda i: lead_time),
            stream.filter(lambda i: i == 2).map(lambda i: run))
    data_stream = (method_stream
            .map(lambda method: method(source))
            .map(update(second_source))
            .log())
    states = rx.combine_latest(
            method_stream,
            selected).filter(all_not_none).log()

    rdo_grp.active = 1
    source.selected.indices = [0]

    document.add_root(bokeh.layouts.widgetbox(*widgets))
    document.add_root(bokeh.layouts.layout([
        [rdo_grp, plus_btn, minus_btn],
        [figure]]))


def plus(source):
    def wrapper():
        if len(source.selected.indices) > 0:
            i = source.selected.indices[0]
            n = len(source.data["x"])
            source.selected.indices = [(i + 1) % n]
    return wrapper


def minus(source):
    def wrapper():
        if len(source.selected.indices) > 0:
            i = source.selected.indices[0]
            n = len(source.data["x"])
            source.selected.indices = [(i - 1) % n]
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
        x = x[pts]
        y = y[pts]
        z = z[pts]
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
