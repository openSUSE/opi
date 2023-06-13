import opi
from opi.plugins import BasePlugin

class YandexDisk(BasePlugin):
	main_query = 'yandex-disk'
	description = 'Yandex.Disk cloud storage client'
	queries = ['yandex-disk']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no('Do you want to install yandex-disk from yandex-disk repository?'):
			return

		opi.add_repo(
			filename = 'yandex-disk',
			name = 'yandex-disk',
			url = 'https://repo.yandex.ru/yandex-disk/rpm/stable/$basearch/',
			gpgkey = 'https://repo.yandex.ru/yandex-disk/YANDEX-DISK-KEY.GPG',
			gpgcheck = False
		)

		opi.install_packages(['yandex-disk'])
		opi.ask_keep_repo('yandex-disk')
