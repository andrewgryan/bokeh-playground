"""

Demonstration of combining client-side animation with streamed
column data sources

"""
import bokeh.plotting
import numpy as np

# Animation state
animation_source = bokeh.models.ColumnDataSource({
    "i": [0],
    "playing": [False]
})

custom_js_filter = bokeh.models.CustomJSFilter(args=dict(animation_source=animation_source), code="""
    let indices = new Array(source.get_length()).fill(true);
    return indices.map((x, i) => i == animation_source.data['i'][0])
""")

source = bokeh.models.ColumnDataSource({
    "x": [],
    "y": [],
    "dw": [],
    "dh": [],
    "image": [],
})
view = bokeh.models.CDSView(source=source, filters=[custom_js_filter])
figure = bokeh.plotting.figure()
figure.image(
        x="x",
        y="y",
        dw="dw",
        dh="dh",
        image="image",
        source=source,
        view=view)
buttons = {
    "add_image": bokeh.models.Button(label="Add frame"),
    "play": bokeh.models.Button(label="Play"),
    "pause": bokeh.models.Button(label="Pause")
}

X, Y = np.meshgrid(
        np.linspace(0, 2, 256),
        np.linspace(0, 2, 256))

def particle(X, Y):
    return np.exp(-1 * (X**2 + Y**2))


def _image(index):
    """Simulates retrieving next image from server"""
    return particle((X - 0.1 * i), Y)

i = 0
def on_click():
    global i
    source.stream({
        "x": [0],
        "y": [0],
        "dw": [2],
        "dh": [2],
        "image": [_image(i)],
    })
    i += 1
buttons["add_image"].on_click(on_click)


# Button to "animate" frames
custom_js = bokeh.models.CustomJS(args=dict(
    image_source=source,
    animation_source=animation_source), code="""
        animation_source.data['playing'] = [true];
        animation_source.change.emit()
        let next_frame = function() {
            if (animation_source.data['playing'][0]) {
                let index = animation_source.data['i'][0];
                animation_source.data['i'] = [(index + 1) % image_source.get_length()]
                image_source.change.emit() // Trigger CustomJSFilter
                setTimeout(next_frame, 100)
            }
        }
        setTimeout(next_frame, 100)
""")
buttons["play"].js_on_click(custom_js)
custom_js = bokeh.models.CustomJS(args=dict(
    animation_source=animation_source), code="""
        animation_source.data['playing'] = [false];
        animation_source.change.emit()
""")
buttons["pause"].js_on_click(custom_js)

document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.column(
    bokeh.layouts.row(
        buttons["add_image"],
        buttons["play"],
        buttons["pause"]
    ),
    figure))
