import opi
from opi.plugins import BasePlugin

class ResilioSync(BasePlugin):
	main_query = 'resilio-sync'
	description = 'Decentralized file sync between devices using bittorrent protocol (See OSS alternative syncthing)'
	queries = ['resilio-sync', 'resilio', 'rslsync']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no('Do you want to install resilio-sync from resilio-sync repository?'):
			return

		opi.add_repo(
			filename = 'resilio-sync',
			name = 'resilio-sync',
			url = 'https://linux-packages.resilio.com/resilio-sync/rpm/$basearch',
			gpgkey = 'https://linux-packages.resilio.com/resilio-sync/key.asc',
			gpgcheck = False
		)

		opi.install_packages(['resilio-sync'])
		opi.ask_keep_repo('resilio-sync')
