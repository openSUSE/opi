#!/usr/bin/python3

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from opi.plugins import PluginManager

pm = PluginManager()

for plugin in pm.plugins:
	print('Checking plugin: %s' % plugin)
	assert plugin.main_query != ""
	assert plugin.description != ""
	assert plugin.main_query in plugin.queries, "Plugin main query must be in queries list"
