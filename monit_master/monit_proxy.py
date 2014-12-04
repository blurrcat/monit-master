#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import abort, Blueprint, request, make_response
import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError


b_monit_proxy = Blueprint('monit_proxy', 'monit_proxy', url_prefix='/monit')


class MonitProxy(object):

    def __init__(self, app=None):
        self.config = {}
        self._url_tpl = None
        self._auth = None
        self.blueprint = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.config.setdefault(
            'user', app.config.get('MONIT_USER', 'admin'))
        self.config.setdefault(
            'password', app.config.get('MONIT_PASSWORD', 'monit'))
        self.config.setdefault(
            'scheme', app.config.get('MONIT_SCHEME', 'http'))
        self.config.setdefault(
            'port', app.config.get('MONIT_PORT', 2812))
        self.config.setdefault(
            'timeout', app.config.get('MONIT_TIMEOUT', 2)
        )
        self._url_tpl = (
            self.config['scheme'] + '://%s:' + str(self.config['port']))
        self._auth = (self.config['user'], self.config['password'])
        self.blueprint = Blueprint(
            'monit_proxy', 'monit_proxy', url_prefix='/monit')
        self.blueprint.add_url_rule(
            '/<string:host>/', 'monit_index', self.monit_index)
        self.blueprint.add_url_rule(
            '/<string:host>/<string:service>', 'monit_service',
            self.monit_service, methods=['GET', 'POST']
        )
        app.register_blueprint(self.blueprint)
        extensions = getattr(app, 'extensions', {})
        extensions['monit_proxy'] = self

    def build_url(self, host):
        return self._url_tpl % host

    def _request(self, method, url, **kwargs):
        meth = getattr(requests, method)
        kwargs['auth'] = self._auth
        kwargs['timeout'] = self.config['timeout']
        try:
            resp = meth(url, **kwargs)
        except ConnectionError as e:
            return make_response('connection error to %s: %s' % (url, e), 400)
        except HTTPError as e:
            return make_response('http error: %s', e)
        except Timeout:
            abort(408)
        else:
            return resp.content

    def monit_index(self, host):
        return self._request('get', self.build_url(host))

    def monit_service(self, host, service):
        url = '%s/%s' % (self.build_url(host), service)
        if request.method == 'GET':
            return self._request('get', url)
        else:
            return self._request('post', url, data=request.form)
