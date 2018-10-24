import os
import bokeh.plotting
import bokeh.themes
import numpy as np
import jinja2


script_dir = os.path.dirname(__file__)
env = jinja2.Environment(loader=jinja2.FileSystemLoader(script_dir))


def app(document):
    figure = bokeh.plotting.figure(sizing_mode="stretch_both", name="map",
                                   title="Circles")
    source = bokeh.models.ColumnDataSource(dict(
        x=[1, 2, 3],
        y=[1, 2, 3],
        size=[5, 5, 5]
    ))
    figure.circle(x="x", y="y", size="size", source=source)

    def on_click():
        size = np.asarray(source.data["size"])
        if max(size) > 20:
            size = size - 10
        else:
            size = size + 5
        source.data["size"] = size

    button = bokeh.models.Button(label="Circle size", name="btn")
    button.on_click(on_click)

    document.add_root(button)
    document.add_root(figure)

    filename = os.path.join(os.path.dirname(__file__), "theme.yaml")
    document.theme = bokeh.themes.Theme(filename=filename)

    document.template = env.get_template("templates/index.html")
