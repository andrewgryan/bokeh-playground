import numpy as np
import bokeh.plotting
import bokeh.layouts
import bokeh.models
figure = bokeh.plotting.figure()
btn = bokeh.models.Button()


def pixels(N, M):
    # image (i, j) maps to (y, x) in real space
    container = np.empty((M, N), dtype=np.uint32)
    view = container.view(dtype=np.uint8).reshape(M, N, 4)
    alpha = 255
    for i in range(M):
        if i % 2 == 0:
            red = 158
        else:
            red = 0
        for j in range(N):
            if (i*M + j) % 2 == 0:
                green = int((i / N) * 255)
                blue = int((j / M) * 255)
            else:
                green = int((j / M) * 255)
                blue = int((i / N) * 255)
            view[i, j, 0] = red
            view[i, j, 1] = green
            view[i, j, 2] = blue
            view[i, j, 3] = alpha
    return container


N, M = 1800, 900
rgba = pixels(N, M)
print("finished generating pixels: {} x {}".format(N, M))
source = bokeh.models.ColumnDataSource({
    "x": [-19],
    "y": [-13],
    "dw": [72],
    "dh": [36],
    "image": [rgba],
})
figure.image_rgba(
        x="x",
        y="y",
        dw="dw",
        dh="dh",
        image="image",
        source=source)
document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.column(figure, btn))
