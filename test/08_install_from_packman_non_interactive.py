#!/usr/bin/python3

import sys
import pexpect
import subprocess

c = pexpect.spawn('./bin/opi -v -n x265', logfile=sys.stdout.buffer, echo=False)

c.expect('1. x265\r\n')
c.expect('Pick a number')

c.expect('1. .*Packman Essentials', timeout=10)

c.expect('Package install size change', timeout=60)
c.interact()
c.wait()
c.close()
assert c.exitstatus == 0, f'Exit code: {c.exitstatus}'

subprocess.check_call(['rpm', '-qi', 'x265'])
