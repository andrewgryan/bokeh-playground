#!/usr/bin/env python
import os
import tornado.ioloop
import tornado.web


class Index(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


def main():
    static_path = os.path.join(os.path.dirname(__file__), 'static')
    return tornado.web.Application([
        (r"/", Index)
    ],
    static_path=static_path)


if __name__ == '__main__':
    port = 5006
    app = main()
    app.listen(port)
    print("serving localhost:{}".format(port))
    tornado.ioloop.IOLoop.current().start()
