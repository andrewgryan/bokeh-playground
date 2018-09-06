import bokeh.plotting
import bokeh.models
import bokeh.layouts

document = bokeh.plotting.curdoc()

figure_1 = bokeh.plotting.figure()
figure_1.circle([1, 2, 3], [1, 2, 3])
figure_2 = bokeh.plotting.figure()
figure_2.circle([1, 2, 3], [1, 2, 3], fill_color="red")

one_fig_root = bokeh.layouts.row(figure_1)
two_fig_root = bokeh.layouts.row(figure_1, figure_2)

def on_click():
    document.remove_root(one_fig_root)
    document.add_root(two_fig_root)
button = bokeh.models.Button()
button.on_click(on_click)

document.add_root(one_fig_root)
document.add_root(button)
