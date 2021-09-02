import opi
from opi.plugins import BasePlugin
import subprocess

class YandexDisk(BasePlugin):
	main_query = "yandex-disk"
	description = "Yandex.Disk keeps your files with you at all times. You can access photos, videos, and documents on Disk from any where in the world where there's internet."
	queries = ('yandex-disk')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install yandex-disk from yandex-disk repository?", 'y'):
			return

		opi.add_repo(
			filename = 'yandex-disk',
			name = 'yandex-disk',
			url = 'https://repo.yandex.ru/yandex-disk/rpm/stable/$basearch/',
			gpgkey = 'https://repo.yandex.ru/yandex-disk/YANDEX-DISK-KEY.GPG'
		)
