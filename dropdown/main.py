import forest
import bokeh.plotting
import bokeh.layouts


stream = forest.Stream()
def menu_item(word):
    return word, word.lower()

def limited(state, update):
    next_state = state + [update]
    return next_state[-5:]

menu_stream = stream.map(menu_item).scan([], limited)

dropdown = bokeh.models.Dropdown()
dropdown.on_click(lambda value: print(value))
def update(menu):
    dropdown.menu = menu
menu_stream.subscribe(update)

buttons = []
def on_click():
    stream.emit("C")
button = bokeh.models.Button()
button.on_click(on_click)
buttons.append(button)

def on_click():
    stream.emit("D")
button = bokeh.models.Button()
button.on_click(on_click)
buttons.append(button)

stream.emit("A")
stream.emit("B")

document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.row(*buttons, dropdown))
