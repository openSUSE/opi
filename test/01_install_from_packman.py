#!/usr/bin/python3

import sys
import pexpect
import subprocess

c = pexpect.spawn('./bin/opi gstreamer-plugins-ugly', logfile=sys.stdout.buffer, echo=False)

c.expect("1. gstreamer-plugins-ugly\r\n")
c.expect('Choose a number')
c.sendline('1')

c.expect("3. .*Packman Essentials", timeout=10)
c.sendline('3')

c.expect("Do you want to reject the key", timeout=10)
c.sendline('t')

c.expect("new packages to install", timeout=10)
c.expect("Continue", timeout=10)
c.sendline('y')
c.interact()
c.wait()
c.close()
assert c.exitstatus == 0, "Exit code: %i" % c.exitstatus

subprocess.check_call(['rpm', '-qi', 'gstreamer-plugins-ugly'])
