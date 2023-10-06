import opi
from opi.plugins import BasePlugin

class YandexBrowser(BasePlugin):
	main_query = 'yandex-browser'
	description = 'Yandex web browser'
	queries = ['yandex-browser-stable', 'yandex-browser-beta', 'yandex-browser']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no('Do you want to install yandex-browser from yandex-browser repository?'):
			return

		print('Which version do you want to install?')
		option = opi.ask_for_option(options=[
			'yandex-browser-stable',
			'yandex-browser-beta',
		])
		if not option:
			return

		release = option.split('-')[-1]
		print('You have chosen', release)

		opi.add_repo(
			filename = option,
			name = option,
			url = f'https://repo.yandex.ru/yandex-browser/rpm/{release}/$basearch/',
			gpgkey = 'https://repo.yandex.ru/yandex-browser/YANDEX-BROWSER-KEY.GPG',
			gpgcheck = False
		)

		opi.install_packages([option])
		opi.ask_keep_repo(option)
