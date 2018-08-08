"""Prototype to play with HTML bokeh elements"""
import bokeh.plotting
import bokeh.models
import bokeh.layouts
import time


def main(bokeh_id):
    figure = bokeh.plotting.figure(sizing_mode="stretch_both", match_aspect=True)
    figure.circle(x=[1, 2, 3], y=[1, 2, 3])

    def callback_one():
        print("one started")
        figure.circle(x=[1, 2, 3], y=[4, 5, 6], color="orange")
        time.sleep(10)
        print("one finished")

    def callback_two():
        print("two started")
        figure.circle(x=[1, 2, 3], y=[6, 7, 8], color="purple")
        print("two finished")

    button = bokeh.models.widgets.Button()
    button.on_click(callback_one)
    button.on_click(callback_two)


    document = bokeh.layouts.column(figure, button)
    if bokeh_id == "__main__":
        bokeh.plotting.show(document)
    else:
        bokeh.io.curdoc().add_root(document)


main(__name__)
