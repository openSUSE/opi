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

OBS_APIROOT = {
	'openSUSE': 'https://api.opensuse.org',
	'Packman': 'https://pmbs.links2linux.de'
}
PROXY_URL = 'https://opi-proxy.opensuse.org/'

REPO_DIR = '/etc/zypp/repos.d/'


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
	if name == 'openSUSE Tumbleweed' or name == 'openSUSE MicroOS':
		project = 'openSUSE:Factory'
	elif name == 'openSUSE Leap':
		if use_releasever_variable:
			project = 'openSUSE:Leap:$releasever'
		else:
			project = 'openSUSE:Leap:' + version
	elif name.startswith('SLE'):
		project = 'SLE' + version
	if prefix:
		project = 'openSUSE.org:' + project
	return project

def get_version():
	os_release = get_os_release()
	version = os_release.get('VERSION') # VERSION is not set for TW
	return version

###############
### PACKMAN ###
###############

def add_packman_repo(dup=False):
	project = get_distribution(use_releasever_variable=config.get_key_from_config('use_releasever_var'))
	project = project.replace(':', '_')
	project = project.replace('Factory', 'Tumbleweed')

	add_repo(
		filename = 'packman',
		name = 'Packman',
		url = f'https://ftp.gwdg.de/pub/linux/misc/packman/suse/{project}/',
		auto_refresh = True,
		priority = 90
	)

	if dup:
		dist_upgrade(from_repo='packman', allow_downgrade=True, allow_vendor_change=True)

def add_openh264_repo(dup=False):
	project = get_os_release()['NAME']
	project = project.replace(':', '_').replace(' ', '_')

	url = f'http://codecs.opensuse.org/openh264/{project}/'
	existing_repo = get_enabled_repo_by_url(url)
	if existing_repo:
		print(f"Installing from existing repo '{existing_repo['name']}'")
		repo = existing_repo['alias']
	else:
		repo = 'openh264'
		print(f"Adding repo '{repo}'")
		add_repo(
			filename = repo,
			name = repo,
			url = url,
			gpgkey = f"{url.replace('http://', 'https://')}repodata/repomd.xml.key",
			auto_refresh = True,
			priority = 90
		)

	if dup:
		dist_upgrade(from_repo=repo, allow_downgrade=True, allow_vendor_change=True)

def install_packman_packages(packages, **kwargs):
	install_packages(packages, from_repo='packman', **kwargs)


################
### ZYPP/DNF ###
################

def search_local_repos(package):
	"""
		Search local default repos
	"""
	search_results = defaultdict(list)
	try:
		sr = subprocess.check_output(['zypper', '-n', '--no-refresh', 'se', '-sx', '-tpackage', package], env={'LANG': 'c'}).decode()
		for line in re.split(r'-\+-+\n', sr, re.MULTILINE)[1].strip().split('\n'):
			version, arch, repo_name = [s.strip() for s in line.split('|')[3:]]
			if arch not in (get_cpu_arch(), 'noarch'):
				continue
			if repo_name == '(System Packages)':
				continue
			search_results[repo_name].append({'version': version, 'arch': arch})
	except subprocess.CalledProcessError as e:
		if e.returncode != 104:
			# 104 ZYPPER_EXIT_INF_CAP_NOT_FOUND is returned if there are no results
			raise

	repos_by_name = {repo['name']: repo for repo in get_repos()}
	local_installables = []
	for repo_name, installables in search_results.items():
		try:
			installables.sort(key=lambda p: cmp_to_key(rpm.labelCompare)(p['version']))
		except TypeError:
			# rpm 4.14 needs a tuple of epoch, version, release - rpm 4.18 can handle a string
			installables.sort(key=lambda p: cmp_to_key(rpm.labelCompare)(['1']+p['version'].split('-')))
		installable = installables[-1]
		installable['repository'] = repos_by_name[repo_name]
		installable['name'] = package
		installable['obs_instance'] = 'LOCAL_REPO'
		installable['project'] = installable['repository']['name']
		# filter out OBS/Packman repos as they are already searched via OBS/Packman API
		if 'download.opensuse.org/repositories' in installable['repository']['url']:
			continue
		if installable['repository']['filename'] == 'packman':
			continue
		local_installables.append(installable)
	return local_installables

