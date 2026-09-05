import subprocess
import tempfile

from termcolor import cprint

import opi
from opi.rpmbuild import RPMBuild
from opi.plugins import BasePlugin


SUPPORTED_ARCHITECTURES = {'x86_64', 'aarch64'}
COMPAT_PACKAGE = 'chatgpt-opensuse-compat'
REPO_ALIAS = 'openai-chatgpt'
REPO_URL = 'https://persistent.oaistatic.com/codex-app-prod/linux/rpm/$basearch'
REPO_KEY_PATH = '/etc/pki/rpm-gpg/RPM-GPG-KEY-chatgpt'
DEFAULTS_PATH = '/etc/default/chatgpt'
# Extracted from the official ChatGPT RPM. Fingerprint:
# 3BFA 0E4A E8B8 CC16 A2D9 BA68 4A3B 4A56 6C46 60E4
REPO_KEY = '''-----BEGIN PGP PUBLIC KEY BLOCK-----

mQINBGpypFUBEACi1Vvzq9pIpA6lj7chbqELuxJtVuzUzxrasa6ZU0yF4yhq7jf8
3YkJRHwbezBKeQyzJ5lkX0EhXS8aXxUhMAm3PFpAlwcInfKzmV7atJwvaxIw6Rmd
GYe9fBWKjTN/SmPIjtyxrTznZY97+TfD1AeGZpLaJ8fsnhrC+HkiN2TACiTocgpe
hFiP0OWK7mWZeTWnY2scpIYXP1Ro7nQv4KacmY4JacTQ7m/HM0Qej/3olhuEv2Cw
lMVWw57/oHhmTllfLDQOogFQyIVqaaR98y/Eu6cAabSfcsqAAZ2A8vfHYD27z28J
vLO2PZEJd5ThlnX4Zqv0eIpZdBj//8Sl/MSqTshFZ1NDsRoqwdqw284X5MpnOJ4k
4Sc2Se8tJxt/nCeibH3dJ504Fb1X/mnOqhCAQ6pVJz4RB5HRlFPSkxVPyag1v1m/
7T4vie+OR4eqFQNz6mudrOoMmeVIfyL5fbe4cOr4fk/FyvEE2xMgkFatPqXn7vM9
og+zremPCfwRAFpBPyX74VowFY7llcdaj/w8K5T8PzM14Hb3E4ZKizMluKmTvTq9
WE1/eSQJLLQqXD5VmtmdUaC/VyE/1ZlIxcA1LWqvEQ327UXREvX/nHsrkKrl956W
jzkiHFUTsD1NJ0dMfs+csOt8Furb5jZj+HsMmCm9jLdfz5b/4WKLPbvxIwARAQAB
tBZDb2RleCBMaW51eCBSZXBvc2l0b3J5iQJRBBMBCgA7FiEEO/oOSui4zBai2bpo
SjtKVmxGYOQFAmpypFUCGwMFCwkIBwICIgIGFQoJCAsCBBYCAwECHgcCF4AACgkQ
SjtKVmxGYORlCQ/9FyikZo8HQcJBP9E/oXVPds/fQnIFB2qJR2z3DrfYEonNt/ev
SAySkPPq4/mEOjaI0pFlDDGSaps+FTcJFgoVRTasBIF7JJivvjW9ap8iWEbhhVLe
IrFLbMLpUcTRntUx7R4fVMJ/1/cGn+NWZmNwS9ORorzSyCH0IAgCw1Xc3ZrjuMbF
VjdToMC1TiXXCEmlYpQakmQ3Ay1cH0FHC2BBNn1MNVkJdPhpZIZCdhaMPHfYFpyo
pg8wFvZ5iIcvlbMgyuy8CPJVRWUcYy2dOhEOGnYJnXRPkE3E1hf8YOHNzRlduH89
6lT9qcEK2+fpLfrVGoc4zscLZ+Ey+Ko6iQRdVE1j67+wNR3hX8ukue574v1N/xxu
i575jumSE19lEj1sH4+P4gFHOtTbF0JhKKzLctbga0IAwTPKhnt3qzj1U5Yj/MZS
uEVjrLhdRauOuFBXUclgyVf2w/lE85UUOdlcollsYA6Huq7xDamqf8SslZQGre3E
I+lhpqJR1cOwDMUzzcl40uTyhrxXXd/bk4QSlhZbwHR25Pnt+ZMtWavlQWS0eDEV
8djuXAURCmx5WOqAFB/TJe1mn5EvyWg4VFzrY/NVNOpzgY5+Xp7J28z7f637r712
Eu9j4imVcdPigwS+jf/0f81i2o9b82Y26TN8+EtDLCY841MJ1lrjDrX/dno=
=Y+3h
-----END PGP PUBLIC KEY BLOCK-----
'''


def install_file(contents, destination):
	with tempfile.NamedTemporaryFile('w') as source:
		source.write(contents)
		source.flush()
		subprocess.check_call([
			'sudo', 'install', '-D', '-m', '0644', source.name, destination,
		])


class ChatGPT(BasePlugin):
	main_query = 'chatgpt'
	description = 'Official ChatGPT desktop app'
	queries = ['chatgpt']

	@classmethod
	def run(cls, query):
		arch = opi.get_cpu_arch()
		if arch not in SUPPORTED_ARCHITECTURES:
			cprint(f'The ChatGPT OPI plugin does not support architecture {arch}.', 'red')
			return
		if not opi.ask_yes_or_no('Do you want to install ChatGPT from the official OpenAI repository?'):
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

		install_file(REPO_KEY, REPO_KEY_PATH)
		subprocess.check_call(['sudo', 'rpm', '--import', REPO_KEY_PATH])
		install_file('repo_add_once="false"\n', DEFAULTS_PATH)

		opi.add_repo(
			filename=REPO_ALIAS,
			name='ChatGPT',
			url=REPO_URL,
		)
		opi.install_packages(['chatgpt'])
		opi.ask_keep_repo(REPO_ALIAS)
