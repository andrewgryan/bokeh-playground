import bokeh.plotting
import bokeh.layouts

letters = ["A", "B"]

def as_menu(letters):
    return [(letter, letter.lower()) for letter in letters]
dropdown = bokeh.models.Dropdown(menu=as_menu(letters))
dropdown.on_click(lambda value: print(value))

def on_click():
    dropdown.menu = as_menu(["C"])
button = bokeh.models.Button()
button.on_click(on_click)

document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.row(button, dropdown))
