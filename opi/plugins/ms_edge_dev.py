import opi
import subprocess

from opi.plugins import BasePlugin

class MSEdgeDev(BasePlugin):
	main_query = "msedge-dev"
	description = "Microsoft Edge Dev"
	queries = ('microsoft-edge-dev', 'msedge-dev', 'edge-dev')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install Microsoft Edge Dev from Microsoft repository?", 'y'):
			return

		opi.add_repo(
			filename = 'microsoft-edge',
			name = 'Microsoft Edge',
			url = 'https://packages.microsoft.com/yumrepos/edge',
			gpgkey = 'https://packages.microsoft.com/keys/microsoft.asc'
		)

		# prevent post install script from messing with our repos
		subprocess.call(['sudo', 'rm', '-f', '/etc/default/microsoft-edge-dev'])
		subprocess.call(['sudo', 'touch', '/etc/default/microsoft-edge-dev'])

		opi.install_packages(['microsoft-edge-dev'])
		opi.ask_keep_repo('microsoft-edge')
