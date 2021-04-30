import opi
from opi.plugins import BasePlugin
import subprocess

class VSCode(BasePlugin):
	main_query = "vscode"
	description = "Microsoft Visual Studio Code"
	queries = ('visualstudiocode', 'vscode', 'vsc')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install VS Code from Microsoft repository?", 'y'):
			return

		opi.add_repo(
			filename = 'vscode',
			name = 'Visual Studio Code',
			url = 'https://packages.microsoft.com/yumrepos/vscode',
			gpgkey = 'https://packages.microsoft.com/keys/microsoft.asc'
		)

		opi.install_packages(['code'])
		opi.ask_keep_repo('vscode')
