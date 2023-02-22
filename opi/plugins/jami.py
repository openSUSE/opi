import opi
from opi.plugins import BasePlugin

class Jami(BasePlugin):
	main_query = "jami"
	description = "Jami p2p messenger."
	queries = [main_query, 'jami-qt', 'jami-gnome', 'jami-daemon']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install jami from jami repository?", 'y'):
			return

		print("Which version do you want to install?")
		option = opi.ask_for_option(options=[
			'jami',
			'jami-qt',
			'jami-gnome',
			'jami-daemon',
		])

		print("You have chosen %s", option)

		if opi.get_distribution().startswith('openSUSE:Leap'):
			repourl = 'https://dl.jami.net/nightly/opensuse-leap_%s/' % opi.get_version()
		else:
			repourl = 'https://dl.jami.net/nightly/opensuse-tumbleweed/'

		opi.add_repo(
			filename = 'jami'
			name = 'jami',
			url = repourl,
			gpgkey = 'https://dl.jami.net/jami.pub.key',
			gpgcheck = False
		)

		opi.install_packages([option])
		opi.ask_keep_repo('jami')
