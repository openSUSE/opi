import opi

from opi.plugins import BasePlugin

class Atom(BasePlugin):
	main_query = "atom"
	description = "Atom Text Editor"
	queries = ['atom', 'atom-editor']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install Atom from Atom repository?", 'y'):
			return

		opi.add_repo(
			filename = 'atom',
			name = 'Atom',
			url = 'https://packagecloud.io/AtomEditor/atom/el/7/x86_64/?type=rpm',
			gpgkey = 'https://packagecloud.io/AtomEditor/atom/gpgkey'
		)

		opi.install_packages(['atom'])

		opi.ask_keep_repo('atom')
