import os
import sys
import subprocess
import re
import tempfile
import math

import requests
import lxml.etree

from termcolor import colored
from shutil import which
from tempfile import NamedTemporaryFile
from os import path, remove

from opi.backends import get_backend, BackendConstants
from opi import pager
from opi import config

OBS_APIROOT = {
	'openSUSE': 'https://api.opensuse.org',
	'Packman': 'https://pmbs.links2linux.de'
}
PROXY_URL = 'https://opi-proxy.opensuse.org/'


###################
### System Info ###
###################

cpu_arch = ''
def get_cpu_arch():
	global cpu_arch
	if not cpu_arch:
		cpu_arch = subprocess.check_output(['uname', '-m']).strip().decode('ASCII')
		if re.match(r"^i.86$", cpu_arch):
			cpu_arch = 'i586'
	return cpu_arch

def get_os_release():
	os_release = {}
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
		# strip prerelease suffix (eg. " Alpha")
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
	project = get_distribution(use_releasever_variable=config.get_key_from_config("use_releasever_var"))
	project = project.replace(':', '_')
	project = project.replace('Factory', 'Tumbleweed')

	add_repo(
		filename = 'packman',
		name = 'Packman',
		url = 'https://ftp.gwdg.de/pub/linux/misc/packman/suse/%s/' % project,
		auto_refresh = True,
		priority = 90
	)

	if dup:
		if get_backend() == BackendConstants.zypp:
			subprocess.call(['sudo', 'zypper', 'dist-upgrade', '--from', 'packman', '--allow-downgrade', '--allow-vendor-change'])
		elif get_backend() == BackendConstants.dnf:
			subprocess.call(['sudo', 'dnf', 'dup', '--setopt=allow_vendor_change=True', '--repo', 'packman'])

def install_packman_packages(packages, **kwargs):
	install_packages(packages, from_repo='packman', **kwargs)


################
### ZYPP/DNF ###
################

def add_repo(filename, name, url, enabled=True, gpgcheck=True, gpgkey=None, repo_type='rpm-md', auto_import_key=False, auto_refresh=False, priority=None):
	tf = tempfile.NamedTemporaryFile('w')
	tf.file.write("[%s]\n" % filename)
	tf.file.write("name=%s\n" % name)
	tf.file.write("baseurl=%s\n" % url)
	tf.file.write("enabled=%i\n" % enabled)
	tf.file.write("type=%s\n" % repo_type)
	tf.file.write("gpgcheck=%i\n" % gpgcheck)
	if gpgkey:
		subprocess.call(['sudo', 'rpm', '--import', gpgkey.replace('$releasever', get_version() or '$releasever')])
		tf.file.write("gpgkey=%s\n" % gpgkey)
	if auto_refresh:
		tf.file.write("autorefresh=1\n")
	if priority:
		tf.file.write("priority=%i\n" % priority)
	tf.file.flush()
	subprocess.call(['sudo', 'cp', tf.name, '/etc/zypp/repos.d/%s.repo' % filename])
	subprocess.call(['sudo', 'chmod', '644', '/etc/zypp/repos.d/%s.repo' % filename])
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

def install_packages(packages, from_repo=None, allow_vendor_change=False, allow_arch_change=False, allow_downgrade=False, allow_name_change=False):
	if get_backend() == BackendConstants.zypp:
		args = ['sudo', 'zypper', 'in']
		if from_repo:
			args.extend(['--from', from_repo])
	elif get_backend() == BackendConstants.dnf:
		args = ['sudo', 'dnf', 'in']
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
		xquery = "'%s'" % query
	xpath = "contains-ic(@name, %s) and path/project='%s'" % (xquery, distribution)
	url = requests.Request('GET', url, params={'match': xpath, 'limit': 0}).prepare().url
	try:
		r = requests.get(PROXY_URL, params={'obs_api_link': url, 'obs_instance': obs_instance})
		r.raise_for_status()

		dom = lxml.etree.fromstring(r.text)
		binaries = []
		for binary in dom.xpath('/collection/binary'):
			binary_data = {k: v for k, v in binary.items()}
			binary_data['obs_instance'] = obs_instance

			for k in ['name', 'project', 'repository', 'version', 'release', 'arch', 'filename', 'filepath', 'baseproject', 'type']:
				assert k in binary_data, 'Key "%s" missing' % k

			# Filter out ghost binary
			# (package has been deleted, but binary still exists)
			if not binary_data.get('package'):
				continue

			# Filter out branch projects
			if ':branches:' in binary_data['project']:
				continue

			# Filter out Packman personal projects
			if binary_data['obs_instance'] != 'openSUSE'and is_personal_project(binary_data['project']):
				continue

			# Filter out debuginfo, debugsource, devel, buildsymbols, lang and docs packages
			regex = r"-(debuginfo|debugsource|buildsymbols|devel|lang|l10n|trans|doc|docs)(-.+)?$"
			if re.match(regex, binary_data['name']):
				continue

			# Filter out source packages
			if binary_data['arch'] == 'src':
				continue

			# Filter architecture
			if binary_data['arch'] not in (get_cpu_arch(), 'noarch'):
				continue

			binaries.append(binary_data)

		return binaries
	except requests.exceptions.HTTPError as e:
		if e.response.status_code == 413:
			print("Please use different search keywords. Some short keywords cause OBS timeout.")
		else:
			print("HTTPError: %s" % e)
		sys.exit(1)

