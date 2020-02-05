import bokeh.plotting

index_source = bokeh.models.ColumnDataSource({
    "i": [0],
    "playing": [False]
})

custom_js_filter = bokeh.models.CustomJSFilter(args=dict(index_source=index_source), code="""
    let indices = new Array(source.get_length()).fill(true);
    return indices.map((x, i) => i == index_source.data['i'][0])
""")

source = bokeh.models.ColumnDataSource({
    "x": [],
    "y": [],
    "dw": [],
    "dh": [],
    "image": [],
})
view = bokeh.models.CDSView(source=source, filters=[
    custom_js_filter
])
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

def _image(index):
    return [
        [0 + index, 1, 2],
        [2, 3 + index, 4],
        [4, 5, 6 + index]
    ]

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
    i += 2
buttons["add_image"].on_click(on_click)


# Button to "animate" frames
custom_js = bokeh.models.CustomJS(args=dict(
    image_source=source,
    index_source=index_source), code="""
        index_source.data['playing'] = [true];
        index_source.change.emit()
        let next_frame = function() {
            console.log(index_source);
            if (index_source.data['playing'][0]) {
                let index = index_source.data['i'][0];
                index_source.data['i'] = [(index + 1) % image_source.get_length()]
                image_source.change.emit() // Trigger CustomJSFilter
                setTimeout(next_frame, 100)
            }
        }
        setTimeout(next_frame, 100)
""")
buttons["play"].js_on_click(custom_js)
custom_js = bokeh.models.CustomJS(args=dict(
    index_source=index_source), code="""
        index_source.data['playing'] = [false];
        index_source.change.emit()
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
