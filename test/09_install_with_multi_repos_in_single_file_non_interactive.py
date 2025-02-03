#!/usr/bin/python3

import sys
import pexpect
import subprocess

subprocess.check_call("cat /etc/zypp/repos.d/*.repo > /tmp/singlefile.repo", shell=True)
subprocess.check_call("rm -v /etc/zypp/repos.d/*.repo", shell=True)
subprocess.check_call("mv -v /tmp/singlefile.repo /etc/zypp/repos.d/", shell=True)

c = pexpect.spawn('./bin/opi -n tmux', logfile=sys.stdout.buffer, echo=False)

c.expect(r'([0-9]+)\. tmux', timeout=10)
c.expect('Pick a number')
c.expect(r'([0-9]+)\. [^ ]*(openSUSE-Tumbleweed-Oss|Main Repository)', timeout=10)
c.expect('Installing from existing repo', timeout=10)
c.expect('Continue?', timeout=60)
c.interact()
c.wait()
c.close()
print()
assert c.exitstatus == 0, f'Exit code: {c.exitstatus}'
subprocess.check_call(['rpm', '-qi', 'tmux'])


c = pexpect.spawn('./bin/opi -n helloworld-opi-tests', logfile=sys.stdout.buffer, echo=False)

c.expect(r'([0-9]+)\. helloworld-opi-tests', timeout=10)
c.expect('Pick a number')
c.expect(r'([0-9]+)\. [^ ]*(home:dheidler:opitests)', timeout=10)
c.expect('Adding repo \'home:dheidler:opitests\'', timeout=10)
c.expect('Continue?', timeout=60)
c.interact()
c.wait()
c.close()
print()
assert c.exitstatus == 0, f'Exit code: {c.exitstatus}'
subprocess.check_call(['rpm', '-qi', 'helloworld-opi-tests'])
