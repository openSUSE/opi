import opi
from opi.plugins import BasePlugin
import subprocess

class YandexBrowser(BasePlugin):
	main_query = "yandex-browser-beta"
	description = "Yandex web browser"
	queries = ('yandex-browser')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install yandex-disk from yandex-disk repository?", 'y'):
			return

		opi.add_repo(
			filename = 'yandex-browser-beta',
			name = 'yandex-browser-beta',
			url = 'https://repo.yandex.ru/yandex-disk/rpm/beta/$basearch/',
			gpgkey = 'https://repo.yandex.ru/yandex-browser/YANDEX-BROWSER-KEY.GPG',
			gpgcheck = False
		)

		opi.install_packages(['yandex-browser-beta'])
		opi.ask_keep_repo('yandex-browser-beta')
