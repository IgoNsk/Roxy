# coding: UTF-8
import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.autoreload
import yaml
from roxy.handlers import *
from roxy.provider import ApiProviderList
from roxy.counter.redis_counter import RedisCounter
from tornado.options import define, options
from gredis.client import AsyncRedis

define('config', help="config file path", type=str)
define('port', default=8888, help="run on given port", type=int)
define('redis_host', default='photo-all-in-one', help='hostname of redis storage', type=str)
define('redis_port', default='6379', help='port of redis storage', type=int)

class RoxyApplicationServer(tornado.web.Application):

    def __init__(self, providers_config, counter):
        handlers = [
            (r"/(.+)", ProxyHandler),
        ]

        settings = dict(
            app_name=providers_config['name'],
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )

        # Создаем список провайдеров, устанавливаем для него хранилище ключей и заполняем элементами из
        # переданного в веб сервер конфига словаря с настройками
        self.provider_list = ApiProviderList()
        self.provider_list.set_counter_storage(counter)\
                          .add_items_from_dict(providers_config['providers'])

        tornado.web.Application.__init__(self, handlers, **settings)
        print('Server is started!')

    @staticmethod
    def load_config_from_file(filename):
        if filename is None:
            raise BaseException('Не указан кофигурационный файл приложения')

        with open(filename, 'r') as stream:
            return yaml.load(stream)

def main():
    tornado.options.parse_command_line()

    config = {}
    try:
        config = RoxyApplicationServer.load_config_from_file(options.config)
    except BaseException as e:
        print(str(e))
        exit(2)

    redis_client = AsyncRedis(options.redis_host, options.redis_port)
    roxy_app = RoxyApplicationServer(config, RedisCounter(redis_client))

    http_server = tornado.httpserver.HTTPServer(roxy_app)
    http_server.listen(options.port)
    instance = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(instance)
    instance.start()

if __name__ == '__main__':
    main()
