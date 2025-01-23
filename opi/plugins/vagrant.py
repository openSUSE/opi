import opi
from opi.plugins import BasePlugin

class Vagrant(BasePlugin):
	main_query = 'vagrant'
	description = 'Tool for building and distributing development environments'
	queries = [main_query]

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no('Do you want to install Vagrant from Hashicorp repository?'):
			return

		opi.add_repo(
			filename = 'hashicorp',
			name = 'Hashicorp',
			url = 'https://rpm.releases.hashicorp.com/AmazonLinux/latest/$basearch/stable',
			gpgkey = 'https://rpm.releases.hashicorp.com/gpg'
		)

		opi.install_packages(['vagrant'])
		opi.ask_keep_repo('hashicorp')
