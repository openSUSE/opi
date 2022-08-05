import opi
from opi.plugins import BasePlugin
import subprocess

class Skype(BasePlugin):
	main_query = "skype"
	description = "Microsoft Skype"
	queries = ['skype']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install Skype from Microsoft repository?", 'y'):
			return

		opi.add_repo(
			filename = 'skype-stable',
			name = 'Microsoft Skype',
			url = 'https://repo.skype.com/rpm/stable/',
			gpgkey = 'https://repo.skype.com/data/SKYPE-GPG-KEY'
		)

		opi.install_packages(['skypeforlinux'])
		opi.ask_keep_repo('skype-stable')
