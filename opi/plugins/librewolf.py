import opi
from opi.plugins import BasePlugin

class librewolf(BasePlugin):
	main_query = 'librewolf'
	description = 'Librewolf is a custom version of Firefox, focused on privacy, security and freedom.'
	queries = ['librewolf', 'Librewolf', 'LibreWolf']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no('Do you want to install librewolf from librewolf repository?'):
			return

		opi.add_repo(
			filename = 'librewolf',
			name = 'librewolf',
			url = 'https://rpm.librewolf.net',
			gpgkey = 'https://rpm.librewolf.net/pubkey.gpg'
		)

		opi.install_packages(['librewolf'])
		opi.ask_keep_repo('librewolf')
