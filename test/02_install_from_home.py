#!/usr/bin/python3

import sys
import pexpect
import subprocess

c = pexpect.spawn('./bin/opi xosview', logfile=sys.stdout.buffer, echo=False)

c.expect("1. xosview\r\n")
c.expect('Choose a number')
c.sendline('1')

c.expect("2. .*X11:Utilities", timeout=10)
c.sendline('2')

c.expect("Do you want to reject the key", timeout=10)
c.sendline('t')

c.expect("new packages to install", timeout=10)
c.expect("Continue", timeout=10)
c.sendline('y')

c.expect("Do you want to keep the repo", timeout=150)
c.sendline('n')

c.interact()
c.wait()
c.close()
assert c.exitstatus == 0, "Exit code: %i" % c.exitstatus

subprocess.check_call(['rpm', '-qi', 'xosview'])
subprocess.check_call('zypper lr -u | grep -v X11', shell=True)
