import numpy as np
import datetime as dt
import bokeh.plotting
import bokeh.models
import bokeh.events


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

    def on_change(source, div, second_source):
        def wrapper(attr, old, new):
            if len(new) > 0:
                i = new[0]
                x, y, z = (
                        source.data["x"][i],
                        source.data["y"][i],
                        source.data["z"][i])
                msg = "<p>Valid date: {}</p><p>Start date: {}</p><p>Offset: {}</p>".format(
                        dt.datetime.fromtimestamp(x / 1000.),
                        dt.datetime.fromtimestamp(z / 1000.),
                      "T+{}".format(str(y)))
                div.text = msg

                # Highlight glyphs to be iterated over
                dimension = "forecast"
                if dimension == "time":
                    pts = np.where(np.array(source.data["x"]) == x)
                elif dimension == "forecast":
                    pts = np.where(np.array(source.data["y"]) == y)
                elif dimension == "run":
                    pts = np.where(np.array(source.data["z"]) == z)
                pts = pts[0].tolist()
                x = [source.data["x"][k] for k in pts]
                y = [source.data["y"][k] for k in pts]
                z = [source.data["z"][k] for k in pts]
                second_source.data = {
                        "x": x,
                        "y": y,
                        "z": z}
                second_source.selected.indices = [pts.index(i)]
            else:
                second_source.data = {
                        "x": [],
                        "y": [],
                        "z": []}
                second_source.selected.indices = []
        return wrapper
    source.selected.on_change('indices', on_change(source, div, second_source))

    widgets = [div]

    plus_btn = bokeh.models.Button(label="+", width=50)
    plus_btn.on_click(plus(second_source))
    minus_btn = bokeh.models.Button(label="-", width=50)
    minus_btn.on_click(minus(second_source))
    btns = [plus_btn, minus_btn]

    rdo_grp = bokeh.models.RadioGroup(labels=[
        "Time", "Forecast", "Run"], active=2,
        inline=True,
        width=210)
    def callback(attr, old, new):
        if new == 0:
            print('grouping by time')
        elif new == 1:
            print('grouping by lead time')
        elif new == 2:
            print('grouping by model run')
    rdo_grp.on_change("active", callback)

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


if __name__.startswith('bk'):
    main()
