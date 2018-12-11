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

    all_hours = {}
    for d in dates:
        for h in forecast_hours:
            v = d + dt.timedelta(hours=float(h))
            if v in all_hours:
                all_hours[v].append(float(h))
            else:
                all_hours[v] = [float(h)]

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
    figure = bokeh.plotting.figure(x_axis_type='datetime',
                                   plot_height=150,
                                   plot_width=600,
                                   tools=[
                                       "tap",
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
    sources = []

    # Group by model run
    xs = []
    ys = []
    zs = []
    for date in dates:
        y = forecast_hours
        x = np.array([date + dt.timedelta(hours=float(h))
            for h in forecast_hours], dtype=object)
        z = np.array(len(forecast_hours) * [date], dtype=object)
        xs.append(x)
        ys.append(y)
        zs.append(z)
    print("By model run", len(xs))

    # Group by forecast time
    xs = []
    ys = []
    zs = []
    for hour in forecast_hours:
        y = np.array(len(dates) * [hour])
        x = dates + dt.timedelta(hours=float(hour))
        z = dates
        xs.append(x)
        ys.append(y)
        zs.append(z)
    print("By forecast hour", len(xs))

    # Group by valid date
    xs = []
    ys = []
    zs = []
    for valid_date, hours in all_hours.items():
        y = np.array(hours)
        x = np.array(len(hours) * [valid_date], dtype=object)
        z = np.array([valid_date - dt.timedelta(hours=float(h))
            for h in hours], dtype=object)
        xs.append(x)
        ys.append(y)
        zs.append(z)
    print("By valid time", len(xs))

    for x, y, z in zip(xs, ys, zs):
        source = bokeh.models.ColumnDataSource({
            "x": x,
            "y": y,
            "z": z
            })
        renderer = figure.square(x="x", y="y", size=8,
                source=source,
                line_color=None)
        renderer.selection_glyph = bokeh.models.Square(
                fill_alpha=1,
                fill_color="Red",
                line_color="Black")
        renderer.nonselection_glyph = bokeh.models.Square(
                fill_alpha=0.2,
                fill_color="grey",
                line_color=None)

        def on_change(source, div):
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
            return wrapper
        source.selected.on_change('indices', on_change(source, div))
        sources.append(source)

    widgets = [div]

    def plus(sources):
        def wrapper():
            for source in sources:
                if len(source.selected.indices) > 0:
                    i = source.selected.indices[0]
                    source.selected.indices = [i + 1]
        return wrapper

    def minus(sources):
        def wrapper():
            for source in sources:
                if len(source.selected.indices) > 0:
                    i = source.selected.indices[0]
                    source.selected.indices = [i - 1]
        return wrapper

    plus_btn = bokeh.models.Button(label="+", width=50)
    plus_btn.on_click(plus(sources))
    minus_btn = bokeh.models.Button(label="-", width=50)
    minus_btn.on_click(minus(sources))
    btns = [plus_btn, minus_btn]

    div = bokeh.models.Div(text="Navigate:")
    rdo_grp = bokeh.models.RadioGroup(labels=[
        "Time", "Forecast", "Run"], active=2, inline=True)
    def callback(attr, old, new):
        if new == 0:
            print('grouping by time')
        elif new == 1:
            print('grouping by lead time')
        elif new == 2:
            print('grouping by model run')
    rdo_grp.on_change("active", callback)

    document.add_root(bokeh.layouts.widgetbox(*widgets))
    document.add_root(bokeh.layouts.row(div, rdo_grp, plus_btn, minus_btn, width=100))
    document.add_root(figure)


if __name__.startswith('bk'):
    main()
