import requests
import opi

def http_get_json(url):
	r = requests.get(url)
	r.raise_for_status()
	return r.json()

def get_releases(org, repo, filter_prereleases=True, filters=[]):
	releases = http_get_json(f'https://api.github.com/repos/{org}/{repo}/releases')
	if filter_prereleases:
		releases = [release for release in releases if not release['prerelease']]
	for f in filters:
		releases = [r for r in releases if f(r)]
	return releases

def get_latest_release(org, repo, filter_prereleases=True, filters=[]):
	releases = get_releases(org, repo, filter_prereleases, filters)
	return releases[0] if releases else None

def get_release_assets(release):
	return [{'name': a['name'], 'url': a['browser_download_url']} for a in http_get_json(release['assets_url'])]

def get_release_asset(release, filters=[]):
	assets = get_release_assets(release)
	for f in filters:
		assets = [r for r in assets if f(r)]
	return assets[0] if assets else None

def install_rpm_release(org, repo, filters=[lambda a: a['name'].endswith('.rpm')], allow_unsigned=False):
	latest_release = get_latest_release(org, repo)
	if not latest_release:
		print(f'No release found for {org}/{repo}')
		return
	asset = get_release_asset(latest_release, filters=filters)
	if not asset:
		print(f"No RPM asset found for {org}/{repo} release {latest_release['tag_name']}")
		return
	print(f"Found: {asset['url']}")
	if not opi.ask_yes_or_no(f"Do you want to install {repo} release {latest_release['tag_name']} RPM from {org} github repo?"):
		return
	opi.install_packages([asset['url']], allow_unsigned=allow_unsigned)
