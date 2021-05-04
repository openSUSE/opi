import opi
from opi.plugins import BasePlugin
import subprocess

class GoogleChrome(BasePlugin):
	main_query = "chrome"
	description = "Google Chrome web browser"
	queries = ('chrome', 'google-chrome')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install Chrome from Google repository?", 'y'):
			return

		opi.add_repo(
			filename = 'google-chrome',
			name = 'google-chrome',
			url = 'http://dl.google.com/linux/chrome/rpm/stable/x86_64',
			gpgkey = 'https://dl.google.com/linux/linux_signing_key.pub'
		)

		opi.install_packages(['google-chrome-stable'])
		opi.ask_keep_repo('google-chrome')
