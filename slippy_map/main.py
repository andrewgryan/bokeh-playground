import numpy as np
import bokeh.plotting


def perimeter(x, y, dw, dh):
    return ([x, x + dw, x + dw, x, x],
            [y, y, y + dh, y + dh, y])


def pixels(N):
    img = np.empty((N, N), dtype=np.uint32)
    view = img.view(dtype=np.uint8).reshape(N, N, 4)
    for i in range(N):
        for j in range(N):
            view[i, j, 0] = int((i / N) * 255)
            view[i, j, 1] = 158
            view[i, j, 2] = int((j / N) * 255)
            view[i, j, 3] = 255
    return img

figure = bokeh.plotting.figure(sizing_mode="stretch_both")
figure.image_rgba(
    x=0,
    y=0,
    dw=1,
    dh=1,
    image=[pixels(128)]
)
x, y = perimeter(0.5, 0.4, 0.25, 0.6)
figure.line(x, y)
document = bokeh.plotting.curdoc()
document.add_root(figure)
