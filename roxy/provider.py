# coding: UTF-8
from roxy.counter.interface import AbstractCounter
from roxy.counter.handlers import *


class ApiKeyRequestExceed(BaseException):
    def __init__(self, count, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = count

    def __str__(self):
        return "Limit of count is exceed: %i" % self.count


class ApiKeyUndefined(BaseException):
    pass


class ApiProviderList:
    """Список провайдеров"""

    def __init__(self):
        super().__init__()
        self._providers = dict()
        self._counter_storage = None

    def add_items_from_dict(self, items):
        """Инициализация компонентов"""

        if not self._counter_storage:
            raise RuntimeError('Не определен компонент для хранения счетчиков обращений по ключю')

        for (provider_key, provider_item) in items.items():
            provider = ApiProvider(provider_item['host'], provider_item['params'],
                                   name=provider_item['name'],
                                   protocol=provider_item['protocol'])

            for (key_name, key_value) in provider_item['keys'].items():
                provider.add_key(
                    key_name,
                    ApiProviderKey(
                        key_value['name'],
                        counter_storage=self._counter_storage,
                        limits=key_value['limits'],
                        key_prefix=provider_key + "-" + key_name
                    )
                )

            self._providers[provider_key] = provider

        return self

    def get_provider_key_by_domain(self, domain):
        """Возвращает объект конкретного ключа провайдера, ассоциированного с указанным поддоменом"""
        (key_name, provider_name) = self._parse_domain(domain)
        if provider_name not in self._providers:
            raise ApiKeyUndefined

        provider = self._providers[provider_name]
        key = provider.get_key(key_name)
        return provider, key

    def set_counter_storage(self, storage_class):
        if not isinstance(storage_class, AbstractCounter):
            raise NotImplementedError

        self._counter_storage = storage_class

        return self

    @staticmethod
    def _parse_domain(domain=""):
        parts = domain.split('.', 3)

        if len(parts) < 2:
            raise ApiKeyUndefined('Переданый домен неправильного формата')

        return parts[0], parts[1]


class ApiProvider:
    """Внешний провайдер данных"""

    def __init__(self, host, params, name="", protocol="http"):
        self.host = host
        self.params = params
        self.name = name if name else host
        self.protocol = protocol
        self._keys = {}
        self._request_processors = {}

        # @TODO(igo) Вынести этот код во внешнюю зависимость
        self.add_request_processor(GETMethodProcessor(), 'GET')

    def add_key(self, name, key):
        self._keys[name] = key
        return self

    def get_key(self, name):
        if name not in self._keys:
            raise ApiKeyUndefined

        return self._keys[name]

    def add_request_processor(self, handler, method):
        if not isinstance(handler, MethodProcessor):
            raise RuntimeError()

        self._request_processors[method] = handler
        return self

    def make_response(self, method, response):
        return self._request_processors[method].make_response(response, self)

    def make_request(self, method, request):
        return self._request_processors[method].make_request(request, self)

    @staticmethod
    def get_exceed_response(exception):
        """Метод возвращающий ответ пользователю в случае превышения лимита по обращениям"""
        return 405, str(exception), []


class ApiProviderKey:
    """Ключ для доступа"""

    def __init__(self, name, counter_storage, limits=None, key_prefix=None):
        self.name = name
        self._counter_storage = counter_storage
        self._limit_handler, self.limit = self.parse_limits(limits, key_prefix)

    @staticmethod
    def parse_limits(limits, prefix=None):
        limit_type = limits['type']
        if limit_type == 'interval':
            handler = IntervalCounterHandler(limits['value']['interval'], prefix)
            return handler, limits['value']['limit']

        raise NotImplementedError("Попытка инициации обработчика счетчика неизвестного типа %s" % limit_type)

    def get_limits(self):
        value = 0
        try:
            key = self._limit_handler.get_cur_key()
            value = self._counter_storage.get_count(key)
        except KeyError:
            pass

        return value

    def inc(self):
        value = 1
        try:
            key = self._limit_handler.get_cur_key()
            value = self._counter_storage.increment_by_key(key)
        except KeyError:
            self._counter_storage.add_key(key, value)

        return value


class MethodProcessor:

    @staticmethod
    def make_response(response, provider):
        raise NotImplementedError()

    @staticmethod
    def make_request(request, provider):
        raise NotImplementedError()


class GETMethodProcessor(MethodProcessor):

    not_accept_headers = ['Transfer-Encoding']

    @staticmethod
    def make_response(response, provider):
        headers = [(name, val) for name, val in response.headers.items()
                   if name not in GETMethodProcessor.not_accept_headers]
        return response.code, response.body, headers

    @staticmethod
    def make_request(request, provider):
        from tornado.httputil import url_concat
        from urllib.parse import parse_qs

        request_url = '%s://%s%s' % (provider.protocol, provider.host, request.path)
        get_params = dict((k, v if len(v) > 1 else v[0]) for k, v in parse_qs(request.query).items())
        get_params.update(provider.params['keyParams'])

        request_url = url_concat(request_url, get_params)
        request_headers = request.headers
        request_headers['Host'] = provider.host

        return request_url, request_headers
