#!/usr/bin/python3

import sys
import pexpect
import subprocess

c = pexpect.spawn('./bin/opi vivaldi', logfile=sys.stdout.buffer, echo=False)

c.expect("Do you want to install")
c.sendline('y')

c.expect("Continue")
c.sendline('y')

c.expect("Do you want to keep", timeout=800)
c.sendline('y')

c.interact()
c.wait()
c.close()
assert c.exitstatus == 0, "Exit code: %i" % c.exitstatus

subprocess.check_call(['rpm', '-qi', 'vivaldi-stable'])
subprocess.check_call('zypper lr | grep vivaldi', shell=True)
