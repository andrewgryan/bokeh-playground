import bokeh.plotting


class Application(object):
    def __init__(self):
        self.roots = []
        self.button = bokeh.models.Button()
        self.roots.append(self.button)


def main():
    app = Application()
    document = bokeh.plotting.curdoc()
    for root in app.roots:
        document.add_root(root)


if __name__.startswith("bk"):
    main()
