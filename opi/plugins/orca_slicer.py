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
		releases = github.get_releases(org, repo)
		releases = [r for r in releases if not 'beta' in r['tag_name']]
		if not releases:
			print(f'No release found for {org}/{repo}')
			return
		latest_release = releases[0]
		if not opi.ask_yes_or_no(f"Do you want to install {repo} release {latest_release['tag_name']} from {org} github repo?"):
			return
		version = latest_release['tag_name'].lstrip('v')
		assets = github.get_release_assets(latest_release)
		assets = [a for a in assets if a['name'].endswith('.AppImage')]
		if not assets:
			print(f"No asset found for {org}/{repo} release {latest_release['tag_name']}")
			return
		url = assets[0]['url']

		binary_path = 'usr/bin/OrcaSlicer'
		icon_path = 'usr/share/pixmaps/OrcaSlicer.svg'

		rpm = rpmbuild.RPMBuild('OrcaSlicer', version, cls.description, "x86_64", [
			f"/{binary_path}",
			f"/{icon_path}"
		])

		binary_abspath = os.path.join(rpm.src_root_dir, binary_path)
		http.download_file(url, binary_abspath)
		os.chmod(binary_abspath, 0o755)

		icon_abspath = os.path.join(rpm.src_root_dir, icon_path)
		icon_url = "https://raw.githubusercontent.com/SoftFever/OrcaSlicer/2d849f/resources/images/OrcaSlicer.svg"
		http.download_file(icon_url, icon_abspath)

		rpm.add_desktop_file(cmd="OrcaSlicer", icon=f"/{icon_path}")

		rpm.build()

		opi.install_packages([rpm.rpmfile_path], allow_unsigned=True)
