#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import abort, Blueprint, request, jsonify, json, current_app


class Beat(object):
    DEFAULT_PREFIX = 'bt'
    DEFAULT_PING_TIMEOUT = 240
    DEFAULT_INVENTORY_TIMEOUT = 240

    def __init__(self, app, redis, boto):
        self.blueprint = Blueprint(
            'heartbeat', 'heartbeat', url_prefix='/beat')
        self._redis = redis
        self._boto = boto
        app.config.setdefault('BEAT_PREFIX', self.DEFAULT_PREFIX)
        app.config.setdefault('BEAT_PING_TIMEOUT', self.DEFAULT_PING_TIMEOUT)
        app.config.setdefault(
            'BEAT_INVENTORY_TIMEOUT', self.DEFAULT_INVENTORY_TIMEOUT)
        self.blueprint.add_url_rule('/ping', 'ping', self.ping)
        self.blueprint.add_url_rule(
            '/instances/<string:state>', 'instances', self.instances)
        self.blueprint.add_url_rule(
            '/instances/', 'instances', self.instances)
        app.register_blueprint(self.blueprint)
        app.extensions['beat'] = self

    @staticmethod
    def _key(key):
        return '%s:%s' % (current_app.config['BEAT_PREFIX'], key)

    def ping(self):
        """
        GET: update the heartbeat of the client
        """
        self._redis.set(
            self._key(request.remote_addr), '',
            ex=current_app.config['BEAT_PING_TIMEOUT'])
        return jsonify({'pong': request.remote_addr})

    def get_inventory(self):
        key = self._key('inventory')
        data = self._redis.get(key)
        if not data:
            hosts = {}
            for r in self._boto.get_all_reservations():
                for i in r.instances:
                    if i.state == 'running':
                        hosts[i.private_ip_address] = [
                            ('%s_%s' % (k, v)).strip('_')
                            for k, v in i.tags.items()]
                self._redis.set(
                    key, json.dumps(hosts),
                    ex=current_app.config['BEAT_INVENTORY_TIMEOUT'])
        else:
            hosts = json.loads(data)
        return hosts

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
        hosts = self.get_inventory().keys()
        for host in hosts:
            pipe.get(self._key(host))
        for i, r in enumerate(pipe.execute()):
            if r is None:
                instances['down'].append(hosts[i])
            else:
                instances['up'].append(hosts[i])
        if state:
            return jsonify({
                'instances': {state: instances[state]}
            })
        else:
            return jsonify({'instances': instances})
