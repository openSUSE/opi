import opi

from opi.plugins import BasePlugin
from shutil import which

class MEGAsync(BasePlugin):
	main_query = "megasync"
	description = "Mega Desktop App"
	queries = ('megasync', 'megasyncapp')

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

		if which('nautilus') is not None:
			packages.append('nautilus-megasync')

		if which('nemo') is not None:
			packages.append('nemo-megasync')
		
		if which('thunar') is not None:
			packages.append('thunar-megasync')
		
		if which('dolphin') is not None:
			packages.append('dolphin-megasync')

		opi.install_packages(packages)

		opi.ask_keep_repo('megasync')
