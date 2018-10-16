import forest
import bokeh.plotting
import bokeh.layouts

stream = forest.Stream()
menu_stream = stream.map(lambda c: (c, c.lower())).scan([], lambda a, i: a + [i])

dropdown = bokeh.models.Dropdown()
dropdown.on_click(lambda value: print(value))
def update(menu):
    dropdown.menu = menu
menu_stream.subscribe(update)

def on_click():
    stream.emit("C")
button = bokeh.models.Button()
button.on_click(on_click)
stream.emit("A")
stream.emit("B")

document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.row(button, dropdown))
