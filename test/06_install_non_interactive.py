#!/usr/bin/python3

import sys
import pexpect
import subprocess

c = pexpect.spawn('./bin/opi -n bottom', logfile=sys.stdout.buffer, echo=False)

c.expect(r'([0-9]+)\. bottom', timeout=20)
c.expect('Pick a number')
c.expect(r'([0-9]+)\. [^ ]*(openSUSE-Tumbleweed-Oss|Main Repository)', timeout=20)
c.expect('Installing from existing repo', timeout=20)
c.expect('Continue?', timeout=60)
c.interact()
c.wait()
c.close()
print()
assert c.exitstatus == 0, f'Exit code: {c.exitstatus}'
subprocess.check_call(['rpm', '-qi', 'bottom'])


c = pexpect.spawn('./bin/opi -n helloworld-opi-tests', logfile=sys.stdout.buffer, echo=False)

c.expect(r'([0-9]+)\. helloworld-opi-tests', timeout=20)
c.expect('Pick a number')
c.expect(r'([0-9]+)\. [^ ]*(home:dheidler:opitests)', timeout=20)
c.expect('Adding repo \'home:dheidler:opitests\'', timeout=20)
c.expect('Continue?', timeout=60)
c.interact()
c.wait()
c.close()
print()
assert c.exitstatus == 0, f'Exit code: {c.exitstatus}'
subprocess.check_call(['rpm', '-qi', 'helloworld-opi-tests'])
