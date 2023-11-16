import os
import opi
from opi.plugins import BasePlugin
from opi import github
from opi import rpmbuild
from opi import http

class OrcaSlicer(BasePlugin):
	main_query = 'orcaslicer'
	description = 'Slicer and controller for Bambu and other 3D printers'
	queries = [main_query, 'orca-slicer', 'OrcaSlicer']

	@classmethod
	def run(cls, query):
		org = 'SoftFever'
		repo = 'OrcaSlicer'
		latest_release = github.get_latest_release(org, repo)
		if not latest_release:
			print(f'No release found for {org}/{repo}')
			return
		version = latest_release['tag_name'].lstrip('v').replace('-', '_')
		if not opi.ask_yes_or_no(f"Do you want to install {repo} release {version} from {org} github repo?"):
			return
		asset = github.get_release_asset(latest_release, filters=[lambda a: a['name'].endswith('.AppImage')])
		if not asset:
			print(f"No asset found for {org}/{repo} release {version}")
			return
		url = asset['url']

		binary_path = 'usr/bin/OrcaSlicer'
		icon_path = 'usr/share/pixmaps/OrcaSlicer.svg'

		rpm = rpmbuild.RPMBuild('OrcaSlicer', version, cls.description, "x86_64", files=[
			f"/{binary_path}",
			f"/{icon_path}"
		])

		binary_abspath = os.path.join(rpm.buildroot, binary_path)
		http.download_file(url, binary_abspath)
		os.chmod(binary_abspath, 0o755)

		icon_abspath = os.path.join(rpm.buildroot, icon_path)
		icon_url = "https://raw.githubusercontent.com/SoftFever/OrcaSlicer/2d849f/resources/images/OrcaSlicer.svg"
		http.download_file(icon_url, icon_abspath)

		rpm.add_desktop_file(cmd="OrcaSlicer", icon=f"/{icon_path}")

		rpm.build()

		opi.install_packages([rpm.rpmfile_path], allow_unsigned=True)
