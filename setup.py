#!/usr/bin/python3

from setuptools import setup, find_packages
import os

# Load __version__ from opi/version.py
exec(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'opi/version.py')).read())

setup(
    name='opi',
    version=__version__,
    license='GPLv3',
    description='Tool to Search and install almost all packages available for openSUSE and SLE',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Guo Yunhe, Dominik Heidler, KaratekHD',
    author_email='i@guoyunhe.me, dheidler@suse.de, karatek@karatek.net',
    install_requires=['lxml', 'requests', 'termcolor', 'curses'],
    packages=['opi', 'opi.plugins', 'opi.config'],
    scripts=['bin/opi'],
)
