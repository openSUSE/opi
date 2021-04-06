import opi
from opi.plugins import BasePlugin
import subprocess

class Zoom(BasePlugin):
	main_query = "zoom"
	description = "ZOOM Video Conference"
	queries = ('zoom')

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install zoom from zoom.us?", 'y'):
			return

		subprocess.call(['sudo', 'rpm', '--import', 'https://zoom.us/linux/download/pubkey'])
		subprocess.call(['sudo', 'zypper', 'in', 'https://zoom.us/client/latest/zoom_openSUSE_x86_64.rpm'])
