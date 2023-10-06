import os
from importlib import import_module
import inspect

class BasePlugin:
	main_query = ''
	description = ''
	queries = []

	@classmethod
	def matches(cls, query):
		return query in cls.queries

	@classmethod
	def run(cls, query):
		pass

class PluginManager:
	def __init__(self):
		self.plugins = []
		for module in os.listdir(os.path.dirname(__file__)):
			if module == '__init__.py' or not module.endswith('.py') or module == '__pycache__':
				continue
			m = import_module(f'opi.plugins.{module[:-3]}')
			for name, obj in inspect.getmembers(m):
				if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
					self.plugins.append(obj)
			self.plugins.sort(key=lambda p: p.main_query)

	def run(self, query):
		query = query.lower()
		for plugin in self.plugins:
			if plugin.matches(query):
				plugin.run(query)
				return True

	def get_plugin_string(self, indent=''):
		plugins = ''
		for plugin in self.plugins:
			description = plugin.description.replace('\n', '\n' + (' ' * 16) + '  ')
			plugins += f'{indent}{plugin.main_query:16}  {description}\n'
		return plugins
