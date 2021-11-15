import opi
import subprocess
import textwrap

from opi.plugins import BasePlugin

class MSEdge(BasePlugin):
	main_query = "msedge"
	description = "Microsoft Edge"
	queries = ('microsoft-edge', 'msedge', 'edge')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install Microsoft Edge from Microsoft repository?", 'y'):
			return

		print("Which version do you want to install?")
		option = opi.ask_for_option(options=[
			'microsoft-edge-stable',
			'microsoft-edge-beta',
			'microsoft-edge-dev',
		])

		opi.add_repo(
			filename = 'microsoft-edge',
			name = 'Microsoft Edge',
			url = 'https://packages.microsoft.com/yumrepos/edge',
			gpgkey = 'https://packages.microsoft.com/keys/microsoft.asc'
		)

		# prevent post install script from messing with our repos
		defaults_file = option.replace('-stable', '')
		subprocess.call(['sudo', 'rm', '-f', '/etc/default/%s' % defaults_file])
		subprocess.call(['sudo', 'touch', '/etc/default/%s' % defaults_file])

		opi.install_packages([option])
		opi.ask_keep_repo('microsoft-edge')
