import tornado.web
import tornado.httpclient
from tornado import gen
from tornado.log import gen_log
from roxy.provider import ApiKeyRequestExceed, ApiKeyUndefined


class ProxyHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        """Обработка GET запросов"""
        providers = self.application.provider_list

        # Определение провайдера и ключа по доменному имени
        try:
            domain = self.request.host
            (provider, key) = providers.get_provider_key_by_domain(domain)
        except ApiKeyUndefined as e:
            raise tornado.web.HTTPError(400, str(e))

        # Составляем запрос на основании данных переданных пользователем
        (request_url, request_headers) = provider.make_request('GET', self.request)
        gen_log.info('GET Request: %s' % (request_url,))

        # Делаем попытку увеличить счетчик запросов на +1
        try:
            # TODO(igo) Возможно тут нужен неблокирующий вызов, т.к. будет идти обращение к внешнему сервису
            # хранения данных
            key.inc()
        except ApiKeyRequestExceed as e:
            # В случае если лимит превышен, будет выброшено исключение
            gen_log.warning('%s limits of request per hour is  exceed ' % (str(e.count)))
            raise provider.get_exceed_response(e)

        # Делаем асинхронный неблокирующий запрос к провайдеру, на получение данных
        http = tornado.httpclient.AsyncHTTPClient()
        response = yield http.fetch(request_url, headers=request_headers)

        # Готовим ответ
        (status_code, body, headers) = provider.make_response('GET', response)
        self._render_answer(status_code, body, headers)

    def _render_answer(self, status_code, body, headers):
        self.clear()
        self.set_status(status_code)

        for (name, val) in headers:
            self.set_header(name, val)

        self.write(body)
        self.finish()
