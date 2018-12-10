from bokeh.models import InputWidget


class Chronometer(InputWidget):
    __implementation__ = 'chronometer.ts'
    __css__ = "chronometer/static/chronometer.css"
