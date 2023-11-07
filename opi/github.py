import requests
import opi

def http_get_json(url):
	r = requests.get(url)
	r.raise_for_status()
	return r.json()

def get_releases(org, repo, filter_prereleases=True):
	releases = http_get_json(f'https://api.github.com/repos/{org}/{repo}/releases')
	if filter_prereleases:
		releases = [release for release in releases if not release['prerelease']]
	return releases

def get_release_assets(release):
	return [{'name': a['name'], 'url': a['browser_download_url']} for a in http_get_json(release['assets_url'])]

def install_rpm_release(org, repo, allow_unsigned=False):
	releases = get_releases(org, repo)
	if not releases:
		print(f'No release found for {org}/{repo}')
		return
	latest_release = releases[0]
	if not opi.ask_yes_or_no(f"Do you want to install {repo} release {latest_release['tag_name']} RPM from {org} github repo?"):
		return
	assets = get_release_assets(latest_release)
	assets = [a for a in assets if a['name'].endswith('.rpm')]
	if not assets:
		print(f"No RPM asset found for {org}/{repo} release {latest_release['tag_name']}")
		return
	rpm_url = assets[0]['url']
	opi.install_packages([rpm_url], allow_unsigned=allow_unsigned)
