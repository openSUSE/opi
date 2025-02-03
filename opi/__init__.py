import os
import sys
import subprocess
import re
import tempfile
import configparser
from functools import cmp_to_key
from collections import defaultdict

import requests
import lxml.etree
import rpm

from termcolor import colored

from opi.backends import get_backend, BackendConstants
from opi import pager
from opi import config
from opi.state import global_state

OBS_APIROOT = {
	'openSUSE': 'https://api.opensuse.org',
	'Packman': 'https://pmbs.links2linux.de'
}
PROXY_URL = 'https://opi-proxy.opensuse.org/'

REPO_DIR = '/etc/zypp/repos.d/'

##################
### Exceptions ###
##################

class NoOptionSelected(Exception):
	pass

class HTTPError(Exception):
	pass

###################
### System Info ###
###################

cpu_arch = None
def get_cpu_arch():
	global cpu_arch
	if not cpu_arch:
		cpu_arch = os.uname().machine
		if re.match(r'^i.86$', cpu_arch):
			cpu_arch = 'i586'
	return cpu_arch

os_release = {}
def get_os_release():
	global os_release
	if not os_release:
		with open('/etc/os-release') as f:
			for line in f.readlines():
				line = line.strip()
				if line.startswith('#') or '=' not in line:
					continue
				key, value = line.split('=', 1)
				key = key.strip()
				value = value.strip()
				if '"' in value:
					value = value.split('"', 1)[1].split('"', 1)[0]
				os_release[key] = value
	return os_release

def get_distribution(prefix=False, use_releasever_variable=False):
	os_release = get_os_release()
	name = os_release['NAME']
	version = os_release.get('VERSION') # VERSION is not set for TW
	if version:
		# strip prerelease suffix (eg. ' Alpha')
		version = version.split(' ', 1)[0]
	if name in ('openSUSE Tumbleweed', 'openSUSE MicroOS'):
		project = 'openSUSE:Factory'
	elif name in ('openSUSE Tumbleweed-Slowroll', 'openSUSE MicroOS-Slowroll'):
		project = 'openSUSE:Slowroll'
	elif name == 'openSUSE Leap':
		if use_releasever_variable:
			project = 'openSUSE:Leap:$releasever'
		else:
			project = 'openSUSE:Leap:' + version
	elif name == 'openSUSE Leap Micro':
		# Leap Micro major version seems to be 10 lower than Leap the version it is based on
		if use_releasever_variable:
			project = 'openSUSE:Leap:1$releasever'
		else:
			project = 'openSUSE:Leap:1' + version
	elif name.startswith('SLE'):
		project = 'SLE' + version
	if prefix:
		project = 'openSUSE.org:' + project
	return project

def get_version() -> str:
	os_release = get_os_release()
	version = os_release.get('VERSION') # VERSION is not set for TW
	return version

def expand_vars(s: str) -> str:
	s = s.replace('${releasever}', get_version() or '${releasever}')
	s = s.replace('$releasever', get_version() or '$releasever')
	s = s.replace('${basearch}', get_cpu_arch() or '${basearch}')
	s = s.replace('$basearch', get_cpu_arch() or '$basearch')
	return s


###############
### PACKMAN ###
###############

