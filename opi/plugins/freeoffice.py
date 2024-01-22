import opi
from opi.plugins import BasePlugin

class SoftMakerFreeOffice(BasePlugin):
	main_query = 'freeoffice'
	description = 'Office suite from SoftMaker (See OSS alternative libreoffice)'
	queries = ['freeoffice']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no('Do you want to install FreeOffice from SoftMaker repository?'):
			return

		opi.add_repo(
			filename = 'SoftMaker',
			name = 'SoftMaker',
			url = 'https://shop.softmaker.com/repo/rpm',
			gpgkey = 'https://shop.softmaker.com/repo/linux-repo-public.key'
		)

		opi.install_packages(['softmaker-freeoffice-2021'])
		opi.ask_keep_repo('SoftMaker')
