"""Prototype to play with HTML bokeh elements"""
import bokeh.plotting
import bokeh.models
import bokeh.layouts


class Toggle(object):
    """Controller to change ColumnDataSource alpha values"""
    def __init__(self, left_images, right_images):
        self.left_images = left_images
        self.right_images = right_images

    def show(self, images):
        print("show method called")

    def hide(self, images):
        print("hide method called")

    def on_change(self, attr, old, new):
        """Interface to bokeh widgets"""
        if new == 0:
            self.show(self.left_images)
            self.hide(self.right_images)
        else:
            self.show(self.right_images)
            self.hide(self.left_images)


def main(bokeh_id):
    figure = bokeh.plotting.figure(sizing_mode="stretch_both", match_aspect=True)
    figure.circle(x=[1, 2, 3], y=[1, 2, 3])

    left_image, right_image = None, None
    toggle = Toggle(left_image, right_image)
    button_group = bokeh.models.widgets.RadioButtonGroup(labels=["left", "right"],
                                                         active=0)
    button_group.on_change("active", toggle.on_change)
    page = bokeh.layouts.column(figure, button_group)
    if bokeh_id == "__main__":
        bokeh.plotting.show(page)
    else:
        bokeh.io.curdoc().add_root(page)


main(__name__)
