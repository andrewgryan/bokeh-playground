import bokeh.plotting

index_source = bokeh.models.ColumnDataSource({
    "i": [0]
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
    "next_index": bokeh.models.Button(label="Next frame")
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
        let index = index_source.data['i'][0];
        index_source.data = {
            "i": [(index + 1) % image_source.get_length()]
        }
        image_source.change.emit() // Trigger CustomJSFilter
""")
buttons["next_index"].js_on_click(custom_js)

document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.column(
    bokeh.layouts.row(
        buttons["add_image"],
        buttons["next_index"]
    ),
    figure))
