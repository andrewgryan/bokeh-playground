import datetime as dt
import bokeh.plotting
import pandas as pd
import numpy as np

x = pd.date_range("20190101", "20190106", freq="1H")
y = np.zeros(len(x))

source = bokeh.models.ColumnDataSource(dict(
    x=x,
    y=y,
))
figure = bokeh.plotting.figure(
    plot_height=120,
    tools='xpan',
    x_axis_type='datetime')
figure.toolbar.active_drag = 'auto'

active_scroll = bokeh.models.WheelZoomTool(dimensions='width')
figure.add_tools(active_scroll)
figure.toolbar.active_scroll = active_scroll

renderer = figure.square(x="x", y="y", source=source,
              fill_color='black',
              line_color='black')
renderer.selection_glyph = bokeh.models.Square(
    fill_color="red",
    line_color="red")
renderer.nonselection_glyph = bokeh.models.Square(
    fill_color="black",
    line_color="black",
    fill_alpha=0.2,
    line_alpha=0.2,
)

# X-axis formatter breakpoints
formatter = figure.xaxis[0].formatter
formatter.hourmin = ['%H:%M']
formatter.hours = ['%H:%M']
formatter.days = ["%d %B"]
formatter.months = ["%b %Y"]

# Customize figure to be a time slider widget
figure.grid.grid_line_color = None
figure.yaxis.visible = False
figure.toolbar_location = None
# figure.toolbar.autohide = True
# figure.outline_line_color = None
figure.xaxis.fixed_location = 0
figure.title.text = "Select time"

# Tooltip
# hover_tool = bokeh.models.HoverTool(
#     tooltips=[
#         ("Date", "@x{%Y-%m-%d}"),
#         ("Day", "@x{%A}"),
#         ("Time", "@x{%I:%M %p}"),
#     ],
#     formatters={
#         "x": "datetime"
#     },
#     mode='vline',
#     point_policy='follow_mouse'
# )
hover_tool = bokeh.models.HoverTool(
    tooltips=None
)
figure.add_tools(hover_tool)

selected_span = bokeh.models.Span(
    dimension="height",
    line_color="red",
    location=0)
figure.add_layout(selected_span)

# Wire up Tap event
tap_js = bokeh.models.CustomJS(args=dict(
    span=selected_span,
    source=source), code="""
    let x = source.data['x'];
    let distance = x.map((t) => Math.abs(t - cb_obj.x));
    let minIndex = distance.reduce(function(bestIndex, value, index, values) {
        if (value < values[bestIndex]) {
            return index;
        } else {
            return bestIndex;
        }
    }, 0);
    source.selected.indices = [minIndex];
    span.location = x[minIndex];
    source.change.emit();
""")
figure.js_on_event(bokeh.events.Tap, tap_js)

# Span that follows cursor
span = bokeh.models.Span(
    dimension="height",
    line_color="grey",
    location=source.data["x"][0])
js = bokeh.models.CustomJS(args=dict(span=span), code="""
    span.location = cb_data.geometry.x;
""")
figure.add_layout(span)
hover_tool.callback = js

def on_selected(attr, old, new):
    if len(new) > 0:
        i = new[0]
        date = source.data["x"][i]
        figure.title.text = f"{date:%A %d %B %Y %H:%M}"
source.selected.on_change('indices', on_selected)

# Band to highlight valid times
dates = source.data["x"]
band_source = bokeh.models.ColumnDataSource(dict(
    base=[-1, 1],
    upper=[max(dates), max(dates)],
    lower=[min(dates), min(dates)]
))
band = bokeh.models.Band(
    dimension='width',
    base='base',
    lower='lower',
    upper='upper',
    fill_color='grey',
    fill_alpha=0.2,
    source=band_source
)
figure.add_layout(band)

bokeh.plotting.curdoc().add_root(
    bokeh.layouts.row(
        figure,
    ))
