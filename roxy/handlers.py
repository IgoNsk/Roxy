# coding: UTF-8

import tornado.escape
import tornado.web
import tornado.httpclient
from tornado.httputil import url_concat, _parseparam
from tornado import gen

try:
    from urllib import parse_qs  # py2
except ImportError:
    from urllib.parse import parse_qs  # py3


class ProxyHandler(tornado.web.RequestHandler):

    keys = {
        'dgis': {
            'protocol': 'http',
            'host': 'catalog.api.2gis.ru',
            'keyParams': {
                'key': 'ruaenm7219',
            },
            'limits': 20,
        }
    }

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        http = tornado.httpclient.AsyncHTTPClient()

        key = 'dgis'
        provider_config = self.keys[key]

        request_url = '%s://%s%s' % (provider_config['protocol'], provider_config['host'], self.request.path)
        get_params = dict((k, v if len(v) > 1 else v[0]) for k, v in parse_qs(self.request.query).items())
        get_params.update(provider_config['keyParams'])

        request_url = url_concat(request_url, get_params)
        request_headers = self.request.headers
        request_headers['Host'] = provider_config['host']

        print('GET Request: %s' % (request_url,))

        count_val = self.application.counter.get_count(key)
        limits_for_key = provider_config['limits']
        if count_val >= limits_for_key:
            print('Limit of request fer hour is %s exceed ' % (str(limits_for_key)))
            raise tornado.web.HTTPError(405)

        self.application.counter.increment_by_key(key)

        response = yield http.fetch(request_url, headers=request_headers)

        self.clear()
        for header in response.headers:
            if header not in ['Transfer-Encoding']:
                self.set_header(header, response.headers[header])

        if response.body:
            self.write(response.body)

        self.finish()

        print('Count of request: %s' % (self.application.counter.get_count(key)))