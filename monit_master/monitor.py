#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from flask import abort, Blueprint, request, jsonify, json


class Beat(object):
    DEFAULT_PREFIX = 'beat'
    DEFAULT_TIMEOUT = 300

    def __init__(self, app, redis, boto):
        self.blueprint = Blueprint(
            'heartbeat', 'heartbeat', url_prefix='/beat')
        self._redis = redis
        self._boto = boto
        self.hosts = {}
        self.updated = None
        self.prefix = app.config.get('BEAT_PREFIX', self.DEFAULT_PREFIX)
        self.t = app.config.get('BEAT_TIMEOUT', self.DEFAULT_TIMEOUT)
        self.blueprint.add_url_rule(
            '/ping', 'ping', self.ping, methods=['GET', 'POST'])
        self.blueprint.add_url_rule(
            '/inventory', 'inventory', self.inventory,
            methods=['GET', 'POST'])
        self.blueprint.add_url_rule(
            '/instances/<string:state>', 'instances', self.instances)
        self.blueprint.add_url_rule(
            '/instances', 'instances', self.instances)
        self.blueprint.add_url_rule(
            '/timeout', 'timeout', self.timeout, methods=['GET', 'POST'])
        app.register_blueprint(self.blueprint)

    def _key(self, address):
        return '%s:%s' % (self.prefix, address)

    def timeout(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            try:
                self.t = data['timeout']
            except KeyError:
                abort(400)
        return jsonify({
            'timeout': self.t
        })

    def ping(self):
        """
        POST: update the heartbeat of the client
        GET: get the ttl of the client
        """
        key = self._key(request.remote_addr)
        if request.method == 'POST':
            self._redis.set(key, '', ex=self.t)
            return jsonify({'beat': request.remote_addr})
        else:
            return jsonify({
                'beat': request.remote_addr,
                'ttl': self._redis.ttl(key),
            })

    def inventory(self):
        """
        POST: update inventory from AWS
        GET: return current inventory
        """
        if request.method == 'POST':
            hosts = {}
            for r in self._boto.get_all_reservations():
                for i in r.instances:
                    hosts[i.private_ip_address] = i.state
            self.hosts = hosts
            self.updated = datetime.now()
        return jsonify({'hosts': self.hosts, 'updated': self.updated})

    def instances(self, state=None):
        """
        Check if a host is still alive.

        For each host in inventory built from AWS, its corresponding heartbeat
        in redis is checked. If the heartbeat does not exist, the host is
        considered down.
        """
        if state and state not in ('up', 'down'):
            abort(404)
        instances = {
            'up': [],
            'down': [],
        }
        pipe = self._redis.pipeline(transaction=False)
        for host in self.hosts:
            pipe.get(self._key(host))
        for r in pipe.execute():
            if r is None:
                instances['down'].append(host)
            else:
                instances['up'].append(host)
        if state:
            return jsonify({
                'instances': {state: instances[state]}
            })
        else:
            return jsonify({'instances': instances})
