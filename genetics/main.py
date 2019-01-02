import bokeh.plotting
import numpy as np


def main():
    figure = bokeh.plotting.figure(
            active_scroll="wheel_zoom",
            sizing_mode="stretch_both",
            match_aspect=True)

    # Box positions/widths
    width = np.array([0.1, 3, 0.5, 0.5, 0.25, 0.25, 0.5])
    labels = ["1425bp", "4675bp", "4331bp", "1178bp", "95bp", "17624bp"]
    x = box_x(width)
    y = np.zeros(len(x))

    # Boxes
    source = bokeh.models.ColumnDataSource(dict(
        width=width,
        height=np.ones(len(width)),
        x=x,
        y=y))
    figure.rect(
            width="width",
            height="height",
            x="x",
            y="y",
            fill_alpha=0.5,
            line_color="blue",
            source=source)
    source = bokeh.models.ColumnDataSource(dict(
        x=x,
        y=y,
        text=[str(i + 1) for i in range(len(x))]
        ))
    text = bokeh.models.Text(
            x="x",
            y="y",
            text="text",
            text_font_style="bold",
            text_align="center",
            text_baseline="middle")
    figure.add_glyph(source, text)

    # Dashed lines
    xs, ys = [], []
    for i in range(len(x) - 1):
        x1, x2 = x[i], x[i + 1]
        w1, w2 = width[i], width[i + 1]
        xs.append([x1 + (w1 / 2),  x2 - (w2 / 2)])
        ys.append([0, 0])
    figure.multi_line(
            xs=xs,
            ys=ys,
            line_color="black",
            line_dash="dashed")
    source = bokeh.models.ColumnDataSource(dict(
        x=np.mean(xs, axis=1),
        y=np.mean(ys, axis=1),
        text=labels
        ))
    text = bokeh.models.Text(x="x", y="y",
            text="text",
            text_align="center",
            text_baseline="middle")
    figure.add_glyph(source, text)

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

    # Second diagram
    yc = -3
    x = [4.5, 9, 11]
    y = np.full(len(x), yc)
    source = bokeh.models.ColumnDataSource(dict(
        width=[12],
        height=[1],
        x=[6],
        y=[yc]))
    figure.rect(
            width="width",
            height="height",
            x="x",
            y="y",
            fill_alpha=0.,
            line_color="black",
            source=source)
    figure.rect(
            width=[5, 1.5, 1.5],
            height=[1, 1, 1],
            x=x,
            y=y,
            fill_color=["blue", "red", "red"],
            fill_alpha=0.5,
            line_color="black")
    source = bokeh.models.ColumnDataSource(dict(
        x=x,
        y=y,
        text=["Lorem ipsum", "dolor", "est"]
        ))
    text = bokeh.models.Text(x="x", y="y",
            text="text",
            text_align="center",
            text_baseline="middle")
    figure.add_glyph(source, text)

    document = bokeh.plotting.curdoc()
    document.add_root(figure)


def box_x(widths):
    if len(widths) == 0:
        return []
    position = widths[0] / 2
    gap = 1
    x = [position]
    for w1, w2 in zip(widths[:-1], widths[1:]):
        position += (w1 / 2) + gap + (w2 / 2)
        x.append(position)
    return x


if __name__.startswith('bk'):
    main()
