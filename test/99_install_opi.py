#!/usr/bin/python3

import subprocess

version = subprocess.check_output(['python3', 'setup.py', '--version']).decode().strip()
subprocess.check_call(['python3', '-mpip', 'wheel', '--verbose', '--progress-bar', 'off', '--disable-pip-version-check', '--use-pep517', '--no-build-isolation', '--no-deps', '--wheel-dir', './build', '.'])
subprocess.check_call(['python3', '-mpip', 'install', '--root-user-action=ignore', '--break-system-packages', '--verbose', '--progress-bar', 'off', '--disable-pip-version-check', '--no-compile', '--ignore-installed', '--no-deps', '--no-index', '--find-links', './build', f"opi=={version}"])
subprocess.check_call(f'opi --version | grep {version}', shell=True)
subprocess.check_call('opi --help | grep --color -A1000 -B1000 Microsoft', shell=True)
