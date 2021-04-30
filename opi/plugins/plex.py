import opi
from opi.plugins import BasePlugin
import subprocess

class PlexMediaServer(BasePlugin):
	main_query = "plex"
	description = "Plex Media Server"
	queries = ('plex', 'plexmediaserver')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install plexmediaserver from Plex repository?", 'y'):
			return

		opi.add_repo(
			filename = 'PlexRepo',
			name = 'PlexRepo',
			url = 'https://downloads.plex.tv/repo/rpm/$basearch/',
			gpgkey = 'https://downloads.plex.tv/plex-keys/PlexSign.key'
		)

		opi.install_packages(['plexmediaserver'])
		opi.ask_keep_repo('PlexRepo')
