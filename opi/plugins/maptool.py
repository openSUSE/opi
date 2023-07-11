import opi
from opi.plugins import BasePlugin

import requests

def http_get_json(url):
	r = requests.get(url)
	r.raise_for_status()
	return r.json()

def install_github_release(org, repo):
	releases = http_get_json(f'https://api.github.com/repos/{org}/{repo}/releases')
	releases = [release for release in releases if not release['prerelease']]
	if not releases:
		print(f'No release found for {org}/{repo}')
		return
	latest_release = releases[0]
	if not opi.ask_yes_or_no(f"Do you want to install {repo} release {latest_release['tag_name']} RPM from {org} github repo?"):
		return
	assets = http_get_json(latest_release['assets_url'])
	rpm_assets = [asset for asset in assets if asset['name'].endswith('.rpm')]
	if not rpm_assets:
		print(f"No RPM asset found for {org}/{repo} release {latest_release['tag_name']}")
		return
	rpm_url = rpm_assets[0]['browser_download_url']
	opi.install_packages([rpm_url])

class MapTool(BasePlugin):
	main_query = 'maptool'
	description = 'Virtual Tabletop for playing roleplaying games'
	queries = ['maptool', 'MapTool']

	@classmethod
	def run(cls, query):
		install_github_release('RPTools', 'maptool')
