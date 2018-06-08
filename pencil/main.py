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
    right_renderer = figure.rect([1, 2, 3], [3, 2, 1], width=0.5, height=0.5,
                                 color="red",
                                 hover_alpha=0.)
    span = bokeh.models.Span(location=0, dimension='height', line_color='black', line_width=1)
    figure.renderers.append(span)

    callback = bokeh.models.callbacks.CustomJS(args=dict(span=span), code="""
        span.location = cb_data.geometry.x;
    """)
    hover_tool = bokeh.models.HoverTool(callback=callback,
                                        mode="vline")
    figure.add_tools(hover_tool)


main(__name__)
