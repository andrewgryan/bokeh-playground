import argparse
import tornado.web
import tornado.ioloop
import bokeh.resources
import bokeh.palettes
import datetime as dt


class Index(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", resources=bokeh.resources.CDN.render())


class Data(tornado.web.RequestHandler):
    def get(self, dataset, variable):
        # import time
        # time.sleep(5)  # Simulate expensive I/O or slow server
        # self.set_header("Cache-control", "max-age=31536000")
        if dataset == "takm4p4":
            self.write({
                "x": [0, 1e5, 2e5],
                "y": [0, 1e5, 2e5]
            })
        else:
            self.write({
                "x": [0, 1e5, 2e5],
                "y": [0, 3e5, 1e5]
            })


class DataTime(tornado.web.RequestHandler):
    def get(self, dataset):
        # self.set_header("Cache-control", "max-age=31536000")
        x = [dt.datetime.now()]
        self.write({
            "x": [1000 * t.timestamp() for t in x]
        })


class PaletteNames(tornado.web.RequestHandler):
    def get(self):
        names = list(bokeh.palettes.all_palettes.keys())
        self.write({"names": names})


class Palette(tornado.web.RequestHandler):
    def get(self, tail):
        parts = tail.split("/")
        if len(parts) == 1:
            name, = parts
            numbers = list(bokeh.palettes.all_palettes[name].keys())
            self.write({"numbers": numbers})
        elif len(parts) == 2:
            name, number = parts
            number = int(number)
            self.write({"palette": bokeh.palettes.all_palettes[name][number]})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8888)
    args = parser.parse_args()
    app = tornado.web.Application([
        ("/", Index),
        ("/data/(.*)/(.*)", Data),
        ("/palette", PaletteNames),
        ("/palette/(.*)", Palette),
        ("/time/(.*)", DataTime),
    ])
    app.listen(args.port)
    print(f"listening on localhost:{args.port}")
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
