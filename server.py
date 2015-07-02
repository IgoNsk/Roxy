# coding: UTF-8
import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.autoreload
from roxy.handlers import *
from roxy.counter.memory_counter import MemoryCounter
from tornado.options import define, options
from gredis.client import AsyncRedis

define('port', default=8888, help="run on given port", type=int)

# client = AsyncRedis("localhost", 6379)
# https://pypi.python.org/pypi/gredis/0.0.7

class RoxyApplicationServer(tornado.web.Application):

    DGIS_KEY = 'dgis'

    def __init__(self):
        handlers = [
            (r"/(.+)", ProxyHandler),
        ]

        settings = dict(
            app_name=u"pRoxy Island",
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )

        self.counter = MemoryCounter()
        self.counter.add_key('dgis')
        self.counter.initialization()

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
