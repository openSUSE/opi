import opi

from opi.plugins import BasePlugin
from shutil import which

class MEGAsync(BasePlugin):
	main_query = "megasync"
	description = "Mega Desktop App"
	queries = ['megasync', 'megasyncapp']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install MEGAsync from MEGAsync repository?", 'y'):
			return

		opi.add_repo(
			filename = 'megasync',
			name = 'MEGAsync',
			url = 'https://mega.nz/linux/MEGAsync/openSUSE_Tumbleweed/',
			gpgkey = 'https://mega.nz/linux/MEGAsync/openSUSE_Tumbleweed/repodata/repomd.xml.key'
		)

		packages = ['megasync']

		if which('nautilus'):
			packages.append('nautilus-megasync')

		if which('nemo'):
			packages.append('nemo-megasync')
		
		if which('thunar'):
			packages.append('thunar-megasync')
		
		if which('dolphin'):
			packages.append('dolphin-megasync')

		opi.install_packages(packages)

		opi.ask_keep_repo('megasync')
