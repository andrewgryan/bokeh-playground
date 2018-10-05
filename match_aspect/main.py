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

js_callback = bokeh.models.CustomJS(code="""
    console.log('callback');
""")
figure.x_range.callback = js_callback

def on_click():
    source.data = {
        "x": [1, 2, 3, 20],
        "y": [2, 4, 6, 20]
    }
button = bokeh.models.Button()
button.on_click(on_click)
document.add_root(button)

# Work-around to simulate rigid limits
class FixedLimit(object):
    def __init__(self, figure, start, end):
        self.figure = figure
        self._start = start
        self._end = end
        self.js_on_click = bokeh.models.CustomJS(args=dict(figure=figure,
                                                           start=start,
                                                           end=end), code="""
                figure.x_range._initial_start = start;
                figure.x_range._initial_end = end;
        """)

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self.js_on_click.args["start"] = value
        self._start = value

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        self.js_on_click.args["end"] = value
        self._end = value

    def on_click(self):
        self.figure.x_range.start = self.start
        self.figure.x_range.end = self.end
        if self.start is None and self.end is None:
            bounds = None
        else:
            bounds = 'auto'
        self.figure.x_range.bounds = bounds

fixed_limit = FixedLimit(figure, None, None)

button = bokeh.models.Button(label="Fix limits")
button.on_click(fixed_limit.on_click)
button.js_on_click(fixed_limit.js_on_click)

document.add_root(button)
document.add_root(figure)
