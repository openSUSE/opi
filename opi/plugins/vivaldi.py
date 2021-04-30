import opi
from opi.plugins import BasePlugin
import subprocess

class Vivaldi(BasePlugin):
	main_query = "vivaldi"
	description = "Vivaldi webbrowser"
	queries = ('vivaldi')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install Vivaldi from Vivaldi repository?", 'y'):
			return

		opi.add_repo(
			filename = 'vivaldi',
			name = 'vivaldi',
			url = 'https://repo.vivaldi.com/archive/rpm/$basearch',
			gpgkey = 'https://repo.vivaldi.com/archive/linux_signing_key.pub'
		)

		opi.install_packages(['vivaldi-stable'])
		opi.ask_keep_repo('vivaldi')
