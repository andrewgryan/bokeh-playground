import forest
import bokeh.plotting
import bokeh.layouts


def parse_item(word):
    return word, word.lower()


def limited(state, update):
    next_state = state[2:] + [update]
    return state[:2] + next_state[-5:]


def format_menu(items):
    return items[:2] + [None] + items[2:]


def controls(stream):
    menu_stream = stream.map(parse_item).scan([], limited).map(format_menu)
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
    return bokeh.layouts.row(*buttons, dropdown)


stream = forest.Stream()
root = controls(stream)
stream.emit("A")
stream.emit("B")

document = bokeh.plotting.curdoc()
document.add_root(root)
