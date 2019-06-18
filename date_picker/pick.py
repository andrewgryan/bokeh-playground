import bokeh.models


class Calendar(bokeh.models.DatePicker):
    __implementation__ = "pick.ts"