def add_packman_repo(dup=False):
	repos_by_alias = {repo.alias: repo for repo in get_repos()}
	if 'packman' in repos_by_alias:
		print("Installing from existing packman repo")
	else:
		print("Adding packman repo")
		packman_mirrors = {
			"ftp.fau.de                 - University of Erlangen, Germany  -  1h sync": "https://ftp.fau.de/packman",
			"ftp.halifax.rwth-aachen.de - University of Aachen, Germany    -  1h sync": "https://ftp.halifax.rwth-aachen.de/packman",
			"ftp.gwdg.de                - University of Göttingen, Germany -  4h sync": "https://ftp.gwdg.de/pub/linux/misc/packman",
			"mirror.karneval.cz         - TES Media, Czech Republic        -  1h sync": "https://mirror.karneval.cz/pub/linux/packman",
			"mirrors.aliyun.com         - Alibaba Cloud, China             - 24h sync": "https://mirrors.aliyun.com/packman",
		}
		mirror = ask_for_option(list(packman_mirrors.keys()), 'Pick a mirror near your location (0 to quit):')
		mirror = packman_mirrors[mirror]

		project = get_distribution(use_releasever_variable=config.get_key_from_config('use_releasever_var'))
		project = project.replace(':', '_')
		project = project.replace('Factory', 'Tumbleweed')
		add_repo(
			filename = 'packman',
			name = 'Packman',
			url = f'{mirror}/suse/{project}/',
			gpgkey = f'https://ftp.fau.de/packman/suse/{project}/repodata/repomd.xml.key', # always fetch gpgkey from FAU server
			auto_refresh = config.get_key_from_config('new_repo_auto_refresh'),
			priority = 70
		)

	if dup:
		dist_upgrade(from_repo='packman', allow_downgrade=True, allow_vendor_change=True)

def add_openh264_repo(dup=False):
	project = get_os_release()['NAME']
	project = project.replace('-Slowroll', '')
	project = project.replace('openSUSE MicroOS', 'openSUSE Tumbleweed')
	project = project.replace('openSUSE Leap Micro', 'openSUSE Leap')
	project = project.replace(':', '_').replace(' ', '_')

	url = f'http://codecs.opensuse.org/openh264/{project}/'
	existing_repo = get_enabled_repo_by_url(url)
	if existing_repo:
		print(f"Installing from existing repo '{existing_repo.name}'")
		repo = existing_repo.alias
	else:
		repo = 'openh264'
		print(f"Adding repo '{repo}'")
		add_repo(
			filename = repo,
			name = repo,
			url = url,
			gpgkey = f"{url.replace('http://', 'https://')}repodata/repomd.xml.key",
			auto_refresh = config.get_key_from_config('new_repo_auto_refresh'),
			priority = 70
		)

	if dup:
		dist_upgrade(from_repo=repo, allow_downgrade=True, allow_vendor_change=True)

def install_packman_packages(packages, **kwargs):
	install_packages(packages, from_repo='packman', **kwargs)


################
### ZYPP/DNF ###
################

class Repository:
	def __init__(self, alias: str, name: str, url: str, auto_refresh: bool, gpgkey: str = None, filename: str = None):
		self.alias = alias
		self.name = name
		self.url = url
		self.auto_refresh = auto_refresh
		self.gpgkey = gpgkey
		self.filename = filename or alias

	def name_expanded(self):
		""" Return name with all supported vars expanded """
		return expand_vars(self.name)

	def url_expanded(self):
		""" Return url with all supported vars expanded """
		return expand_vars(self.url)

def search_local_repos(package):
	"""
		Search local default repos
	"""
	search_results = defaultdict(list)
	try:
		zc = tempfile.NamedTemporaryFile('w')
		zc.file.write(f'[main]\nshowAlias = true\n')
		zc.file.flush()
		sr = subprocess.check_output(['zypper', '-ntc', zc.name, '--no-refresh', 'se', '-sx', '-tpackage', package], env={'LANG': 'c'}).decode()
		for line in re.split(r'-\+-+\n', sr, re.MULTILINE)[1].strip().split('\n'):
			version, arch, repo_alias = [s.strip() for s in line.split('|')[3:]]
			version, release = version.split('-')
			if arch not in (get_cpu_arch(), 'noarch'):
				continue
			if repo_alias == '(System Packages)':
				continue
			search_results[repo_alias].append({'version': version, 'release': release, 'arch': arch})
	except subprocess.CalledProcessError as e:
		if e.returncode != 104:
			# 104 ZYPPER_EXIT_INF_CAP_NOT_FOUND is returned if there are no results
			raise # TODO: don't exit program, use exception that will be handled in repo_query except block

	repos_by_alias = {repo.alias: repo for repo in get_repos()}
	local_installables = []
	for repo_alias, installables in search_results.items():
		# get the newest package for each repo
		try:
			installables.sort(key=lambda p: cmp_to_key(rpm.labelCompare)("%(version)s-%(release)s" % p))
		except TypeError:
			# rpm 4.14 needs a tuple of (epoch, version, release) - rpm 4.18 can handle a string
			installables.sort(key=lambda p: cmp_to_key(rpm.labelCompare)(['1', p['version'], p['release']]))
		installable = installables[-1]

		installable['repository'] = repos_by_alias[repo_alias]
		installable['name'] = package
		# filter out OBS/Packman repos as they are already searched via OBS/Packman API
		if 'download.opensuse.org/repositories' in installable['repository'].url:
			continue
		if installable['repository'].filename == 'packman':
			continue
		local_installables.append(LocalPackage(**installable))
	return local_installables

