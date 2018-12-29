import bokeh.plotting
figure = bokeh.plotting.figure(
        active_scroll="wheel_zoom",
        sizing_mode="stretch_both")

source = bokeh.models.ColumnDataSource(dict(
    width=[1, 0.5],
    height=[1, 1],
    x=[0, 2],
    y=[0, 0]))
figure.rect(
        width="width",
        height="height",
        x="x",
        y="y",
        fill_alpha=0.5,
        line_color="blue",
        source=source)

# Mutation texts
source = bokeh.models.ColumnDataSource(dict(
    x=[0.05],
    y=[1.5],
    text=["c.701delC"]
    ))
text = bokeh.models.Text(x="x", y="y", text="text")
figure.add_glyph(source, text)

figure.multi_line(
        xs=[[0, 0]],
        ys=[[0.55, 1.55]],
        line_color="black")

# Dashed lines
figure.multi_line(
        xs=[
            [-1, -0.5],
            [0.5, 1.75],
            ],
        ys=[
            [0, 0],
            [0, 0],
            ],
        line_color="black",
        line_dash="dashed")

# Dashed texts
source = bokeh.models.ColumnDataSource(dict(
    x=[-0.75, 1],
    y=[0, 0],
    text=["1425bp", "4675bp"]
    ))
text = bokeh.models.Text(x="x", y="y", text="text")
figure.add_glyph(source, text)

# Numbered boxes
source = bokeh.models.ColumnDataSource(dict(
    x=[0, 2],
    y=[0, 0],
    text=["1", "2"]
    ))
text = bokeh.models.Text(x="x", y="y", text="text",
        text_font_style="bold")
figure.add_glyph(source, text)

document = bokeh.plotting.curdoc()
document.add_root(figure)
