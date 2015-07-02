import re
import roxy.counter.interface as counter_interface


class ApiProviderList:
    """Список провайдеров"""

    def __init__(self):
        self.__init__()
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

            for (key_name, key_value) in provider_item.keys.items():
                provider.add_key(
                    key_name,
                    ApiProviderKey(
                        key_value['name'],
                        counter_storage=self._counter_storage,
                        limit_per_month=key_value['limits']['month'],
                        limit_per_hour=key_value['limits']['hour']
                    )
                )

            self._providers[provider_key] = provider

        return self

    def get_provider_key_by_domain(self, domain):
        """Возвращает объект конкретного ключа провайдера, ассоциированного с указанным поддоменом"""
        try:
            (provider_name, key) = self._parse_domain(domain)
            if provider_name not in self._providers:
                raise RuntimeError

            provider = self._providers[provider_name]
            return provider, provider.get_key(key)
        except RuntimeError:
            raise

    def set_counter_storage(self, storage_class):
        if isinstance(storage_class, counter_interface):
            raise NotImplementedError

        self._counter_storage = storage_class

        return self

    @staticmethod
    def _parse_domain(domain=""):
        pattern = '(.+)\.(.+)'
        if not re.match(pattern, domain):
            raise RuntimeError('Переданый домен неправильного формата')

        return re.findall(pattern, domain)[0]


class ApiProvider:
    """Внешний провайдер данных"""

    def __init__(self, host, params, name="", protocol="http"):
        self.host = host
        self.params = params
        self.name = name if name else host
        self.protocol = protocol
        self._keys = {}
        self._request_processors = {}

    def add_key(self, name, key):
        self._keys[name] = key
        return self

    def add_request_processor(self, handler, method):
        if not isinstance(handler, MethodProcessor):
            raise RuntimeError()

        self._request_processors[method] = handler
        return self

    def make_response(self, method):
        return self._request_processors[method].make_response()

    def make_request(self, method):
        return self._request_processors[method].make_request()

    def get_exceed_response(self):
        """Метод возвращающий ответ пользователю в случае превышения лимита по обращениям"""
        import tornado.web
        raise tornado.web.HTTPError(405)


class ApiProviderKey:
    """Ключ для доступа"""

    def __init__(self, name, counter_storage, limit_per_month, limit_per_hour=None):
        self.name = name
        self._counter_storage = counter_storage
        self.limit_per_month = limit_per_month
        self.limit_per_hour = limit_per_hour

    def get_limits(self):
        pass

    def inc(self):
        pass


class MethodProcessor:

    @staticmethod
    def make_response(response, provider):
        pass

    @staticmethod
    def make_request(request, provider):
        pass

class GETMethodProcessor(MethodProcessor):

    not_accept_headers = ['Transfer-Encoding']

    @staticmethod
    def make_response(response, provider):
        headers = ((name, val) for name, val in response.headers.items()
                   if name not in GETMethodProcessor.not_accept_headers)
        return response.body, headers

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