def url_normalize(url):
	return expand_vars(re.sub(r'^https?', '', url).rstrip('/'))

def get_repos():
	for repo_file in os.listdir(REPO_DIR):
		if not repo_file.endswith('.repo'):
			continue
		try:
			cp = configparser.ConfigParser()
			cp.read(os.path.join(REPO_DIR, repo_file))
			for alias in cp.sections():
				if not bool(int(cp.get(alias, 'enabled'))):
					continue
				repo = {
					'alias': alias,
					'filename': re.sub(r'\.repo$', '', repo_file),
					'name': cp[alias].get('name', alias),
					'url': cp[alias].get('baseurl'),
					'auto_refresh': bool(int(cp[alias].get('autorefresh', '0'))),
				}
				if cp.has_option(alias, 'gpgkey'):
					repo['gpgkey'] = cp[alias].get('gpgkey')
				yield Repository(**repo)
		except Exception as e:
			print(f"Error parsing '{repo_file}': {e}")

def get_enabled_repo_by_url(url):
	for repo in get_repos():
		if url_normalize(repo.url) == url_normalize(url):
			return repo

def add_repo(filename, name, url, enabled=True, gpgcheck=True, gpgkey=None, repo_type='rpm-md', auto_import_keys=False, auto_refresh=False, priority=None):
	tf = tempfile.NamedTemporaryFile('w')
	tf.file.write(f'[{filename}]\n')
	tf.file.write(f'name={name}\n')
	tf.file.write(f'baseurl={url}\n')
	tf.file.write(f'enabled={enabled:d}\n')
	tf.file.write(f'type={repo_type}\n')
	tf.file.write(f'gpgcheck={gpgcheck:d}\n')
	if gpgkey:
		ask_import_key(gpgkey)
		tf.file.write(f'gpgkey={gpgkey}\n')
	if auto_refresh:
		tf.file.write('autorefresh=1\n')
	if priority:
		tf.file.write(f'priority={priority}\n')
	tf.file.flush()
	subprocess.call(['sudo', 'cp', tf.name, os.path.join(REPO_DIR, f'{filename}.repo')])
	subprocess.call(['sudo', 'chmod', '644', os.path.join(REPO_DIR, f'{filename}.repo')])
	tf.file.close()
	refresh_repos(auto_import_keys=auto_import_keys)

def refresh_repos(repo_alias=None, auto_import_keys=False):
	refresh_cmd = []
	if get_backend() == BackendConstants.zypp:
		refresh_cmd = ['sudo', 'zypper']
		if auto_import_keys:
			refresh_cmd.append('--gpg-auto-import-keys')
		refresh_cmd.append('ref')
	elif get_backend() == BackendConstants.dnf:
		refresh_cmd = ['sudo', 'dnf', 'ref']
	if repo_alias:
		refresh_cmd.append(repo_alias)
	subprocess.call(refresh_cmd)

def normalize_key(pem):
	new_lines = []
	for line in pem.split('\n'):
		line = line.strip()
		if not line:
			continue
		if line.lower().startswith('version:'):
			continue
		new_lines.append(line)
	new_lines.insert(1, '')
	return '\n'.join(new_lines)

def split_keys(keys):
	for key in keys.split('-----BEGIN PGP PUBLIC KEY BLOCK-----')[1:]:
		yield '-----BEGIN PGP PUBLIC KEY BLOCK-----' + key

