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
    ni, nj = 100, 100
    values = np.arange(ni*nj).reshape(ni, nj)

    # Matplotlib domain
    quad_mesh = plt.pcolormesh(values)
    plt.savefig("quad_mesh.png")

    # Matplotlib to Bokeh
    rgba = quad_mesh.to_rgba(quad_mesh.get_array(),
                             bytes=True).reshape((ni, nj, 4))

    # Bokeh domain
    source = bokeh.models.ColumnDataSource({
        "image": [rgba]
    })
    figure.image_rgba(x=0,
                      y=0,
                      dw=nj,
                      dh=ni,
                      image="image",
                      source=source)

    if bokeh_id == '__main__':
        bokeh.plotting.show(figure)
    else:
        bokeh.io.curdoc().add_root(figure)


main(__name__)
