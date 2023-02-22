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
			'jami-qt',
			'jami-gnome',
			'jami-daemon',
		])

		# release = option.split('-')[2]
		print("You have chosen %s", option)

		opi.add_repo(
			filename = option,
			name = option,
			url = 'https://dl.jami.net/nightly/opensuse-tumbleweed',
			gpgkey = 'https://dl.jami.net/jami.pub.key',
			gpgcheck = False
		)

		opi.install_packages([option])
		opi.ask_keep_repo(option)
