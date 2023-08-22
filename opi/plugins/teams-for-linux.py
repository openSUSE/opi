import opi
from opi.plugins import BasePlugin

class TeamsForLinux(BasePlugin):
	main_query = 'teams-for-linux'
	description = 'Unofficial Microsoft Teams for Linux client'
	queries = ['teams-for-linux','teams']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no('Do you want to install teams-for-linux from teamsforlinux.de repository?'):
			return

		opi.add_repo(
			filename = 'teams-for-linux',
			name = 'Unofficial Teams for Linux',
			url = 'https://repo.teamsforlinux.de/rpm/',
			gpgkey = 'https://repo.teamsforlinux.de/teams-for-linux.asc'
		)

		opi.install_packages(['teams-for-linux'])
		opi.ask_keep_repo('teams-for-linux')
