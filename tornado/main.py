#!/usr/bin/env python
import os
import tornado.web
import jinja2
from bokeh.server.server import Server
import bar.main


env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))


class Index(tornado.web.RequestHandler):
    def get(self):
        template = env.get_template("index.html")
        self.write(template.render(message="Hello, world!"))


def bokeh_server():
    extra_patterns = [
        ('/', Index),
        (r"/_static/(.*)", tornado.web.StaticFileHandler, {"path": "./_static"}),
        (r"/bar/static/(.*)", tornado.web.StaticFileHandler, {"path": "./bar/static"})
    ]
    return Server({"/bkapp": bar.main.app}, extra_patterns=extra_patterns)


if __name__ == '__main__':
    print("starting bokeh server")
    server = bokeh_server()
    server.io_loop.start()
