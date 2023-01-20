import opi
from opi.plugins import BasePlugin
import subprocess

class Zoom(BasePlugin):
	main_query = "zoom"
	description = "Zoom Video Conference"
	queries = ['zoom']

	@classmethod
	def run(cls, query):
		if not opi.ask_yes_or_no("Do you want to install Zoom from zoom.us?", 'y'):
			return

		key_url = "https://zoom.us/linux/download/pubkey"
		opi.ask_import_key(key_url)
		opi.install_packages(['https://zoom.us/client/latest/zoom_openSUSE_x86_64.rpm'])
		opi.ask_keep_key(key_url)
