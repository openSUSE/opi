import opi
from opi.plugins import BasePlugin
import subprocess

class VSCodium(BasePlugin):
	main_query = "vscodium"
	description = "Visual Studio Codium"
	queries = ('visualstudiocodium', 'vscodium', 'codium')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install VS Codium from paulcarroty_vscodium repository?", 'y'):
			return

		opi.add_repo(
			filename = 'vscodium',
			name = 'Visual Studio Codium',
			url = 'https://paulcarroty.gitlab.io/vscodium-deb-rpm-repo/rpms',
			gpgkey = 'https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg'
		)

		opi.install_packages(['codium'])
		opi.ask_keep_repo('vscodium')
