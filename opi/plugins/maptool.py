import opi
from opi.plugins import BasePlugin
from opi import github

class MapTool(BasePlugin):
	main_query = 'maptool'
	description = 'Virtual Tabletop for playing roleplaying games'
	queries = ['maptool', 'MapTool']

	@classmethod
	def run(cls, query):
		github.install_rpm_release('RPTools', 'maptool', allow_unsigned=True) # no key available
