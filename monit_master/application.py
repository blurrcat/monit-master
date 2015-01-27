#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask import Flask
from redis import StrictRedis
from boto.ec2 import connect_to_region
from monit_master import config
from monit_master.monit_proxy import MonitProxy
from monit_master.monitor import Beat


def create_app():
    app = Flask('monit_master')
    app.config.from_object(config)
    # production config set via environment variables prefixed by "MM_"
    for k, v in os.environ.iteritems():
        if k.startswith('MM_'):
            app.config[k[3:]] = v
    configure_extensions(app)
    return app


def configure_extensions(app):
    MonitProxy(app)
    redis = StrictRedis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB'],
    )
    boto = connect_to_region(app.config['AWS_REGION'])
    Beat(app, redis, boto)


if __name__ == '__main__':
    create_app().run(debug=True, port=8080)
