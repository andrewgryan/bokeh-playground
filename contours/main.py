import bokeh.plotting
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.contour
import matplotlib.colors


def contour(qcs):
    line_colors = []
    for c in qcs.collections:
        line_color = matplotlib.colors.rgb2hex(
                c.get_color()[0], keep_alpha=True)
        line_colors += len(c.get_segments()) * [line_color]
    xs = [ss[:, 0].tolist() for s in qcs.allsegs for ss in s]
    ys = [ss[:, 1].tolist() for s in qcs.allsegs for ss in s]
    return {"xs": xs,
            "ys": ys,
            "line_color": line_colors}


def clabel(txts):
    positions = np.array([t.get_position() for t in txts])
    x = positions[:, 0]
    y = positions[:, 1]
    angle = np.deg2rad([t.get_rotation() for t in txts])
    text = [t.get_text() for t in txts]
    text = [pad(t) for t in text]
    text_color = [matplotlib.colors.rgb2hex(t.get_color(), keep_alpha=True)
            for t in txts]
    return {"x": x,
            "y": y,
            "text": text,
            "angle": angle,
            "text_color": text_color}


def pad(text):
    return " {} ".format(text)


def main():
    bokeh_figure = bokeh.plotting.figure(
            sizing_mode="stretch_both")

    x = np.linspace(-10, 10, 100)
    y = np.linspace(-10, 10, 100)
    X, Y = np.meshgrid(x, y)

    multi_line_source = bokeh.models.ColumnDataSource({
        "xs": [],
        "ys": [],
        "line_color": [],
        })
    bokeh_figure.multi_line(
            xs="xs",
            ys="ys",
            line_color="line_color",
            source=multi_line_source)

    label_set_source = bokeh.models.ColumnDataSource({})
    labels = bokeh.models.LabelSet(
            x="x",
            y="y",
            text="text",
            angle="angle",
            text_color="text_color",
            text_font_size="10px",
            text_align="center",
            text_baseline="middle",
            background_fill_color="white",
            source=label_set_source)
    bokeh_figure.add_layout(labels)

    Z = np.cos(X) + np.sin(Y) + 2 * (X / X.max())
    ax = plt.gca()
    qcs = matplotlib.contour.QuadContourSet(ax, X, Y, Z)
    multi_line_source.data = contour(qcs)
    txts = qcs.clabel(inline=True)
    label_set_source.data = clabel(txts)

    for c in qcs.collections:
        ax.collections.remove(c)
    for t in qcs.labelTexts:
        ax.artists.remove(t)

    def click(X, Y, multi_line_source, label_set_source):
        def wrapped():
            Z = X**2 + Y**2
            ax = plt.gca()
            qcs = matplotlib.contour.QuadContourSet(ax, X, Y, Z)
            multi_line_source.data = contour(qcs)
            txts = qcs.clabel(inline=True)
            label_set_source.data = clabel(txts)
        return wrapped

    btn = bokeh.models.Button()
    btn.on_click(click(X, Y, multi_line_source, label_set_source))

    document = bokeh.plotting.curdoc()
    document.add_root(btn)
    document.add_root(bokeh_figure)


if __name__.startswith("bk"):
    main()
