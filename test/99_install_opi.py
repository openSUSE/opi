#!/usr/bin/python3

import sys
import pexpect
import subprocess

subprocess.check_call(['python3', 'setup.py', 'install'])
version = subprocess.check_output(['python3', 'setup.py', '--version']).decode().strip()
subprocess.check_call("opi --version | grep %s" % version, shell=True)
subprocess.check_call("opi --help | grep --color -A1000 -B1000 Microsoft", shell=True)