def url_normalize(url):
	return re.sub(r'^https?', '', url).rstrip('/').replace('$releasever', get_version() or '$releasever')

def get_repos():
	for repo_file in os.listdir(REPO_DIR):
		if not repo_file.endswith('.repo'):
			continue
		try:
			cp = configparser.ConfigParser()
			cp.read(os.path.join(REPO_DIR, repo_file))
			mainsec = cp.sections()[0]
			if not bool(int(cp.get(mainsec, 'enabled'))):
				continue
			repo = {
				'alias': mainsec,
				'filename': re.sub(r'\.repo$', '', repo_file),
				'name': cp[mainsec].get('name', mainsec),
				'url': cp[mainsec].get('baseurl'),
			}
			if cp.has_option(mainsec, 'gpgkey'):
				repo['gpgkey'] = cp[mainsec].get('gpgkey')
			yield repo
		except Exception as e:
			print(f"Error parsing '{repo_file}': {e}")

def get_enabled_repo_by_url(url):
	for repo in get_repos():
		if url_normalize(repo['url']) == url_normalize(url):
			return repo

def add_repo(filename, name, url, enabled=True, gpgcheck=True, gpgkey=None, repo_type='rpm-md', auto_import_key=False, auto_refresh=False, priority=None):
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
	refresh_cmd = []
	if get_backend() == BackendConstants.zypp:
		refresh_cmd = ['sudo', 'zypper']
		if auto_import_key:
			refresh_cmd.append('--gpg-auto-import-keys')
		refresh_cmd.append('ref')
	elif get_backend() == BackendConstants.dnf:
		refresh_cmd = ['sudo', 'dnf', 'ref']
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
	    '%{NAME}-%{VERSION}-%{RELEASE}\n%{PACKAGER}\n%{DESCRIPTION}\nOPI-SPLIT-TOKEN-TO-TELL-KEY-PACKAGES-APART\n'])
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

def pkgmgr_action(action, packages=[], from_repo=None, allow_vendor_change=False, allow_arch_change=False, allow_downgrade=False, allow_name_change=False):
	if get_backend() == BackendConstants.zypp:
		args = ['sudo', 'zypper', action]
		if from_repo:
			args.extend(['--from', from_repo])
	elif get_backend() == BackendConstants.dnf:
		args = ['sudo', 'dnf', action]
		if from_repo:
			args.extend(['--repo', from_repo])
	if get_backend() == BackendConstants.zypp:
		if allow_downgrade:
			args.append('--allow-downgrade')
		if allow_arch_change:
			args.append('--allow-arch-change')
		if allow_name_change:
			args.append('--allow-name-change')
		if allow_vendor_change:
			args.append('--allow-vendor-change')
	elif get_backend() == BackendConstants.dnf:
		# allow_downgrade and allow_name_change are default in DNF
		if allow_vendor_change:
			args.append('--setopt=allow_vendor_change=True')
	args.extend(packages)
	subprocess.call(args)


###########
### OBS ###
###########

def search_published_binary(obs_instance, query):
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
		binaries = []
		for binary in dom.xpath('/collection/binary'):
			binary_data = {k: v for k, v in binary.items()}
			binary_data['obs_instance'] = obs_instance

			for k in ('name', 'project', 'repository', 'version', 'release', 'arch', 'filename', 'filepath', 'baseproject', 'type'):
				assert k in binary_data, f"Key '{k}' missing"

			# Filter out ghost binary
			# (package has been deleted, but binary still exists)
			if not binary_data.get('package'):
				continue

			# Filter out branch projects
			if ':branches:' in binary_data['project']:
				continue

			# Filter out Packman personal projects
			if binary_data['obs_instance'] != 'openSUSE' and is_personal_project(binary_data['project']):
				continue

			# Filter out debuginfo, debugsource, devel, buildsymbols, lang and docs packages
			regex = r'-(debuginfo|debugsource|buildsymbols|devel|lang|l10n|trans|doc|docs)(-.+)?$'
			if re.match(regex, binary_data['name']):
				continue

			# Filter out source packages
			if binary_data['arch'] == 'src':
				continue

			# Filter architecture
			cpu_arch = get_cpu_arch()
			if binary_data['arch'] not in (cpu_arch, 'noarch'):
				continue

			# Filter repo architecture
			if binary_data['repository'] == 'openSUSE_Factory' and (cpu_arch not in ('x86_64' 'i586')):
				continue
			elif binary_data['repository'] == 'openSUSE_Factory_ARM' and not cpu_arch.startswith('arm') and not cpu_arch == 'aarch64':
				continue
			elif binary_data['repository'] == 'openSUSE_Factory_PowerPC' and not cpu_arch.startswith('ppc'):
				continue
			elif binary_data['repository'] == 'openSUSE_Factory_zSystems' and not cpu_arch.startswith('s390'):
				continue
			elif binary_data['repository'] == 'openSUSE_Factory_RISCV' and not cpu_arch.startswith('risc'):
				continue

			binaries.append(binary_data)

		return binaries
	except requests.exceptions.HTTPError as e:
		if e.response.status_code == 413:
			print('Please use different search keywords. Some short keywords cause OBS timeout.')
		else:
			print('HTTPError:', e)
		sys.exit(1)

