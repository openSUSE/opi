import opi
from opi.plugins import BasePlugin
import subprocess

class Teamviewer(BasePlugin):
	main_query = "teamviewer"
	description = "Teamviewer remote access"
	queries = ('teamviewer')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install Teamviewer from Teamviewer repository?", 'y'):
			return

		opi.add_repo(
			filename = 'teamviewer',
			name = 'Teamviewer',
			url = 'https://linux.teamviewer.com/yum/stable/main/binary-$basearch/',
			gpgkey = 'https://linux.teamviewer.com/pubkey/currentkey.asc'
		)

		subprocess.call(['sudo', 'zypper', 'in', 'teamviewer-suse'])
		# Teamviewer packages its own repo file so our repo file got saved as rpmorig
		subprocess.call(['sudo', 'rm', '-f', '/etc/zypp/repos.d/teamviewer.repo.rpmorig'])
		opi.ask_keep_repo('teamviewer')
