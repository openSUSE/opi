import opi
from opi.plugins import BasePlugin

class Ocenaudio(BasePlugin):
	main_query = 'ocenaudio'
	description = 'Audio Editor'
	queries = [main_query]

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no('Do you want to install ocenaudio from ocenaudio.com?'):
			return

		opi.install_packages(['https://www.ocenaudio.com/downloads/index.php/ocenaudio_opensuse.rpm'], allow_unsigned=True) # rpm is unsigned
