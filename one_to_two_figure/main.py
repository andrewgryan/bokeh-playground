import bokeh.plotting
import bokeh.models
import bokeh.layouts

document = bokeh.plotting.curdoc()

figure_1 = bokeh.plotting.figure()
figure_1.circle([1, 2, 3], [1, 2, 3])
figure_2 = bokeh.plotting.figure()
figure_2.circle([1, 2, 3], [1, 2, 3], fill_color="red")

layout = bokeh.layouts.row(figure_1)

def on_click():
    layout.children = [figure_1, figure_2]
button = bokeh.models.Button()
button.on_click(on_click)

document.add_root(layout)
document.add_root(button)
