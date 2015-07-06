# coding: UTF-8
import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.autoreload
from roxy.handlers import *
from roxy.provider import ApiProviderList
from roxy.counter.memory_counter import MemoryCounter
from tornado.options import define, options
# from gredis.client import AsyncRedis

define('port', default=8888, help="run on given port", type=int)

# client = AsyncRedis("localhost", 6379)
# https://pypi.python.org/pypi/gredis/0.0.7

keys = {
    'dgis': {
        'host': 'catalog.api.2gis.ru',
        'name': 'Web API 2GIS',
        'protocol': 'http',
        'params': {
            'keyParams': {
                'key': 'ruaenm7219',
            },
        },
        'limits': {
            'type': 'interval',
            'value': ('minute', 20),
        },
        'keys': {
            'photo': {
                'name': 'Photo API 2GIS key',
                'limits': {
                    'type': 'interval',
                    'value': ('minute', 20),
                }
            },
            'embassy': {
                'name': 'Embassy app 2GIS key',
                'limits': {
                    'type': 'interval',
                    'value': ('minute', 5),
                }
            },
        },
    }
}


class RoxyApplicationServer(tornado.web.Application):

    def __init__(self, providers_config):
        handlers = [
            (r"/(.+)", ProxyHandler),
        ]

        settings = dict(
            app_name=u"pRoxy Island",
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )

        # Создаем список провайдеров, устанавливаем для него хранилище ключей и заполняем элементами из
        # переданного в веб сервер конфига словаря с настройками
        self.provider_list = ApiProviderList()
        self.provider_list.set_counter_storage(MemoryCounter())\
                          .add_items_from_dict(providers_config)

        tornado.web.Application.__init__(self, handlers, **settings)
        print('Server is started!')


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(RoxyApplicationServer(keys))
    http_server.listen(options.port)
    instance = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(instance)
    instance.start()

if __name__ == '__main__':
    main()
