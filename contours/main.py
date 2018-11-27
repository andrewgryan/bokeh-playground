import bokeh.plotting
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.contour
import matplotlib.colors


def contour(bokeh_figure, X, Y, Z):
    ax = plt.gca()
    qcs = matplotlib.contour.QuadContourSet(ax, X, Y, Z)
    line_colors = []
    for c in qcs.collections:
        line_color = matplotlib.colors.rgb2hex(
                c.get_color()[0], keep_alpha=True)
        line_colors += len(c.get_segments()) * [line_color]
    xs = [ss[:, 0].tolist() for s in qcs.allsegs for ss in s]
    ys = [ss[:, 1].tolist() for s in qcs.allsegs for ss in s]

    # Tidy up references for garbage collector
    for c in qcs.collections:
        ax.collections.remove(c)

    bokeh_figure.multi_line(xs=xs, ys=ys, line_color=line_colors)

    def pad(text):
        return " {} ".format(text)

    qcs.clabel(inline=True)

    # Scrape data from Texts
    positions = np.array([t.get_position() for t in qcs.labelTexts])
    x = positions[:, 0]
    y = positions[:, 1]
    angle = np.deg2rad([t.get_rotation() for t in qcs.labelTexts])
    text = [t.get_text() for t in qcs.labelTexts]
    text = [pad(t) for t in text]
    text_color = [matplotlib.colors.rgb2hex(t.get_color(), keep_alpha=True)
            for t in qcs.labelTexts]
    source = bokeh.models.ColumnDataSource(dict(
            x=x,
            y=y,
            text=text,
            angle=angle,
            text_color=text_color))
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
            source=source)
    bokeh_figure.add_layout(labels)


def main():
    figure = bokeh.plotting.figure(
            sizing_mode="stretch_both")

    x = np.linspace(-10, 10, 100)
    y = np.linspace(-10, 10, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.cos(X) + np.sin(Y) + 2 * (X / X.max())

    contour(figure, X, Y, Z)

    document = bokeh.plotting.curdoc()
    document.add_root(figure)


if __name__.startswith("bk"):
    main()
