import opi
from opi.plugins import BasePlugin

class Jami(BasePlugin):
	main_query = "jami"
	description = "Jami p2p messenger."
	queries = ['jami-qt', 'jami-gnome', 'jami-daemon']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install jami from jami repository?", 'y'):
			return

		print("Which version do you want to install?")
		option = opi.ask_for_option(options=[
			Jami.main_query,
			'jami-qt',
			'jami-gnome',
			'jami-daemon',
		])

		print("You have chosen %s", option)

		if opi.get_version() == '15.4':
			repourl = 'https://dl.jami.net/nightly/opensuse-leap_15.4/'
		elif opi.get_version() == '15.3':
			repourl = 'https://dl.jami.net/nightly/opensuse-leap_15.3/'
		elif opi.get_version() == 'tumbleweed':
			repourl = 'https://dl.jami.net/nightly/opensuse-tumbleweed/'
		else:
			print("Distribution version detection error")

		opi.add_repo(
			filename = Jami.main_query,
			name = option,
			url = repourl,
			gpgkey = 'https://dl.jami.net/jami.pub.key',
			gpgcheck = False
		)

		opi.install_packages([option])
		opi.ask_keep_repo(option)
