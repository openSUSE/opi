import os
import opi
from opi.plugins import BasePlugin
from opi.state import global_state
from opi import github
from opi import http
from opi import rpmbuild
from opi import deb

class LocalSend(BasePlugin):
	main_query = 'localsend'
	description = 'Share files to nearby devices'
	queries = [main_query]

	@classmethod
	def run(cls, query):
		latest_release = github.get_latest_release('localsend', 'localsend')
		if not latest_release:
			print(f'No release found for LocalSend')
			return

		match_filename_suffix = f'{opi.get_cpu_arch().replace("aarch64", "arm-64").replace("_", "-")}.deb'
		asset = github.get_release_asset(latest_release, filters=[lambda a: a['name'].endswith(match_filename_suffix)])
		if not asset:
			print(f"No DEB asset found for LocalSend release {latest_release['tag_name']}")
			return
		if global_state.arg_verbose_mode:
			print(f"Found: {asset['url']}")
		if not opi.ask_yes_or_no(f"Do you want to install LocalSend DEB release {latest_release['tag_name']} converted to RPM from LocalSend github repo?"):
			return

		binary_path = 'usr/bin/localsend'
		data_path = 'usr/share/localsend_app'

		rpm = rpmbuild.RPMBuild('localsend', latest_release['tag_name'], cls.description, opi.get_cpu_arch(), 
			files = [
				f"/{binary_path}",
				f"/{data_path}"
			]
		)

		deb_path = os.path.join(rpm.tmpdir.name, 'localsend.deb')
		deb_path_extracted = os.path.join(rpm.tmpdir.name, 'localsend')
		http.download_file(asset['url'], deb_path)
		deb.extract_deb(deb_path, deb_path_extracted)

		os.makedirs(os.path.join(rpm.buildroot, os.path.dirname(binary_path)), exist_ok=True)
		os.symlink("../share/localsend_app/localsend_app", os.path.join(rpm.buildroot, binary_path))

		rpmbuild.copy(os.path.join(deb_path_extracted, data_path), os.path.join(rpm.buildroot, data_path))

		rpm.add_desktop_file(cmd="localsend %U", icon="/usr/share/localsend_app/data/flutter_assets/assets/img/logo-256.png",
		                     Categories="GTK;FileTransfer;Utility;",
		                     Keywords="Sharing;LAN;Files;",
		                     StartupNotify="true"
		)

		rpm.build()
		opi.install_packages([rpm.rpmfile_path], allow_unsigned=True)
