#!/usr/bin/python3

from distutils.core import setup
import os

setup(
    name='opi_proxy',
    version='1.0',
    license='GPLv3',
    description='Proxy server for communication between OPI and OBS/PMBS',
    author='Dominik Heidler',
    author_email='dheidler@suse.de',
    requires=['requests', 'Flask'],
    packages=['opi_proxy'],
)