def get_keys_from_rpmdb():
	s = subprocess.check_output(['rpm', '-q', 'gpg-pubkey', '--qf',
	    '%{NAME}-%{VERSION}\n%{PACKAGER}\n%{DESCRIPTION}\nOPI-SPLIT-TOKEN-TO-TELL-KEY-PACKAGES-APART\n'])
	keys = []
	for raw_kpkg in s.decode().strip().split('OPI-SPLIT-TOKEN-TO-TELL-KEY-PACKAGES-APART'):
		raw_kpkg = raw_kpkg.strip()
		if not raw_kpkg:
			continue
		kid, name, pubkey = raw_kpkg.strip().split('\n', 2)
		keys.append({
			'kid': kid,
			'name': name,
			'pubkey': normalize_key(pubkey)
		})
	return keys

def install_packages(packages, **kwargs):
	pkgmgr_action('in', packages, **kwargs)

def dist_upgrade(**kwargs):
	pkgmgr_action('dup', **kwargs)

def pkgmgr_action(action, packages=[], from_repo=None, allow_vendor_change=False, allow_arch_change=False, allow_downgrade=False, allow_name_change=False, allow_unsigned=False):
	if get_backend() == BackendConstants.zypp:
		args = ['sudo', 'zypper']
		if global_state.arg_non_interactive:
			args.append('-n')
		if allow_unsigned:
			args.append('--no-gpg-checks')
		args.append(action)
		if from_repo:
			args.extend(['--from', from_repo])
		if allow_downgrade:
			args.append('--allow-downgrade')
		if allow_arch_change:
			args.append('--allow-arch-change')
		if allow_name_change:
			args.append('--allow-name-change')
		if allow_vendor_change:
			args.append('--allow-vendor-change')
		if action == 'in':
			args.append('--oldpackage')
	elif get_backend() == BackendConstants.dnf:
		args = ['sudo', 'dnf']
		if global_state.arg_non_interactive:
			args.append('-y')
		args.append(action)
		if from_repo:
			args.extend(['--repo', from_repo])
		# allow_downgrade and allow_name_change are default in DNF
		if allow_vendor_change:
			args.append('--setopt=allow_vendor_change=True')
		if allow_unsigned:
			args.append('--nogpgcheck')
	else:
		raise Exception(f"Unknown Backend: {get_backend()}")
	args.extend(packages)
	subprocess.call(args)


###########
### OBS ###
###########

class Installable:
	def __init__(self, name: str, version: str, release: str, arch: str):
		self.name = name # e.g. MozillaFirefox
		self.version = version # e.g. 1.2.3
		self.release = release # e.g. 150500.1.1
		self.arch = arch # e.g. x86_64, aarch64 or noarch

	def install(self):
		raise NotImplemented()

	def name_with_arch(self):
		return f'{self.name}.{self.arch}'

	def _install_from_existing_repo(self, repo: Repository):
		# Install from existing repos (don't add a repo)
		print(f"Installing from existing repo '{repo.name_expanded()}'")
		# ensure that this repo is up to date if no auto_refresh is configured
		if not repo.auto_refresh:
			refresh_repos(repo.alias)
		install_packages([self.name_with_arch()], from_repo=repo.alias)

