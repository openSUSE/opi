#!/usr/bin/python3

from distutils.core import setup

setup(
    name='opi',
    version='2.0.0',
    license='GPLv3',
    description='Tool to Search and install almost all packages available for openSUSE and SLE',
    author='Guo Yunhe, Dominik Heidler',
    author_email='dheidler@suse.de',
    requires=['lxml', 'requests', 'termcolor'],
    packages=['opi', 'opi.plugins'],
    scripts=['bin/opi'],
)
