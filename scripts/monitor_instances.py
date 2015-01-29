#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from urlparse import urljoin
import requests
import sys


parser = ArgumentParser()
parser.add_argument('-H', '--host', default='localhost')
parser.add_argument('-p', '--port', default=8080, type=int)
parser.add_argument('-s', '--scheme', default='http')
args = parser.parse_args()
url = '%s://%s:%d/' % (args.scheme, args.host, args.port)
r = requests.get(urljoin(url, 'beat/instances/down'))
data = r.json()['instances']['down']
if data:
    sys.stderr.write('%d hosts are not making heartbeats\n' % len(data))
    for i in data:
        sys.stderr.write('%s\n' % i)
    sys.stderr.flush()
    sys.exit(-1)
