import opi
from opi.plugins import BasePlugin
import subprocess

class BraveBrowser(BasePlugin):
	main_query = "brave"
	description = "Brave web browser"
	queries = ['brave', 'brave-browser']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install Brave from Brave repository?"):
			return

		opi.add_repo(
			filename = 'brave-browser',
			name = 'Brave Browser',
			url = 'https://brave-browser-rpm-release.s3.brave.com/x86_64/',
			gpgkey = 'https://brave-browser-rpm-release.s3.brave.com/brave-core.asc'
		)

		# prevent post install script from messing with our repos
		subprocess.call(['sudo', 'rm', '-f', '/etc/default/brave-browser'])
		subprocess.call(['sudo', 'touch', '/etc/default/brave-browser'])

		opi.install_packages(['brave-browser'])
		opi.ask_keep_repo('brave-browser')
