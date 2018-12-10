import numpy as np
import datetime as dt
import bokeh.plotting
import bokeh.models
import bokeh.events


dates = np.array([
    dt.datetime(2018, 11, 30),
    dt.datetime(2018, 11, 30, 12),
    dt.datetime(2018, 12, 3, 12),
    dt.datetime(2018, 12, 5, 12),
    dt.datetime(2018, 12, 6, 0),
], dtype=object)

document = bokeh.plotting.curdoc()
hover_tool = bokeh.models.HoverTool(
        tooltips=[
            ('valid', '@x{%F %T}'),
            ('start', '@s{%F %T}'),
            ('length', 'T+@y')
            ],
        formatters={
            'x': 'datetime',
            's': 'datetime'
            })
pan_tool = bokeh.models.PanTool(dimensions="width")
figure = bokeh.plotting.figure(x_axis_type='datetime',
                               plot_height=100,
                               plot_width=600,
                               tools=[
                                   "tap",
                                   hover_tool,
                                   pan_tool],
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
for d in dates:
    y = np.array([3 * i for i in range(12)])
    x = np.array([d + dt.timedelta(hours=float(h))
        for h in y], dtype=object)
    s = np.array([d for h in y], dtype=object)
    source = bokeh.models.ColumnDataSource({
        "x": x,
        "y": y,
        "s": s
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
                x, y, s = (
                        source.data["x"][i],
                        source.data["y"][i],
                        source.data["s"][i])
                msg = "<p>Valid date: {}</p><p>Start date: {}</p><p>Offset: {}</p>".format(
                        dt.datetime.fromtimestamp(x / 1000.),
                        dt.datetime.fromtimestamp(s / 1000.),
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
    print(attr, old, new)
rdo_grp.on_change("active", callback)

document.add_root(bokeh.layouts.widgetbox(*widgets))
document.add_root(bokeh.layouts.row(div, rdo_grp, plus_btn, minus_btn, width=100))
document.add_root(figure)
