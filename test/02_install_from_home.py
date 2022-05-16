#!/usr/bin/python3

import sys
import pexpect
import subprocess

c = pexpect.spawn('./bin/opi rtl8812au', logfile=sys.stdout.buffer, echo=False)

c.expect('1. rtl8812au\r\n')
c.sendline('q')
c.expect('Pick a number')
c.sendline('1')

c.expect(r'([0-9]+)\. [^ ]*hardware', timeout=10)
hwentryid = c.match.groups()[0]
print("PEXPECT: Found hardware entry id %r" % hwentryid)
c.sendline(hwentryid)

c.expect('new packages? to install', timeout=60)
c.expect('Continue', timeout=60)
c.sendline('y')

c.expect('Do you want to keep the repo', timeout=350)
c.sendline('n')

c.interact()
c.wait()
c.close()
assert c.exitstatus == 0, 'Exit code: %i' % c.exitstatus

subprocess.check_call(['rpm', '-qi', 'rtl8812au'])
subprocess.check_call('zypper lr -u | grep -v hardware', shell=True)
