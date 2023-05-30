#!/usr/bin/python3

import sys
import pexpect
import subprocess

c = pexpect.spawn('./bin/opi resilio-sync', logfile=sys.stdout.buffer, echo=False)

c.expect('Do you want to install')
c.sendline('y')

c.expect('Import package signing key', timeout=10)
c.sendline('y')

c.expect('Continue')
c.sendline('y')

c.expect('Do you want to keep', timeout=500)
c.sendline('y')

c.interact()
c.wait()
c.close()
assert c.exitstatus == 0, f'Exit code: {c.exitstatus}'

subprocess.check_call(['rpm', '-qi', 'resilio-sync'])
subprocess.check_call('zypper lr | grep resilio-sync', shell=True)
