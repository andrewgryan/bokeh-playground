#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
import bokeh.io
import bokeh.plotting


def main(bokeh_id):
    """Main program"""
    figure = bokeh.plotting.figure(sizing_mode="stretch_both",
                                   match_aspect=True)

    # Add x-ticks above plot
    figure.extra_x_ranges['above'] = figure.x_range
    axis = bokeh.models.LinearAxis(x_range_name='above')
    axis.major_label_text_font_size = '0pt'
    figure.add_layout(axis, 'above')

    # Add y-ticks to right of plot
    figure.extra_y_ranges['right'] = figure.y_range
    axis = bokeh.models.LinearAxis(y_range_name='right')
    axis.major_label_text_font_size = '0pt'
    figure.add_layout(axis, 'right')

    # Numpy/iris.Cube domain
    ni, nj = 1000, 1000
    values = np.arange(ni*nj).reshape(ni, nj)

    # Matplotlib domain
    quad_mesh = plt.pcolormesh(values)

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

