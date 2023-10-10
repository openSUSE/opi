#!/usr/bin/python3

import sys
import pexpect
import subprocess

c = pexpect.spawn('./bin/opi -m android-tools yandex-disk', logfile=sys.stdout.buffer, echo=False)

# plugins are installed first
c.expect('Do you want to install')
c.sendline('y')

c.expect('Import package signing key', timeout=10)
c.sendline('y')

c.expect('Continue')
c.sendline('y')

c.expect('Do you want to keep', timeout=500)
c.sendline('y')

# packages come after plugins
c.expect(r'([0-9]+)\. android-tools', timeout=10)
entry_id = c.match.groups()[0]
print(f'PEXPECT: Found entry id {entry_id!r}')
c.expect('Pick a number')
c.sendline(entry_id)

c.expect(r'([0-9]+)\. [^ ]*(openSUSE-Tumbleweed-Oss|Main Repository)', timeout=10)
entry_id = c.match.groups()[0]
print(f'PEXPECT: Found entry id {entry_id!r}')
c.sendline(entry_id)

c.expect('Installing from existing repo', timeout=10)
c.expect('Continue?', timeout=20)
c.sendline('y')

c.interact()
c.wait()
c.close()
print()
assert c.exitstatus == 0, f'Exit code: {c.exitstatus}'
subprocess.check_call(['rpm', '-qi', 'yandex-disk'])
subprocess.check_call(['rpm', '-qi', 'android-tools'])
