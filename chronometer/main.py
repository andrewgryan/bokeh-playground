import bokeh.plotting
import bokeh.models

widgets = [
        bokeh.models.DatePicker(),
        bokeh.models.Slider(
            value=1.5,
            start=1.5,
            end=13.5,
            step=3),
        bokeh.models.RangeSlider(
            value=(0, 3),
            start=0,
            end=12,
            step=3),
        ]
document = bokeh.plotting.curdoc()
document.add_root(bokeh.layouts.column(*widgets))
