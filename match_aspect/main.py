import bokeh.plotting
import bokeh.events

document = bokeh.plotting.curdoc()
source = bokeh.models.ColumnDataSource({
    "x": [1, 2, 3],
    "y": [2, 4, 6]
})
figure = bokeh.plotting.figure(match_aspect=True,
                               aspect_scale=1)
figure.circle(x="x", y="y", source=source)

def on_click():
    source.data = {
        "x": [1, 2, 3, 20],
        "y": [2, 4, 6, 20]
    }
button = bokeh.models.Button()
button.on_click(on_click)
document.add_root(button)

# Work-around to simulate rigid limits
start = 0.9
end = 3.1
def on_click():
    figure.x_range.start = start
    figure.x_range.end = end
    figure.x_range.bounds = 'auto'
button = bokeh.models.Button(label="Fix limits")
button.on_click(on_click)
js_fix_limits = bokeh.models.CustomJS(args=dict(figure=figure,
                                                _initial_start=start,
                                                _initial_end=end), code="""
        figure.x_range._initial_start = _initial_start;
        figure.x_range._initial_end = _initial_end;
""")
button.js_on_click(js_fix_limits)

document.add_root(button)
document.add_root(figure)
