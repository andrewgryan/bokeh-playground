"""Prototype to programmatically hide/show HoverTool"""
import bokeh.plotting
import bokeh.models
import bokeh.events
import bokeh.layouts


def main(bokeh_id):
    """Main program"""
    hover_tool = bokeh.models.HoverTool()

    figure = bokeh.plotting.figure(tools=[hover_tool])
    figure.circle(x=[1, 2, 3], y=[1, 2, 3])

    js_callback = bokeh.models.CustomJS(args=dict(hover_tool=hover_tool), code="""
        console.log("JS button clicked");
        hover_tool.active = !hover_tool.active;
    """)
    js_button = bokeh.models.Button(label="JS call back")
    js_button.js_on_event(bokeh.events.ButtonClick, js_callback)

    py_button = bokeh.models.Button(label="Python call back")
    def py_callback():
        print("Python button clicked")
        js_button.trigger("change", 0, 0)
    py_button.on_click(py_callback)

    buttons = bokeh.layouts.row(js_button, py_button)
    page = bokeh.layouts.column(buttons, figure)
    if bokeh_id == "__main__":
        bokeh.plotting.show(page)
    else:
        bokeh.io.curdoc().add_root(page)


main(__name__)
