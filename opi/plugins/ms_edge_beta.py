import opi
import subprocess

from opi.plugins import BasePlugin

class MSEdgeBeta(BasePlugin):
	main_query = "msedge-beta"
	description = "Microsoft Edge Beta"
	queries = ('microsoft-edge-beta', 'msedge-beta', 'edge-beta')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install Microsoft Edge Beta from Microsoft repository?", 'y'):
			return

		opi.add_repo(
			filename = 'microsoft-edge-beta',
			name = 'Microsoft Edge Beta',
			url = 'https://packages.microsoft.com/yumrepos/edge',
			gpgkey = 'https://packages.microsoft.com/keys/microsoft.asc'
		)

		# prevent post install script from messing with our repos
		subprocess.call(['sudo', 'rm', '-f', '/etc/default/microsoft-edge-beta'])
		subprocess.call(['sudo', 'touch', '/etc/default/microsoft-edge-beta'])

		opi.install_packages(['microsoft-edge-beta'])
		opi.ask_keep_repo('microsoft-edge-beta')