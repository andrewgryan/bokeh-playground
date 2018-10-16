import bokeh.plotting
import bokeh.layouts
menu = [
    ("A", "a"),
    ("B", "b"),
]
dropdown = bokeh.models.Dropdown(menu=menu)
dropdown.on_click(lambda value: print(value))
button = bokeh.models.Button()
def on_click():
    dropdown.menu = [("C", "c")]
button.on_click(on_click)
document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.row(button, dropdown))
