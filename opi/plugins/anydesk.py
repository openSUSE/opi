import opi
from opi.plugins import BasePlugin
import subprocess

class Anydesk(BasePlugin):
	main_query = "anydesk"
	description = "AnyDesk remote desktop access"
	queries = ('anydesk')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install anydesk from anydesk repository?", 'y'):
			return

		opi.add_repo(
			filename = 'anydesk',
			name = 'anydesk',
			url = 'http://rpm.anydesk.com/opensuse/$basearch/',
			gpgkey = 'https://keys.anydesk.com/repos/RPM-GPG-KEY'
		)

		opi.install_packages(['anydesk'])
		opi.ask_keep_repo('anydesk')
