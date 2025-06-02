#!/usr/bin/python3

import sys
import pexpect
import subprocess
import time

c = pexpect.spawn('./bin/opi -v x265', logfile=sys.stdout.buffer, echo=False)

c.expect('1. x265\r\n')
c.sendline('q')
c.expect('Pick a number')
c.sendline('1')

c.expect('1. .*Packman Essentials', timeout=10)
c.sendline('1')

c.expect('Pick a mirror near your location', timeout=10)
c.sendline('2')

c.expect('Import package signing key', timeout=10)
c.sendline('y')

c.expect('Package install size change', timeout=60)
c.expect('Continue', timeout=60)
time.sleep(3)
c.sendline('y')
c.interact()
c.wait()
c.close()
assert c.exitstatus == 0, f'Exit code: {c.exitstatus}'

subprocess.check_call(['rpm', '-qi', 'x265'])
