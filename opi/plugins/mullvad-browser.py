import opi
from opi.plugins import BasePlugin
import subprocess

class MullvadBrowser(BasePlugin):
	main_query = 'mullvad-browser'
	description = 'Mullvad web browser'
	queries = ['mullvad', 'mullvad-browser']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no('Do you want to install Mullvad-browser from Mullvad repository?'):
			return

		opi.add_repo(
			filename = 'mullvad',
			name = 'Mullvad VPN',
			url = 'https://repository.mullvad.net/rpm/stable/$basearch/',
                        gpgkey = 'https://repository.mullvad.net/rpm/mullvad-keyring.asc',
                        gpgcheck = 1
		)

		opi.install_packages(['mullvad-browser'])
		opi.ask_keep_repo('mullvad')
