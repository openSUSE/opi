#!/usr/bin/python3

import subprocess

def run(cmd, **kwargs):
    print('% ' + (' '.join(cmd) if isinstance(cmd, list) else cmd))
    subprocess.check_call(cmd, **kwargs)

version = subprocess.check_output(['python3', 'setup.py', '--version']).decode().strip()
run(['python3', '-mpip', 'wheel', '--verbose', '--progress-bar', 'off', '--disable-pip-version-check', '--use-pep517', '--no-build-isolation', '--no-deps', '--wheel-dir', './build', '.'])
cmd = ['python3', '-mpip', 'install', '--root-user-action=ignore', '--break-system-packages', '--verbose', '--progress-bar', 'off', '--disable-pip-version-check', '--no-compile', '--ignore-installed', '--no-deps', '--no-index', '--find-links', './build', f"opi=={version}"]
if subprocess.run('grep "openSUSE Leap" /etc/os-release', shell=True).returncode == 0:
    cmd.remove('--root-user-action=ignore')
    cmd.remove('--break-system-packages')
run(cmd)
run(f'opi --version | grep {version}', shell=True)
run('opi --help | grep --color -A1000 -B1000 Microsoft', shell=True)
