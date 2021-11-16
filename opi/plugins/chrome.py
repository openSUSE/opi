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

		print("Which version do you want to install?")
		option = opi.ask_for_option(options=[
			'google-chrome-stable',
			'google-chrome-beta',
			'google-chrome-unstable',
		])

		opi.add_repo(
			filename = 'google-chrome',
			name = 'google-chrome',
			url = 'http://dl.google.com/linux/chrome/rpm/stable/x86_64',
			gpgkey = 'https://dl.google.com/linux/linux_signing_key.pub'
		)

		# prevent post install script from messing with our repos
		defaults_file = option.replace('-stable', '')
		subprocess.call(['sudo', 'rm', '-f', '/etc/default/%s' % defaults_file])
		subprocess.call(['sudo', 'touch', '/etc/default/%s' % defaults_file])

		opi.install_packages([option])
		opi.ask_keep_repo('google-chrome')
