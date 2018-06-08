#!/usr/bin/env python3
import bokeh.io
import bokeh.plotting
import bokeh.models.callbacks

def main(bokeh_id):
    """Main program"""
    figure = bokeh.plotting.figure(sizing_mode="stretch_both", match_aspect=True)

    windy_forest(figure)

    if bokeh_id == '__main__':
        bokeh.plotting.show(figure)
    else:
        bokeh.io.curdoc().add_root(figure)


def windy_forest(figure):
    left_renderer = figure.rect([1, 2, 3], [1, 2, 3], width=1, height=1,
                                color="blue")
    right_source = bokeh.models.ColumnDataSource({
        "x": [1, 2, 3],
        "y": [3, 2, 1],
        "width": [0.5, 0.5, 0.5],
        "alpha": [1, 1, 1]
    })
    right_renderer = figure.rect(x="x", y="y", width="width", height=0.5,
                                 color="red",
                                 alpha="alpha",
                                 source=right_source)
    vertical_line(figure)

    # Hide anything to the left of pointer
    callback = bokeh.models.callbacks.CustomJS(args=dict(source=right_source), code="""
        let x = source.data["x"];
        let width = source.data["width"];
        let mouse_x = cb_data.geometry.x;
        let alpha = []
        for (let i=0; i<x.length; i++) {
            if ((x[i] + (width[i] / 2)) < mouse_x) {
               alpha.push(0);
            } else {
               alpha.push(1);
            }
        }
        console.log(alpha);
        source.data.alpha = alpha;
        source.change.emit();
    """)
    hover_tool = bokeh.models.HoverTool(callback=callback)
    figure.add_tools(hover_tool)


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
