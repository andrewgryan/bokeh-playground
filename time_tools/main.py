import bokeh.plotting
import bokeh.models
import datetime as dt

# Figure to illustrate time/forecast length
x = [dt.datetime(2018, 1, 1 + i) for i in range(4)]
source = bokeh.models.ColumnDataSource({
    "x": x,
    "y": [0, 0, 0, 0],
    "width": 4*[dt.timedelta(hours=3)],
    "height": [0.1, 0.1, 0.1, 0.1],
    "color": ["red", "grey", "grey", "grey"]
})
hover_tool = bokeh.models.HoverTool()
figure = bokeh.plotting.figure(x_axis_type='datetime',
                               plot_height=50,
                               tools=[hover_tool],
                               toolbar_location=None)
figure.toolbar.active_inspect = hover_tool
figure.yaxis.visible = False
figure.ygrid.grid_line_color = None
figure.rect(x="x",
            y="y",
            width="width",
            height="height",
            fill_color="color",
            line_color=None,
            source=source)
figure.y_range.start = -0.5
figure.y_range.end = +0.5

# Add a Tap event handler
def callback(event):
    div.text = "Tapped, world!"
    print(event.x, event.y)
figure.on_event(bokeh.events.Tap, callback)

# Minimal Button click example
div = bokeh.models.Div(text="Hello, world!")
def update_div():
    div.text = "Goodbye, world!"
    source.data["color"] = ["grey", "red", "grey", "grey"]
button = bokeh.models.Button()
button.on_click(update_div)

document = bokeh.plotting.curdoc()
document.add_root(figure)
document.add_root(div)
document.add_root(button)

