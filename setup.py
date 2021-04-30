#!/usr/bin/python3

from distutils.core import setup
import os

# Load __version__ from opi/version.py
exec(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "opi/version.py")).read())

setup(
    name='opi',
    version=__version__,
    license='GPLv3',
    description='Tool to Search and install almost all packages available for openSUSE and SLE',
    author='Guo Yunhe, Dominik Heidler',
    author_email='i@guoyunhe.me, dheidler@suse.de',
    requires=['lxml', 'requests', 'termcolor'],
    packages=['opi', 'opi.plugins'],
    scripts=['bin/opi'],
)
