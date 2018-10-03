import bokeh.plotting

document = bokeh.plotting.curdoc()
figure = bokeh.plotting.figure(match_aspect=True,
                               aspect_scale=1)
figure.circle([1, 2, 3], [1, 2, 3])

def callback():
    print("attempting to set x/y to non-aspect limits")
    figure.x_range.start = 0
    figure.x_range.end = 2

def one_to_one():
    print("attempting to set 1:1 ratio")
    figure.x_range.start = 2
    figure.x_range.end = 5

button_0 = bokeh.models.Button(label="unusual aspect ratio")
button_0.on_click(callback)

button_1 = bokeh.models.Button(label="1:1 aspect ratio")
button_1.on_click(one_to_one)

document.add_root(bokeh.layouts.row(button_0, button_1))
document.add_root(figure)
