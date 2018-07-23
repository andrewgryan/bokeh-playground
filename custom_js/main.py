"""Prototype to play with HTML bokeh elements"""
import bokeh.plotting
import bokeh.models
import bokeh.layouts


def main(bokeh_id):
    figure = bokeh.plotting.figure(sizing_mode="stretch_both",
                                   match_aspect=True)
    figure.circle([1, 2, 3], [1, 2, 3])

    custom_js = bokeh.models.CustomJS(args=dict(greeting="Hello", name="Andy"),
                                      code="console.log(greeting + ', ' + name + '!');")
    button = bokeh.models.Button(label="Button")
    button.js_on_event(bokeh.events.ButtonClick, custom_js)

    def custom_py():
        print("server-side button click")
        custom_js.args["name"] = "Bob"
    button.on_click(custom_py)

    # Make a bokeh document and serve it
    page = bokeh.layouts.column(button, figure)
    if bokeh_id == "__main__":
        bokeh.plotting.show(page)
    else:
        bokeh.io.curdoc().add_root(page)

main(__name__)
