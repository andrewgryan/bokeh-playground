import bokeh.plotting
import bokeh.models
import bokeh.layouts


def main():
    document = bokeh.plotting.curdoc()
    first = bokeh.plotting.figure(
        active_scroll="wheel_zoom")
    second = bokeh.plotting.figure(
        active_scroll="wheel_zoom",
        x_range=first.x_range,
        y_range=first.y_range)
    figures = [
     first,
     second
    ]
    figures[0].circle([1, 2, 3], [1, 2, 3])
    figures[1].circle([1, 2, 3], [1, 2, 3], fill_color="red", line_color=None)
    for f in figures:
        f.toolbar.logo = None
        f.toolbar_location = None

    layout = bokeh.layouts.row(*figures, sizing_mode="stretch_both")
    layout.children = [figures[0]]  # Trick to keep correct sizing modes

    button = bokeh.models.Button()
    button.on_click(toggle(figures, layout))
    document.add_root(layout)
    document.add_root(button)


def toggle(figures, layout):
    def render():
        if len(layout.children) == 1:
            layout.children = figures
        else:
            layout.children = [figures[0]]
    return render


if __name__.startswith('bk'):
    main()
