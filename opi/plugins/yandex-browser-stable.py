import opi
from opi.plugins import BasePlugin
import subprocess

class YandexBrowser(BasePlugin):
	main_query = "yandex-browser-stable"
	description = "Yandex web browser"
	queries = ('yandex-browser')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install yandex-disk from yandex-disk repository?", 'y'):
			return

		opi.add_repo(
			filename = 'yandex-browser-stable',
			name = 'yandex-browser-stable',
			url = 'https://repo.yandex.ru/yandex-disk/rpm/stable/$basearch/',
			gpgkey = 'https://repo.yandex.ru/yandex-browser/YANDEX-BROWSER-KEY.GPG',
			gpgcheck = False
		)

		opi.install_packages(['yandex-browser-stable'])
		opi.ask_keep_repo('yandex-browser-stable')
