from termcolor import cprint

import opi
from opi.rpmbuild import RPMBuild
from opi.plugins import BasePlugin


RPM_URLS = {
	'x86_64': 'https://persistent.oaistatic.com/codex-app-prod/linux/rpm/latest/chatgpt.x86_64.rpm',
	'aarch64': 'https://persistent.oaistatic.com/codex-app-prod/linux/rpm/latest/chatgpt.aarch64.rpm',
}
COMPAT_PACKAGE = 'chatgpt-opensuse-compat'


class ChatGPT(BasePlugin):
	main_query = 'chatgpt'
	description = 'Official ChatGPT desktop app (unsupported community integration for openSUSE Tumbleweed)'
	queries = ['chatgpt']

	@classmethod
	def run(cls, query):
		if opi.get_os_release().get('NAME') != 'openSUSE Tumbleweed':
			cprint('The ChatGPT OPI plugin currently supports openSUSE Tumbleweed only.', 'red')
			return
		arch = opi.get_cpu_arch()
		if arch not in RPM_URLS:
			cprint(f'The ChatGPT OPI plugin does not support architecture {arch}.', 'red')
			return
		cprint(
			'OpenAI does not officially support openSUSE, and does not publish its RPM '
			'signing key separately. This community integration installs the unmodified '
			'official package without signature verification.',
			'yellow',
		)
		if not opi.ask_yes_or_no('Do you want to install ChatGPT from the official OpenAI download?'):
			return

		compat = RPMBuild(
			COMPAT_PACKAGE,
			'1',
			'openSUSE compatibility dependencies for ChatGPT',
			requires=['libvulkan_lvp'],
			provides=['mesa-vulkan-drivers'],
			autoreq=False,
		)
		compat.build()
		opi.install_packages([compat.rpmfile_path], allow_unsigned=True)

		# The RPM is signed, but OpenAI does not publish the signing key through
		# an independent official URL, so a fresh system cannot authenticate it.
		opi.install_packages([RPM_URLS[arch]], allow_unsigned=True)
