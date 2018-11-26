import bokeh.plotting
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.contour


def rgba2hex(rgba):
    assert len(rgba) == 4, "can only process RGBA values"
    values = np.floor(rgba * 255).astype(np.int)
    return "#{:02x}{:02x}{:02x}{:02x}".format(*values)


figure = bokeh.plotting.figure(
        sizing_mode="stretch_both")

x = np.linspace(-10, 10, 100)
y = np.linspace(-10, 10, 100)
X, Y = np.meshgrid(x, y)
Z = np.cos(X) + np.sin(Y)

ax = plt.gca()
qcs = matplotlib.contour.QuadContourSet(ax, X, Y, Z)
xs = [ss[:, 0].tolist() for s in qcs.allsegs for ss in s]
ys = [ss[:, 1].tolist() for s in qcs.allsegs for ss in s]
for c in qcs.collections:
    ax.collections.remove(c)

figure.multi_line(xs=xs, ys=ys)

# Add text annotations
qcs.clabel(inline=True)
xl, yl = [], []
for t in qcs.labelTexts:
    x, y = t.get_position()
    xl.append(x)
    yl.append(y)
angles = np.deg2rad([t.get_rotation() for t in qcs.labelTexts])
texts = [t.get_text() for t in qcs.labelTexts]
colors = [rgba2hex(c.get_color()[0]) for c in qcs.collections]
source = bokeh.models.ColumnDataSource(dict(
        x=xl,
        y=yl,
        text=texts,
        angle=angles,
        text_color=colors))
print(angles, texts)
labels = bokeh.models.LabelSet(
        x="x",
        y="y",
        text="text",
        angle="angle",
        text_color="text_color",
        text_font_size="9px",
        text_align="center",
        text_baseline="middle",
        background_fill_color="white",
        source=source)
figure.add_layout(labels)

document = bokeh.plotting.curdoc()
document.add_root(figure)
