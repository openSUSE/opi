import os
import opi
import shutil
from opi.plugins import BasePlugin
from opi import rpmbuild
from opi import snap
from opi import http

class Spotify(BasePlugin):
	main_query = 'spotify'
	description = 'Listen to music for a monthly fee'
	queries = [main_query]

	@classmethod
	def run(cls, query):
		s = snap.get_snap('spotify')
		if not opi.ask_yes_or_no(f"Do you want to install spotify release {s['version']} converted to RPM from snapcraft repo?"):
			return

		binary_path = 'usr/bin/spotify'
		data_path = 'usr/share/spotify'

		rpm = rpmbuild.RPMBuild('spotify', s['version'], cls.description, "x86_64", 
			conflicts = ["spotify-client"],
			requires = [
				"libasound2",
				"libatk-bridge-2_0-0",
				"libatomic1",
				"libcurl4",
				"libgbm1",
				"libglib-2_0-0",
				"libgtk-3-0",
				"mozilla-nss",
				"libopenssl1_1",
				"libxshmfence1",
				"libXss1",
				"libXtst6",
				"xdg-utils",
				"libayatana-appindicator3-1",
			],
			autoreq = False,
			recommends = [
				"libavcodec.so",
				"libavformat.so",
			],
			suggests = ["libnotify4"],
			files = [
				f"/{binary_path}",
				f"/{data_path}"
			]
		)

		snap_path = os.path.join(rpm.tmpdir.name, 'spotify.snap')
		snap_path_extracted = os.path.join(rpm.tmpdir.name, 'spotify')
		http.download_file(s['url'], snap_path)
		snap.extract_snap(snap_path, snap_path_extracted)

		binary_abspath = os.path.join(rpm.buildroot, binary_path)
		rpmbuild.copy(os.path.join(snap_path_extracted, binary_path), binary_abspath)

		data_abspath = os.path.join(rpm.buildroot, data_path)
		rpmbuild.copy(os.path.join(snap_path_extracted, data_path), data_abspath)

		rpm.add_desktop_file(cmd="spotify %U", icon="/usr/share/spotify/icons/spotify_icon.ico",
		                     Categories="Audio;Music;Player;AudioVideo;",
		                     MimeType="x-scheme-handler/spotify"
		)

		rpm.build()
		opi.install_packages([rpm.rpmfile_path], allow_unsigned=True)
