import bokeh.plotting
import bokeh.models

figure = bokeh.plotting.figure()
glyph = bokeh.models.Patches(xs="xs", ys="ys")
source = bokeh.models.ColumnDataSource({
    "xs": [[0, 0.1, 0.1, 0], [0.3, 0.4, 0.4, 0.3]],
    "ys": [[0, 0, 0.1, 0.1], [0.3, 0.3, 0.4, 0.4]],
})
figure.add_glyph(source, glyph)
document = bokeh.plotting.curdoc()
document.add_root(figure)
