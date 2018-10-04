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
        self.figure.x_range.bounds = 'auto'

fixed_limit = FixedLimit(figure, 0.5, 3.5)

button = bokeh.models.Button(label="Fix limits")
button.on_click(fixed_limit.on_click)
button.js_on_click(fixed_limit.js_on_click)

fixed_limit.start = 0.1
fixed_limit.end = 3.1

document.add_root(button)
document.add_root(figure)
