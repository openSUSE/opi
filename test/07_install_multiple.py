#!/usr/bin/python3

import sys
import pexpect
import subprocess

c = pexpect.spawn('./bin/opi -nm helloworld-opi-tests resilio-sync tmux', logfile=sys.stdout.buffer, echo=False)

# plugins are installed first
c.expect('Do you want to install')
c.expect('Import package signing key', timeout=10)
c.expect('Continue')
c.expect('Do you want to keep', timeout=500)

# packages come after plugins
c.expect(r'([0-9]+)\. helloworld-opi-tests', timeout=10)
c.expect('Pick a number')
c.expect(r'([0-9]+)\. [^ ]*(home:dheidler:opitests)', timeout=10)
c.expect('Adding repo \'home:dheidler:opitests\'', timeout=10)
c.expect('Continue?', timeout=60)

c.expect(r'([0-9]+)\. tmux', timeout=60)
c.expect('Pick a number')
c.expect(r'([0-9]+)\. [^ ]*(openSUSE-Tumbleweed-Oss|Main Repository)', timeout=10)
c.expect('Installing from existing repo', timeout=10)
c.expect('Continue?', timeout=60)

c.interact()
c.wait()
c.close()
print()
assert c.exitstatus == 0, f'Exit code: {c.exitstatus}'
subprocess.check_call(['rpm', '-qi', 'resilio-sync'])
subprocess.check_call(['rpm', '-qi', 'helloworld-opi-tests'])
subprocess.check_call(['rpm', '-qi', 'tmux'])
