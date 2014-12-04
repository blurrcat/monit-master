#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask import Flask
from monit_master import config
from monit_proxy import MonitProxy


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


if __name__ == '__main__':
    create_app().run(debug=True)
