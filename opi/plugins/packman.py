import opi
from opi.plugins import BasePlugin

class PackmanCodecsPlugin(BasePlugin):
	main_query = "codecs"
	description = "Media Codecs from Packman and official repo"
	queries = ['packman', 'codecs']

	@classmethod
	def run(cls, query):
		# Install Packman Codecs
		if not opi.ask_yes_or_no("Do you want to install codecs from Packman repository?"):
			return

		opi.add_packman_repo(dup=True)
		packman_packages = [
			'ffmpeg',
			'libavcodec-full',
			'vlc-codecs',
			'gstreamer-plugins-bad-codecs',
			'gstreamer-plugins-ugly-codecs',
			'gstreamer-plugins-libav',
			'libfdk-aac2',
		]
		if opi.get_version() not in ('15.4', '15.5'):
			packman_packages.append('pipewire-aptx')
			packman_packages.append('ffmpeg>=5')
		opi.install_packman_packages(packman_packages)

		opi.install_packages([
			'gstreamer-plugins-good',
			'gstreamer-plugins-good-extra',
			'gstreamer-plugins-bad',
			'gstreamer-plugins-ugly',
		])

		if not opi.ask_yes_or_no("Do you want to install openh264 codecs from openSUSE openh264 repository?"):
			return
		opi.add_openh264_repo(dup=True)

		openh264_packages = [
			'mozilla-openh264',
		]
		# install something like gstreamer-1.20-plugin-openh264 without actually specifying any version number
		gstreamer_plugin_openh264_pkg = 'libgstopenh264.so()'
		if not (opi.get_cpu_arch() == 'i586' or opi.get_cpu_arch().startswith('armv7')):
			gstreamer_plugin_openh264_pkg += '(64bit)'
		openh264_packages.append(gstreamer_plugin_openh264_pkg)
		opi.install_packages(openh264_packages)
