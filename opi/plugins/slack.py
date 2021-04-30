import opi
from opi.plugins import BasePlugin
import subprocess

class Slack(BasePlugin):
	main_query = "slack"
	description = "Slack messenger"
	queries = ('slack')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install slack from the slack repository?", 'y'):
			return

		opi.add_repo(
			filename = 'slack',
			name = 'slack',
			url = 'https://packagecloud.io/slacktechnologies/slack/fedora/21/$basearch',
			gpgkey = 'https://packagecloud.io/slacktechnologies/slack/gpgkey'
		)

		# tell slack cron not to mess with our repos
		subprocess.call(['sudo', 'rm', '-f', '/etc/default/slack'])
		subprocess.call(['sudo', 'touch', '/etc/default/slack'])

		opi.install_packages(['slack'])
		opi.ask_keep_repo('slack')
