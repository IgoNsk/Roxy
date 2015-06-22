# coding: UTF-8

import tornado.escape
import tornado.web
import tornado.httpclient
from tornado import gen


class ProxyHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        http = tornado.httpclient.AsyncHTTPClient()
        request_url = 'http://catalog.api.2gis.ru/%s?key=ruaenm7219' % self.request.path
        request_headers = self.request.headers
        request_headers['Host'] = 'catalog.api.2gis.ru'

        response = yield http.fetch(request_url, headers=request_headers)

        self.clear()
        for header in response.headers:
            if header not in ['Transfer-Encoding']:
                self.set_header(header, response.headers[header])

        if response.body:
            self.write(response.body)

        self.finish()