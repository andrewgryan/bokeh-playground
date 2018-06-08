#!/usr/bin/env python3
import numpy as np
import bokeh.io
import bokeh.plotting
import bokeh.models.callbacks
import imageio


def main(bokeh_id):
    """Main program"""
    figure = bokeh.plotting.figure(sizing_mode="stretch_both", match_aspect=True)

    windy_images(figure)

    if bokeh_id == '__main__':
        bokeh.plotting.show(figure)
    else:
        bokeh.io.curdoc().add_root(figure)

def windy_images(figure):
    # Left image
    forest_rgba = imageio.imread("forest.png")[::-1, :, :]
    ni, nj, _ = forest_rgba.shape
    shape = (ni, nj)
    source = bokeh.models.ColumnDataSource({
            "image": [forest_rgba],
            "original_alpha": [np.copy(forest_rgba[:, :, -1])]
    })
    left = figure.image_rgba(image="image",
                             x=0,
                             y=0,
                             dw=10,
                             dh=10,
                             source=source)
    hover_tool = hover_tool_image_hide(source, shape, mode="show_right")
    figure.add_tools(hover_tool)

    # Right image
    wind_rgba = imageio.imread("wind.png")[::-1, :, :]
    ni, nj, _ = wind_rgba.shape
    shape = (ni, nj)
    source = bokeh.models.ColumnDataSource({
            "image": [wind_rgba],
            "original_alpha": [np.copy(wind_rgba[:, :, -1])]
    })
    right = figure.image_rgba(image="image",
                              x=0,
                              y=0,
                              dw=10,
                              dh=10,
                              source=source)
    hover_tool = hover_tool_image_hide(source, shape, mode="show_left")
    figure.add_tools(hover_tool)

    # VLine
    vertical_line(figure)

def hover_tool_image_hide(source, shape, mode="hide_right"):
    """Hide anything to the left/right of pointer

    At the moment this is achieved through the use of CustomJS and
    alpha values. A more complete solution would work on the canvas
    itself
    """
    code_template = """
        // Previous mouse position
        console.log('previous mouse-x:', shared_mouse.data.x[0]);

        // Hard-coded values for now
        let x = 0;
        let dw = 10;

        // ColumnDataSource values
        let ni = shape[0];
        let nj = shape[1];
        let original_alpha = source.data.original_alpha[0];

        // Mouse position(s)
        let left_x;
        let right_x;
        let mouse_x = cb_data.geometry.x;
        let previous_mouse_x = shared_mouse.data.x[0];

        // Update alpha pseudo-2D and RGBA pseudo-3D arrays
        let pixel_x;
        let alpha;
        let alpha_index;
        let image_alpha_index;
        let dy = dw / nj;
        for (let j=0; j<nj; j++) {
            pixel_x = x + (j * dy);

            // Optimised selection of columns between mouse events
            if (mouse_x > previous_mouse_x) {
                left_x = previous_mouse_x;
                right_x = mouse_x;
            } else {
                left_x = mouse_x;
                right_x = previous_mouse_x;
            }
            if ((pixel_x > right_x) || (pixel_x < left_x)) {
                // pixel outside current and previous mouse positions
                continue;
            }

            // Ordinary loop logic
            for (let i=0; i<ni; i++) {
                alpha_index = (nj * i) + j;
                original_alpha_value = original_alpha[alpha_index];
                if (original_alpha_value == 0) {
                    continue;
                }
                image_alpha_index = (4 * alpha_index) + 3;
                if (%s) {
                   alpha = original_alpha_value;
                } else {
                   alpha = 0;
                }
               source.data["image"][0][image_alpha_index] = alpha;
            }
        }
        source.change.emit();

        // Update mouse position
        shared_mouse.data.x[0] = mouse_x;
    """
    if mode == "show_left":
        show_logic = "pixel_x < mouse_x"
    else:
        show_logic = "pixel_x > mouse_x"
    code = code_template % show_logic
    shared_mouse = bokeh.models.ColumnDataSource(dict(x=[0]))
    callback = bokeh.models.callbacks.CustomJS(args=dict(source=source,
                                                         shape=shape,
                                                         shared_mouse=shared_mouse),
                                               code=code)
    return bokeh.models.HoverTool(callback=callback)

def windy_forest(figure):
    left_source = bokeh.models.ColumnDataSource({
        "x": [1, 2, 3],
        "y": [1, 2, 3],
        "width": [1, 1, 1],
        "alpha": [1, 1, 1]
    })
    left_renderer = figure.rect(x="x",
                                y="y",
                                width="width",
                                height=1,
                                color="blue",
                                alpha="alpha",
                                source=left_source)
    hover_tool = hover_tool_hide(left_source, side="right")
    figure.add_tools(hover_tool)
    right_source = bokeh.models.ColumnDataSource({
        "x": [1, 2, 3],
        "y": [3, 2, 1],
        "width": [0.5, 0.5, 0.5],
        "alpha": [1, 1, 1]
    })
    right_renderer = figure.rect(x="x",
                                 y="y",
                                 width="width",
                                 height=0.5,
                                 color="red",
                                 alpha="alpha",
                                 source=right_source)
    hover_tool = hover_tool_hide(right_source, side="left")
    figure.add_tools(hover_tool)
    vertical_line(figure)

def hover_tool_hide(source, side="left"):
    """Hide anything to the left/right of pointer

    At the moment this is achieved through the use of CustomJS and
    alpha values. A more complete solution would work on the canvas
    itself
    """
    code_template = """
        let x_left, x_right;
        let x = source.data["x"];
        let width = source.data["width"];
        let mouse_x = cb_data.geometry.x;
        let alpha = [];
        for (let i=0; i<x.length; i++) {
            x_left = x[i] - (width[i] / 2);
            x_right = x[i] + (width[i] / 2);
            if (%s) {
               alpha.push(0);
            } else {
               alpha.push(1);
            }
        }
        source.data.alpha = alpha;
        source.change.emit();
    """
    if side.lower() == "left":
        code = code_template % "mouse_x < x_right"
    else:
        code = code_template % "mouse_x > x_left"
    callback = bokeh.models.callbacks.CustomJS(args=dict(source=source),
                                               code=code)
    return bokeh.models.HoverTool(callback=callback)


def vertical_line(figure):
    """Add vertical Span that follows mouse pointer"""
    span = bokeh.models.Span(location=0, dimension='height', line_color='black', line_width=1)
    figure.renderers.append(span)
    callback = bokeh.models.callbacks.CustomJS(args=dict(span=span), code="""
        span.location = cb_data.geometry.x;
    """)
    hover_tool = bokeh.models.HoverTool(callback=callback)
    figure.add_tools(hover_tool)


main(__name__)
