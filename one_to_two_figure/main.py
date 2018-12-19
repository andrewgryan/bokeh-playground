import bokeh.plotting
import bokeh.models
import bokeh.layouts


def main():
    document = bokeh.plotting.curdoc()
    figures = [
     bokeh.plotting.figure(),
     bokeh.plotting.figure()
    ]
    figures[0].circle([1, 2, 3], [1, 2, 3])
    figures[1].circle([1, 2, 3], [1, 2, 3], fill_color="red", line_color=None)

    for f in figures:
        f.toolbar.logo = None
        f.toolbar_location = None

    layout = bokeh.layouts.row(*figures, sizing_mode="stretch_both")
    button = bokeh.models.Button()
    button.on_click(toggle("single", figures, layout))
    document.add_root(layout)
    document.add_root(button)


def toggle(design, figures, layout):
    def render():
        nonlocal design
        # Layout figures
        if design == "double":
            layout.children = figures
        else:
            layout.children = [figures[0]]

        # Toggle state
        if design == "double":
            design = "single"
        else:
            design = "double"
    return render


if __name__.startswith('bk'):
    main()
