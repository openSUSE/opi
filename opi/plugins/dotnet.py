import opi
from opi.plugins import BasePlugin
import subprocess

class MSDotnet(BasePlugin):
	main_query = "dotnet"
	description = "Microsoft .NET"
	queries = ('dotnet-sdk', 'dotnet')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install .NET from Microsoft repository?", 'y'):
			return

		opi.add_repo(
			filename = 'dotnet',
			name = 'Microsoft .NET',
			url = 'https://packages.microsoft.com/opensuse/15/prod/',
			gpgkey = 'https://packages.microsoft.com/keys/microsoft.asc'
		)

		subprocess.call(['sudo', 'zypper', 'in', 'dotnet-sdk-5.0'])
		opi.ask_keep_repo('dotnet')
