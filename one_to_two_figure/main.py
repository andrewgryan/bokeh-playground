import bokeh.plotting
import bokeh.models
import bokeh.layouts

document = bokeh.plotting.curdoc()

figure_1 = bokeh.plotting.figure(plot_width=800)
figure_1.circle([1, 2, 3], [1, 2, 3])
figure_2 = bokeh.plotting.figure(plot_width=800)
figure_2.circle([1, 2, 3], [1, 2, 3], fill_color="red", line_color=None)
figure_3 = bokeh.plotting.figure(plot_width=1600)
figure_3.circle([1, 2, 3], [1, 2, 3], fill_color="red", line_color=None)

layout = bokeh.layouts.row()

button = bokeh.models.Button()
design = "double"


def render():
    global design
    # Layout figures
    if design == "double":
        layout.children = [figure_1, figure_2]
    else:
        layout.children = [figure_3]

    # Update button label
    button.label = design

    # Toggle state
    if design == "double":
        design = "single"
    else:
        design = "double"


def on_click():
    render()


button.on_click(on_click)
document.add_root(layout)
document.add_root(button)