def get_binary_names(binaries):
	names = []
	for binary in binaries:
		name = binary['name']
		if name not in names:
			names.append(name)
	return names

def sort_uniq_binaries(binaries):
	""" sort -u for binaries; sort by weight and keep only the one with the best repo """
	binaries = sorted(binaries, key=get_binary_weight, reverse=True)
	new_binaries = []
	added_binaries = set()
	for binary in binaries:
		# only select the first binary for each name/project combination
		# which will be the one with the highest repo weight
		query = (binary['name'], binary['project'])
		if query not in added_binaries:
			new_binaries.append(binary)
			added_binaries.add(query)
	return new_binaries

def get_binary_weight(binary):
	weight = 0
	if is_official_project(binary['project']):
		weight += 200000
	elif not is_personal_project(binary['project']):
		weight += 100000

	if binary['name'] == binary['package']:
		weight += 10000

	dash_count = binary['name'].count('-')
	weight += 1000 * (0.5 ** dash_count)

	if not (get_cpu_arch() == 'x86_64' and binary['arch'] == 'i586'):
		weight += 100

	weight -= 10 * len(binary['name'])

	if binary['repository'].startswith('openSUSE_Tumbleweed'):
		weight += 2
	elif binary['repository'].startswith('openSUSE_Factory'):
		weight += 1
	elif binary['repository'] == 'standard':
		weight += 0

	return weight

def is_official_project(project):
	return project.startswith('openSUSE:')

def is_personal_project(project):
	return project.startswith('home:') or project.startswith('isv:')

def get_binaries_by_name(name, binaries):
	return [binary for binary in binaries if binary['name'] == name]

def install_binary(binary):
	name = binary['name']
	obs_instance = binary['obs_instance']
	arch = binary['arch']
	project = binary['project']
	repository = binary['repository']
	name_with_arch = f'{name}.{arch}'

	if obs_instance == 'Packman':
		# Install from Packman Repo
		add_packman_repo()
		install_packman_packages([name_with_arch])
	else:
		if binary['obs_instance'] == 'LOCAL_REPO':
			existing_repo = repository
		else:
			repo_alias = project.replace(':', '_')
			project_path = project.replace(':', ':/')
			if config.get_key_from_config('use_releasever_var'):
				version = get_version()
				if version:
					# version is None on tw
					repository = repository.replace(version, '$releasever')
			url = f'https://download.opensuse.org/repositories/{project_path}/{repository}/'
			gpgkey = url + 'repodata/repomd.xml.key'
			existing_repo = get_enabled_repo_by_url(url)
		if existing_repo:
			# Install from existing repos (don't add a repo)
			print(f"Installing from existing repo '{existing_repo['name']}'")
			install_packages([name_with_arch], from_repo=existing_repo['alias'])
		else:
			print(f"Adding repo '{project}'")
			add_repo(
				filename = repo_alias,
				name = project,
				url = url,
				gpgkey = gpgkey,
				gpgcheck = True,
				auto_refresh = True
			)
			install_packages([name_with_arch], from_repo=repo_alias,
				allow_downgrade=True,
				allow_arch_change=True,
				allow_name_change=True,
				allow_vendor_change=True
			)
			ask_keep_repo(repo_alias)


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
	text = '\n'.join(numbered_options)
	if not sys.stdout.isatty() or len(numbered_options) < (os.get_terminal_size().lines - 1) or disable_pager:
		# no pager needed
		print(text)
		input_string = input(question + ' ')
	else:
		input_string = pager.ask_number_with_pager(text, question)

	input_string = input_string.strip() or '0'
	num = int(input_string) if input_string.isdecimal() else -1
	if num == 0:
		sys.exit()
	elif not (num >= 1 and num <= len(options)):
		return ask_for_option(options, question, option_filter, disable_pager)
	else:
		return options[num - 1]

