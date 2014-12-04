#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

__version__ = '0.1.0'
readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


install_requires = [
    'Flask==0.10.1',
    'requests==2.5.0',
]
tests_require = ['pytest==2.5.1', 'pytest-cov==1.6']
develop_require = tests_require + [
    'Sphinx>=1.2.1', 'pylint>=1.1.0'
]

setup(
    name='monit_master',
    version=__version__,
    description='',
    long_description=readme + '\n\n' + history,
    author='blurrcat',
    author_email='blurrcat@gmail.com',
    url='https://github.com/blurrcat/monit-master',
    packages=[
        'monit_master',
    ],
    package_dir={'monit_master': 'monit_master'},
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'develop': develop_require
    },
    zip_safe=False,
    keywords='monit-master',
)