class OBSPackage(Installable):
	""" Package returned from OBS API """
	def __init__(self,
	             name: str, version: str, release: str, arch: str,
	             package: str, project: str, repository: str, obs_instance: str):
		super().__init__(name, version, release, arch)
		self.package = package # same as name unless this is a subpackage (then package is name of parent)
		self.project = project # e.g. devel:languages:perl
		self.repository = repository # e.g. openSUSE_Tumbleweed
		self.obs_instance = obs_instance # openSUSE or Packman

	def install(self):
		if self.obs_instance == 'Packman':
			# Install from Packman Repo
			add_packman_repo()
			install_packman_packages([self.name_with_arch()])
			return

		repo_alias = self.project.replace(':', '_')
		project_path = self.project.replace(':', ':/')
		repository = self.repository
		if config.get_key_from_config('use_releasever_var'):
			version = get_version()
			if version:
				# version is None on tw
				repository = repository.replace(version, '$releasever')
		url = f'https://download.opensuse.org/repositories/{project_path}/{repository}/'
		gpgkey = url + 'repodata/repomd.xml.key'
		existing_repo = get_enabled_repo_by_url(url)

		if existing_repo:
			self._install_from_existing_repo(existing_repo)
		else:
			print(f"Adding repo '{self.project}'")
			add_repo(
				filename = repo_alias,
				name = self.project,
				url = url,
				gpgkey = gpgkey,
				gpgcheck = True,
				auto_refresh = config.get_key_from_config('new_repo_auto_refresh')
			)
			install_packages([self.name_with_arch()], from_repo=repo_alias,
				allow_downgrade=True,
				allow_arch_change=True,
				allow_name_change=True,
				allow_vendor_change=True
			)
			ask_keep_repo(repo_alias)

	def weight(self):
		weight = 0

		dash_count = self.name.count('-')
		weight += 1e5 * (0.5 ** dash_count)

		weight -= 1e4 * len(self.name)

		if self.is_from_official_project():
			weight += 2e3
		elif not self.is_from_personal_project():
			weight += 1e3

		if self.name == self.package:
			# this rpm is the main or only subpackage
			weight += 1e2

		if not (get_cpu_arch() == 'x86_64' and self.arch == 'i586'):
			weight += 1e1

		if self.repository.startswith('openSUSE_Tumbleweed'):
			weight += 2
		elif self.repository.startswith('openSUSE_Factory'):
			weight += 1
		elif self.repository == 'standard':
			weight += 0

		return weight

	def __lt__(self, other):
		""" Note that we sort from high weight to low weight """
		return self.weight() > other.weight()

	def is_from_official_project(self):
		return self.project.startswith('openSUSE:')

	def is_from_personal_project(self):
		return self.project.startswith('home:') or self.project.startswith('isv:')

class LocalPackage(Installable):
	""" Package found in local repo (metadata) cache """
	def __init__(self, name: str, version: str, release: str, arch: str, repository: Repository):
		super().__init__(name, version, release, arch)
		self.repository = repository

	def install(self):
		self._install_from_existing_repo(self.repository)

def search_published_packages(obs_instance, query):
	distribution = get_distribution(prefix=(obs_instance != 'openSUSE'))
	endpoint = '/search/published/binary/id'
	url = OBS_APIROOT[obs_instance] + endpoint
	if isinstance(query, list):
		xquery = "'" + "', '".join(query) + "'"
	else:
		xquery = f"'{query}'"
	xpath = f"contains-ic(@name, {xquery}) and path/project='{distribution}'"
	url = requests.Request('GET', url, params={'match': xpath, 'limit': 0}).prepare().url
	try:
		r = requests.get(PROXY_URL, params={'obs_api_link': url, 'obs_instance': obs_instance})
		r.raise_for_status()

		dom = lxml.etree.fromstring(r.text)
		packages = []
		for binary in dom.xpath('/collection/binary'):
			binary_data = {k: v for k, v in binary.items()}
			binary_data['obs_instance'] = obs_instance

			del binary_data['filename']
			del binary_data['filepath']
			del binary_data['baseproject']
			del binary_data['type']
			for k in ('name', 'project', 'repository', 'version', 'release', 'arch'):
				assert k in binary_data, f"Key '{k}' missing"

			# Filter out ghost binary
			# (package has been deleted, but binary still exists)
			if not binary_data.get('package'):
				continue

			package = OBSPackage(**binary_data)

			# Filter out branch projects
			if ':branches:' in package.project:
				continue

			# Filter out Packman personal projects
			if package.obs_instance != 'openSUSE' and package.is_from_personal_project():
				continue

			# Filter out debuginfo, debugsource, devel, buildsymbols, lang and docs packages
			regex = r'-(debuginfo|debugsource|buildsymbols|devel|lang|l10n|trans|doc|docs)(-.+)?$'
			if re.match(regex, package.name):
				continue

			# Filter out source packages
			if package.arch == 'src':
				continue

			# Filter architecture
			cpu_arch = get_cpu_arch()
			if package.arch not in (cpu_arch, 'noarch'):
				continue

			# Filter repo architecture
			if package.repository == 'openSUSE_Factory' and (cpu_arch not in ('x86_64' 'i586')):
				continue
			elif package.repository == 'openSUSE_Factory_ARM' and not cpu_arch.startswith('arm') and not cpu_arch == 'aarch64':
				continue
			elif package.repository == 'openSUSE_Factory_PowerPC' and not cpu_arch.startswith('ppc'):
				continue
			elif package.repository == 'openSUSE_Factory_zSystems' and not cpu_arch.startswith('s390'):
				continue
			elif package.repository == 'openSUSE_Factory_RISCV' and not cpu_arch.startswith('risc'):
				continue

			packages.append(package)

		return packages
	except requests.exceptions.HTTPError as e:
		if e.response.status_code == 413:
			print('Please use different search keywords. Some short keywords cause OBS timeout.')
		else:
			print('HTTPError:', e)
		raise HTTPError()

