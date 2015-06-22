# coding: UTF-8

import tornado.escape
import tornado.web
import tornado.httpclient
from tornado import gen


class ProxyHandler(tornado.web.RequestHandler):

    limits_for_key = {
        'dgis': 20,
    }

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        http = tornado.httpclient.AsyncHTTPClient()
        request_url = 'http://catalog.api.2gis.ru/%s?key=ruaenm7219' % self.request.path
        request_headers = self.request.headers
        request_headers['Host'] = 'catalog.api.2gis.ru'

        counter_key = 'dgis'
        count_val = self.application.counter.get_count(counter_key)

        limits_for_key = self.limits_for_key[counter_key]
        if count_val >= limits_for_key:
            print('Limit of request fer hour is %s exceed ' % (str(limits_for_key)))
            raise tornado.web.HTTPError(405)

        self.application.counter.increment_by_key(counter_key)

        response = yield http.fetch(request_url, headers=request_headers)

        self.clear()
        for header in response.headers:
            if header not in ['Transfer-Encoding']:
                self.set_header(header, response.headers[header])

        if response.body:
            self.write(response.body)

        self.finish()

        print('Count of request: %s' % (self.application.counter.get_count(counter_key)))