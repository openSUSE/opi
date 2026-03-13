import opi
from opi.plugins import BasePlugin

class PlexMediaServer(BasePlugin):
	main_query = 'plex'
	description = 'Plex Media Server (See OSS alternative jellyfin or emby)'
	queries = ['plex', 'plexmediaserver']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no('Do you want to install plexmediaserver from Plex repository?'):
			return

		opi.add_repo(
			filename = 'plex',
			name = 'PlexTv',
			url = 'https://repo.plex.tv/rpm/',
			gpgkey = 'https://downloads.plex.tv/plex-keys/PlexSign.v2.key'
		)

		opi.install_packages(['plexmediaserver'])
		opi.ask_keep_repo('PlexRepo')