def get_package_names(packages: list):
	""" return a list of package names but without duplicates """
	names = []
	for pkg in packages:
		name = pkg.name
		if name not in names:
			names.append(name)
	return names

def sort_uniq_packages(packages: list):
	""" sort -u for packages; sort by weight and keep only the one with the best repo """
	packages = sorted(packages)
	new_packages = []
	added_packages = set()
	for package in packages:
		# only select the first package for each name/project combination
		# which will be the one with the highest repo weight
		query = (package.name, package.project)
		if query not in added_packages:
			new_packages.append(package)
			added_packages.add(query)
	return new_packages

########################
### User Interaction ###
########################

def ask_yes_or_no(question, default_answer='y'):
	q = question + ' '
	if default_answer == 'y':
		q += '(Y/n)'
	else:
		q += '(y/N)'
	q += ' '
	if global_state.arg_non_interactive:
		print(q)
		answer = default_answer
	else:
		answer = input(q) or default_answer
	return answer.strip().lower() == 'y'

def ask_for_option(options, question='Pick a number (0 to quit):', option_filter=lambda a: a, disable_pager=False):
	"""
		Ask the user for a number to pick in order to select an option.
		Exit if the number is 0.
		Specify the number with question and the corresponding option will be returned.
		Via option_filter a callback function to format option entries can be supplied,
		but this doesn't work with the pager.
		If needed, a pager will be used, unless disable_pager is True.
	"""

	padding_len = len(str(len(options)))
	i = 1
	numbered_options = []
	terminal_width = os.get_terminal_size().columns - 1 if sys.stdout.isatty() else 0
	for option in options:
		number = f'{i:{padding_len}}. '
		numbered_option = number + option_filter(option)
		if terminal_width and not disable_pager:
			# break too long lines:
			# if pager is disabled this might mean that we get terminal sequences here
			# which might get broken by some spaces and newlines.
			# also too long lines are not fatal outside of the pager
			while len(numbered_option) > terminal_width:
				numbered_options.append(numbered_option[:terminal_width])
				numbered_option = ' ' * len(number) + numbered_option[terminal_width:]
		numbered_options.append(numbered_option)
		i += 1
	if config.get_key_from_config('list_in_reverse'):
		numbered_options.reverse()
	text = '\n'.join(numbered_options)
	if global_state.arg_non_interactive:
		input_string = '1' # default to first option in the list
		print(f"{text}\n{question} {input_string}")
	elif not sys.stdout.isatty() or len(numbered_options) < (os.get_terminal_size().lines - 1) or disable_pager:
		# no pager needed
		print(text)
		input_string = input(question + ' ')
	else:
		input_string = pager.ask_number_with_pager(text, question, start_at_bottom=config.get_key_from_config('list_in_reverse'))

	input_string = input_string.strip() or '0'
	num = int(input_string) if input_string.isdecimal() else -1
	if num == 0:
		raise NoOptionSelected()
	elif not (num >= 1 and num <= len(options)):
		return ask_for_option(options, question, option_filter, disable_pager)
	else:
		return options[num - 1]

