#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
import bokeh.io
import bokeh.plotting
import bokeh.models.callbacks
import imageio


def main(bokeh_id):
    """Main program"""
    figure = bokeh.plotting.figure(sizing_mode="stretch_both", match_aspect=True)

    # Numpy/iris.Cube domain
    values = np.arange(100).reshape(4, 25)

    # Matplotlib domain
    quad_mesh = plt.pcolormesh(values)

    # Matplotlib to Bokeh
    rgba = quad_mesh.to_rgba(quad_mesh.get_array(),
                             bytes=True)

    # Bokeh domain
    # values = np.zeros((4, 25), np.uint32)
    # values = values.view(dtype=np.uint8).reshape((4, 25, 4))
    # ni, nj = 4, 25
    # for i in range(ni):
    #     for j in range(nj):
    #         r = (ni * j) + i
    #         print(rgba[r])
    #         values[i, j, :] = 255 * rgba[r]
    values = rgba.reshape((4, 25, 4), order='F')
    source = bokeh.models.ColumnDataSource({
        "image": [values]
    })
    figure.image_rgba(x=0,
                      y=0,
                      dw=1,
                      dh=1,
                      image="image",
                      source=source)

    if bokeh_id == '__main__':
        bokeh.plotting.show(figure)
    else:
        bokeh.io.curdoc().add_root(figure)


main(__name__)
