import opi
from opi.plugins import BasePlugin

class MSDotnet(BasePlugin):
	main_query = 'dotnet'
	description = 'Microsoft .NET framework'
	queries = ['dotnet-sdk', 'dotnet']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no('Do you want to install .NET from Microsoft repository?'):
			return

		opi.add_repo(
			filename = 'dotnet',
			name = 'Microsoft .NET',
			url = 'https://packages.microsoft.com/opensuse/15/prod/',
			gpgkey = 'https://packages.microsoft.com/keys/microsoft.asc'
		)

		opi.install_packages(['dotnet-sdk-9.0'])
		opi.ask_keep_repo('dotnet')
