import opi
from opi.plugins import BasePlugin
import subprocess

class MSTeams(BasePlugin):
	main_query = "msteams"
	description = "Microsoft Teams"
	queries = ('microsoftteams', 'msteams', 'teams')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install Teams from Microsoft repository?", 'y'):
			return

		opi.add_repo(
			filename = 'teams',
			name = 'MS Teams',
			url = 'https://packages.microsoft.com/yumrepos/ms-teams',
			gpgkey = 'https://packages.microsoft.com/keys/microsoft.asc'
		)

		subprocess.call(['sudo', 'zypper', 'in', 'teams'])
		opi.ask_keep_repo('teams')
