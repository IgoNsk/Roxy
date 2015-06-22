# coding: UTF-8
import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.autoreload
from handlers import *
from tornado.options import define, options

define('port', default=8888, help="run on given port", type=int)


class RoxyApplicationServer(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/(.+)", ProxyHandler),
        ]

        settings = dict(
            app_name=u"pRoxy Island",
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        print('Server is started!')


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(RoxyApplicationServer())
    http_server.listen(options.port)
    instance = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(instance)
    instance.start()

if __name__ == '__main__':
    main()