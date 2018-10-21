#!/usr/bin/env python
import tornado.ioloop
import tornado.web


class Index(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world!")


def main():
    return tornado.web.Application([
        (r"/", Index)
    ])


if __name__ == '__main__':
    app = main()
    app.listen(5006)
    tornado.ioloop.IOLoop.current().start()
