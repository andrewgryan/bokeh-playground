import os
import bokeh.plotting
import bokeh.themes


def app(document):
    figure = bokeh.plotting.figure(sizing_mode="stretch_both")
    figure.circle([1, 2, 3], [1, 2, 3])

    document.add_root(figure)

    filename = os.path.join(os.path.dirname(__file__), "theme.yaml")
    document.theme = bokeh.themes.Theme(filename=filename)
