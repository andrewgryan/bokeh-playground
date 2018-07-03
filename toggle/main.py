"""Prototype to play with HTML bokeh elements"""
import bokeh.plotting
import bokeh.models
import bokeh.layouts
def main(bokeh_id):
    figure = bokeh.plotting.figure(sizing_mode="stretch_both", match_aspect=True)
    figure.circle(x=[1, 2, 3], y=[1, 2, 3])

    class Toggle(object):
        def __init__(self, labels):
            self.labels = labels
            self.methods = {
                0: self.left,
                1: self.right
            }

        def left(self):
            print("left method called")

        def right(self):
            print("right method called")

        def callback(self, attr, old, new):
            self.methods[new]()

    toggle = Toggle(["left", "right"])
    button_group = bokeh.models.widgets.RadioButtonGroup(labels=toggle.labels,
                                                         active=0)
    button_group.on_change("active", toggle.callback)
    page = bokeh.layouts.column(figure, button_group)
    if bokeh_id == "__main__":
        bokeh.plotting.show(page)
    else:
        bokeh.io.curdoc().add_root(page)


main(__name__)