def ask_import_key(keyurl):
	keys = requests.get(expand_vars(keyurl)).text
	db_keys = get_keys_from_rpmdb()
	for key in split_keys(keys):
		for line in subprocess.check_output(['gpg', '--quiet', '--show-keys', '--with-colons', '-'], input=key.encode()).decode().strip().split('\n'):
			if line.startswith('uid:'):
				key_info = line.split(':')[9].replace('\\x3a', ':')
			elif line.startswith('pub:'):
				kid = f"gpg-pubkey-{line.split(':')[4][-8:].lower()}"
		if [db_key for db_key in db_keys if normalize_key(key) in normalize_key(db_key['pubkey'])]:
			print(f"Package signing key {kid} ('{key_info}) is already present.")
		else:
			if ask_yes_or_no(f"Import package signing key {kid} ({key_info})"):
				tf = tempfile.NamedTemporaryFile('w')
				tf.file.write(key)
				tf.file.flush()
				subprocess.call(['sudo', 'rpm', '--import', tf.name])
				tf.file.close()

def ask_keep_key(keyurl, repo_alias=None):
	"""
		Ask to remove the key given by url to key file.
		Warns about all repos still using the key except the repo given by repo_alias param.
	"""
	urlkeys = split_keys(requests.get(expand_vars(keyurl)).text)
	urlkeys_normalized = [normalize_key(urlkey) for urlkey in urlkeys]
	db_keys = get_keys_from_rpmdb()
	keys_to_ask_user = [key for key in db_keys if key['pubkey'] in urlkeys_normalized]
	for key in keys_to_ask_user:
		repos_using_this_key = []
		for repo in get_repos():
			if repo_alias and repo.filename == repo_alias:
				continue
			if repo.gpgkey:
				repokey = normalize_key(requests.get(repo.gpgkey).text)
				if repokey == key['pubkey']:
					repos_using_this_key.append(repo)
		if repos_using_this_key:
			default_answer = 'y'
			print('This key is still in use by the following remaining repos - removal is NOT recommended:')
			print(' - ' + '\n - '.join([repo.filename for repo in repos_using_this_key]))
		else:
			default_answer = 'n'
			print('This key is not in use by any remaining repos.')
		print('Keeping the key will allow additional packages signed by this key to be installed in the future without further warning.')
		if not ask_yes_or_no(f"Keep package signing key {key['kid']} ({key['name']})?", default_answer):
			subprocess.call(['sudo', 'rpm', '-e', key['kid']])

def ask_keep_repo(repo_alias):
	if not ask_yes_or_no(f"Do you want to keep the repo '{repo_alias}'?"):
		repo = next((r for r in get_repos() if r.filename == repo_alias))
		if get_backend() == BackendConstants.zypp:
			subprocess.call(['sudo', 'zypper', 'rr', repo_alias])
		if get_backend() == BackendConstants.dnf:
			subprocess.call(['sudo', 'rm', os.path.join(REPO_DIR, f'{repo_alias}.repo')])
		if repo.gpgkey:
			ask_keep_key(repo.gpgkey, repo)

def format_pkg_option(package, table=True):
	if isinstance(package, LocalPackage):
		color = 'green'
		symbol = '+'
	elif package.is_from_official_project():
		color = 'yellow'
		symbol = '-'
	elif package.is_from_personal_project():
		color = 'red'
		symbol = '!'
	else:
		color = 'cyan'
		symbol = '?'

	if isinstance(package, LocalPackage):
		project = package.repository.name_expanded()
	else:
		project = package.project
		if package.obs_instance != 'openSUSE':
			project = f"{package.obs_instance} {project}"

	colored_name = colored(f'{project[:39]} {symbol}', color)

	if table:
		return f"{colored_name:50} | {package.version[:25]:25} | {package.arch}"
	else:
		return f"{colored_name} | {package.version} | {package.arch}"
