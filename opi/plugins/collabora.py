import opi
from opi.plugins import BasePlugin

class collabora(BasePlugin):
	main_query = 'collabora'
	description = 'Collabora desktop office'
	queries = ['collabora', 'collaboraoffice', 'collaboraoffice-desktop']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no('Do you want to install collaboraoffice-desktop from collaboraoffice repository?'):
			return

		opi.add_repo(
			filename = 'collabora-office',
			name = 'Collabora Office 24.04 Snapshot',
			url = 'https://www.collaboraoffice.com/downloads/Collabora-Office-24-Snapshot/Linux/yum',
			gpgkey = 'https://www.collaboraoffice.com/downloads/Collabora-Office-24-Snapshot/Linux/yum/repodata/repomd.xml.key',
			gpgcheck = True
		)

		opi.install_packages(['collaboraoffice-desktop'])
		opi.ask_keep_repo('Collabora Office 24.04 Snapshot')