def ask_import_key(keyurl):
	keys = requests.get(keyurl.replace('$releasever', get_version() or '$releasever')).text
	db_keys = get_keys_from_rpmdb()
	for key in split_keys(keys):
		for line in subprocess.check_output(['gpg', '--quiet', '--show-keys', '--with-colons', '-'], input=key.encode()).decode().strip().split('\n'):
			if line.startswith('uid:'):
				key_info = line.split(':')[9].replace('\\x3a', ':')
		if [db_key for db_key in db_keys if normalize_key(key) in normalize_key(db_key['pubkey'])]:
			print(f"Package signing key '{key_info}' is already present.")
		else:
			if ask_yes_or_no(f"Import package signing key '{key_info}'"):
				tf = tempfile.NamedTemporaryFile('w')
				tf.file.write(key)
				tf.file.flush()
				subprocess.call(['sudo', 'rpm', '--import', tf.name])
				tf.file.close()

def ask_keep_key(keyurl, repo_name=None):
	"""
		Ask to remove the key given by url to key file.
		Warns about all repos still using the key except the repo given by repo_name param.
	"""
	urlkeys = split_keys(requests.get(keyurl.replace('$releasever', get_version() or '$releasever')).text)
	urlkeys_normalized = [normalize_key(urlkey) for urlkey in urlkeys]
	db_keys = get_keys_from_rpmdb()
	keys_to_ask_user = [key for key in db_keys if key['pubkey'] in urlkeys_normalized]
	for key in keys_to_ask_user:
		repos_using_this_key = []
		for repo in get_repos():
			if repo_name and repo['filename'] == repo_name:
				continue
			if repo.get('gpgkey'):
				repokey = normalize_key(requests.get(repo['gpgkey']).text)
				if repokey == key['pubkey']:
					repos_using_this_key.append(repo)
		if repos_using_this_key:
			default_answer = 'y'
			print('This key is still in use by the following remaining repos - removal is NOT recommended:')
			print(' - ' + '\n - '.join([repo['filename'] for repo in repos_using_this_key]))
		else:
			default_answer = 'n'
			print('This key is not in use by any remaining repos.')
		print('Keeping the key will allow additional packages signed by this key to be installed in the future without further warning.')
		if not ask_yes_or_no(f"Keep package signing key '{key['name']}'?", default_answer):
			subprocess.call(['sudo', 'rpm', '-e', key['kid']])

def ask_keep_repo(repo):
	if not ask_yes_or_no(f"Do you want to keep the repo '{repo}'?"):
		repo_info = next((r for r in get_repos() if r['filename'] == repo))
		if get_backend() == BackendConstants.zypp:
			subprocess.call(['sudo', 'zypper', 'rr', repo])
		if get_backend() == BackendConstants.dnf:
			subprocess.call(['sudo', 'rm', os.path.join(REPO_DIR, f'{repo}.repo')])
		if repo_info.get('gpgkey'):
			ask_keep_key(repo_info['gpgkey'], repo)

def format_binary_option(binary, table=True):
	if binary['obs_instance'] == 'LOCAL_REPO':
		color = 'green'
		symbol = '+'
	elif is_official_project(binary['project']):
		color = 'yellow'
		symbol = '-'
	elif is_personal_project(binary['project']):
		color = 'red'
		symbol = '!'
	else:
		color = 'cyan'
		symbol = '?'

	project = binary['project']
	if binary['obs_instance'] not in ('openSUSE', 'LOCAL_REPO'):
		project = f"{binary['obs_instance']} {project}"

	colored_name = colored(f'{project[:39]} {symbol}', color)

	if table:
		return f"{colored_name:50} | {binary['version'][:25]:25} | {binary['arch']}"
	else:
		return f"{colored_name} | {binary['version']} | {binary['arch']}"
