import opi
from opi.plugins import BasePlugin
import subprocess

class SublimeText(BasePlugin):
	main_query = "sublime"
	description = "Editor for code, markup and prose"
	queries = ('sublime', 'sublime-text', 'sublimetext')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install sublime-text from sublime-text repository?", 'y'):
			return

		opi.add_repo(
			filename = 'sublime-text',
			name = 'sublime-text',
			url = 'https://download.sublimetext.com/rpm/stable/x86_64',
			gpgkey = 'https://download.sublimetext.com/sublimehq-rpm-pub.gpg'
		)
