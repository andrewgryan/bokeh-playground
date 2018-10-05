import bokeh.plotting
import bokeh.models

p = bokeh.models.widgets.Paragraph(text="Hello, world!")
values = [1, 2, 3]
index = 0

def plus():
    global index
    index += 1
    print(values[index])
    p.text = "Plus"

def minus():
    global index
    index -= 1
    print(values[index])
    p.text = "Minus"


plus_btn = bokeh.models.Button(label="+")
plus_btn.on_click(plus)

minus_btn = bokeh.models.Button(label="-")
minus_btn.on_click(minus)

document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.row(p, plus_btn, minus_btn))
