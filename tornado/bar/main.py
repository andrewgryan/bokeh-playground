import os
import bokeh.plotting
import bokeh.themes
import jinja2


script_dir = os.path.dirname(__file__)
env = jinja2.Environment(loader=jinja2.FileSystemLoader(script_dir))


def app(document):
    figure = bokeh.plotting.figure(sizing_mode="stretch_both")
    figure.circle([1, 2, 3], [1, 2, 3])

    def on_click():
        print("clicked")
    button = bokeh.models.Button()
    button.on_click(on_click)

    document.add_root(button)
    document.add_root(figure)

    filename = os.path.join(os.path.dirname(__file__), "theme.yaml")
    document.theme = bokeh.themes.Theme(filename=filename)

    document.template = env.get_template("templates/index.html")
