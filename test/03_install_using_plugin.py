#!/usr/bin/python3

import sys
import pexpect
import subprocess

c = pexpect.spawn('./bin/opi yandex-disk', logfile=sys.stdout.buffer, echo=False)

c.expect("Do you want to install")
c.sendline('y')

c.expect("Continue")
c.sendline('y')

c.expect("Do you want to keep", timeout=500)
c.sendline('y')

c.interact()
c.wait()
c.close()
assert c.exitstatus == 0, "Exit code: %i" % c.exitstatus

subprocess.check_call(['rpm', '-qi', 'yandex-disk'])
subprocess.check_call('zypper lr | grep yandex-disk', shell=True)