def get_binary_names(binaries):
	names = []
	for binary in binaries:
		name = binary['name']
		if name not in names:
			names.append(name)
	return names

def sort_binaries(binaries):
	return sorted(binaries, key=lambda b: get_binary_weight(b), reverse=True)

def get_binary_weight(binary):
	weight = 0
	if is_official_project(binary['project']):
		weight += 20000
	elif is_personal_project(binary['project']):
		weight += 0
	else:
		weight += 10000

	if binary['name'] == binary['package']:
		weight += 1000

	dash_count = binary['name'].count('-')
	weight += 100 * (0.5**dash_count)

	if not (get_cpu_arch() == 'x86_64' and binary['arch'] == 'i586'):
		weight += 10

	weight -= len(binary['name'])

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
	name_with_arch = "%s.%s" % (name, arch)

	if obs_instance == 'Packman':
		# Install from Packman Repo
		add_packman_repo()
		install_packman_packages([name_with_arch])
	elif is_official_project(project):
		# Install from official repos (don't add a repo)
		install_packages([name_with_arch])
	else:
		repo_alias = project.replace(':', '_')
		project_path = project.replace(':', ':/')
		if config.get_key_from_config("use_releasever_var"):
			version = get_version()
			if version:
				# version is None on tw
				repository = repository.replace(version, '$releasever')
		add_repo(
			filename = repo_alias,
			name = project,
			url = "https://download.opensuse.org/repositories/%s/%s/" % (project_path, repository),
			gpgkey = "https://download.opensuse.org/repositories/%s/%s/repodata/repomd.xml.key" % (project_path, repository),
			gpgcheck = True,
			auto_refresh = True
		)
		install_packages([name_with_arch], from_repo=repo_alias, allow_downgrade=True, allow_arch_change=True, allow_name_change=True, allow_vendor_change=True)
		ask_keep_repo(repo_alias)


########################
### User Interaction ###
########################

def ask_yes_or_no(question, default_answer):
	q = question + ' '
	if default_answer == 'y':
		q += '(Y/n)'
	else:
		q += '(y/N)'
	q += ' '
	answer = input(q) or default_answer
	return answer.strip().lower() == 'y'

def ask_for_option(options, question="Pick a number (0 to quit):", option_filter=lambda a: a, disable_pager=False):
	"""
		Ask the user for a number to pick in order to select an option.
		Exit if the number is 0.
		Specify the number with question and the corresponding option will be returned.
		Via option_filter a callback function to format option entries can be supplied,
		but this doesn't work with the pager.
		If needed, a pager will be used, unless disable_pager is True.
	"""

	padding_len = math.floor(math.log(len(options), 10))
	i = 1
	numbered_options = []
	terminal_width = os.get_terminal_size().columns-1 if sys.stdout.isatty() else 0
	for option in options:
		number = "%%%id. " % (padding_len+1) % i
		numbered_option = number + option_filter(option)
		if terminal_width and not disable_pager:
			# break too long lines:
			# if pager is disabled this might mean that we get terminal sequences here
			# which might get broken by some spaces and newlines.
			# also too long lines are not fatal outside of the pager
			while len(numbered_option) > terminal_width:
				numbered_options.append(numbered_option[:terminal_width])
				numbered_option = ' '*len(number) + numbered_option[terminal_width:]
		numbered_options.append(numbered_option)
		i += 1
	text = '\n'.join(numbered_options)
	if not sys.stdout.isatty() or len(numbered_options) < (os.get_terminal_size().lines-1) or disable_pager:
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
		return options[num-1]

def ask_keep_repo(repo):
	if not ask_yes_or_no('Do you want to keep the repo "%s"?' % repo, 'y'):
		if get_backend() == BackendConstants.zypp:
			subprocess.call(['sudo', 'zypper', 'rr', repo])
		if get_backend() == BackendConstants.dnf:
			subprocess.call(['sudo', 'rm', '/etc/zypp/repos.d/' + repo + '.repo'])

def format_binary_option(binary, table=True):
	if is_official_project(binary['project']):
		color = 'green'
		symbol = '+'
	elif is_personal_project(binary['project']):
		color = 'red'
		symbol = '!'
	else:
		color = 'cyan'
		symbol = '?'

	project = binary['project']
	if binary['obs_instance'] != 'openSUSE':
		project = '%s %s' % (binary['obs_instance'], project)

	colored_name = colored('%s %s' % (project[0:39], symbol), color)

	if table:
		return '%-50s | %-25s | %s' % (colored_name, binary['version'][0:25], binary['arch'])
	else:
		return '%s | %s | %s' % (colored_name, binary['version'], binary['arch'])
