import os
import sys
from importlib import import_module
import inspect

class BasePlugin(object):
	main_query = ''
	description = ''
	queries = ()

	@classmethod
	def matches(cls, user_query):
		for query in cls.queries:
			if query.find(user_query) != -1:
				return True
		return False

	@classmethod
	def run(cls, query):
		pass

class PluginManager(object):
	def __init__(self):
		self.plugins = []
		for module in os.listdir(os.path.dirname(__file__)):
			if module == '__init__.py' or module[-3:] != '.py' or module == '__pycache__':
				continue
			m = import_module('opi.plugins.%s' % module[:-3])
			for name, obj in inspect.getmembers(m):
				if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
					self.plugins.append(obj)
			self.plugins.sort(key=lambda p: p.main_query)

	def run(self, query):
		query = query.lower()
		for plugin in self.plugins:
			if plugin.matches(query):
				plugin.run(query)
				sys.exit()

	def get_plugin_string(self, indent=''):
		plugins = ""
		for plugin in self.plugins:
			description = plugin.description.replace("\n", "\n" + (" "*16) + "  ")
			plugins += "%s%-16s  %s\n" % (indent, plugin.main_query, description)
		return plugins
