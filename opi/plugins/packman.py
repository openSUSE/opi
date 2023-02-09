import opi
from opi.plugins import BasePlugin

class PackmanCodecsPlugin(BasePlugin):
	main_query = "codecs"
	description = "Media Codecs from Packman and official repo"
	queries = ['packman', 'codecs']

	@classmethod
	def run(cls, query):
		# Install Packman Codecs
		if not opi.ask_yes_or_no("Do you want to install codecs from Packman repository?", 'y'):
			return

		opi.add_packman_repo(dup=True)
		packman_packages = [
			'ffmpeg',
			'libavcodec-full',
			'vlc-codecs',
			'gstreamer-plugins-bad-codecs',
			'gstreamer-plugins-ugly-codecs',
			'gstreamer-plugins-libav',
		]
		if opi.get_version() != '15.4':
			packman_packages.append('pipewire-aptx')
		opi.install_packman_packages(packman_packages)

		opi.install_packages([
			'gstreamer-plugins-good',
			'gstreamer-plugins-good-extra',
			'gstreamer-plugins-bad',
			'gstreamer-plugins-ugly',
		])

		if not opi.ask_yes_or_no("Do you want to install openh264 codecs from openSUSE openh264 repository?", 'y'):
			return
		opi.add_openh264_repo(dup=True)

		opi.install_packages([
			'gstreamer-1.20-plugin-openh264',
			'mozilla-openh264',
		])
