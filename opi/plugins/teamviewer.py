import opi
import os
from opi.plugins import BasePlugin
import subprocess

class Teamviewer(BasePlugin):
	main_query = 'teamviewer'
	description = 'TeamViewer remote access'
	queries = ['teamviewer']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no('Do you want to install Teamviewer from Teamviewer repository?'):
			return

		opi.add_repo(
			filename = 'teamviewer',
			name = 'Teamviewer',
			url = 'https://linux.teamviewer.com/yum/stable/main/binary-$basearch/',
			gpgkey = 'https://linux.teamviewer.com/pubkey/currentkey.asc'
		)

		opi.install_packages(['teamviewer-suse'])
		# Teamviewer packages its own repo file so our repo file got saved as rpmorig
		subprocess.call(['sudo', 'rm', '-f', os.path.join(opi.REPO_DIR, 'teamviewer.repo.rpmorig')])
		opi.ask_keep_repo('teamviewer')
