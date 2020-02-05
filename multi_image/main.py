import bokeh.plotting

index_source = bokeh.models.ColumnDataSource({
    "i": [2]
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
    "add_image": bokeh.models.Button()
}
i = 0
def on_click():
    global i
    source.stream({
        "x": [i],
        "y": [0],
        "dw": [2],
        "dh": [2],
        "image": [
            [[1, 2], [3, 4]]
        ],
    })
    i += 2
buttons["add_image"].on_click(on_click)
document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.column(
    figure,
    bokeh.layouts.row(
        buttons["add_image"]
    )
))
