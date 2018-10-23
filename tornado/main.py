#!/usr/bin/env python
import os
import tornado.ioloop
import tornado.web
import jinja2
import bokeh.embed
from bokeh.server.server import Server
import bar.main


env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))


class Index(tornado.web.RequestHandler):
    def get(self):
        template = env.get_template("index.html")
        self.write(template.render(message="Hello, world!", app="foo"))


class Goodbye(tornado.web.RequestHandler):
    def get(self):
        script = bokeh.embed.server_document("http://localhost:5006/bkapp")
        if os.path.exists("bar/templates/index.html"):
            path = "bar/templates/index.html"
        else:
            path = "index.html"
        template = env.get_template(path)
        content = template.render(message="Goodbye, world!",
                                  app="bar",
                                  script=script)
        print(content)
        self.write(content)


def tornado_server():
    extra_patterns = [
        (static_regex(app), tornado.web.StaticFileHandler, {"path": static_path(app)})
        for app in ["foo", "bar"]
    ]
    return tornado.web.Application([
        (r"/", Index),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
        (r"/bkapp", bar.main.app),
        (r"/bkapp/(.*)", tornado.web.StaticFileHandler, {"path": "./bkapp"}),
        (r"/hello", Index),
        (r"/goodbye", Goodbye),
    ] + extra_patterns)


def bokeh_server():
    extra_patterns = [
        ('/', Index),
        (r"/static_extra/(.*)", tornado.web.StaticFileHandler,
         {"path": "./static_extra"}),
        (r"/goodbye", Goodbye),
        (static_regex("bar"), tornado.web.StaticFileHandler,
         {"path": static_path("bar")})
    ]
    return Server({"/bkapp": bar.main.app}, extra_patterns=extra_patterns)


def static_regex(app_name):
    return r"/{}/static/(.*)".format(app_name)


def static_path(app_name):
    return os.path.join(os.path.dirname(__file__), app_name, "static")


if __name__ == '__main__':
    server = "bokeh"
    if server == "tornado":
        print("starting tornado server")
        app = tornado_server()
        app.listen(5006)
        tornado.ioloop.IOLoop.current().start()
    else:
        print("starting bokeh server")
        server = bokeh_server()
        server.io_loop.start()
