#!/usr/bin/python3

import sys
import pexpect
import subprocess

c = pexpect.spawn('./bin/opi -nm zfs resilio-sync html2text yandex-disk', logfile=sys.stdout.buffer, echo=False)

# plugins are installed first
c.expect('Do you want to install resilio-sync')
c.expect('Import package signing key', timeout=10)
c.expect('Continue')
c.expect('Do you want to keep', timeout=500)

c.expect('Do you want to install yandex-disk')
c.expect('Import package signing key', timeout=10)
c.expect('Continue')
c.expect('Do you want to keep', timeout=500)

# packages come after plugins
c.expect(r'([0-9]+)\. zfs', timeout=10)
c.expect('Pick a number')
c.expect(r'([0-9]+)\. [^ ]*(filesystems)', timeout=10)
c.expect('Adding repo \'filesystems\'', timeout=10)
c.expect('Continue?', timeout=20)

c.expect(r'([0-9]+)\. html2text', timeout=10)
c.expect('Pick a number')
c.expect(r'([0-9]+)\. [^ ]*(openSUSE-Tumbleweed-Oss|Main Repository)', timeout=10)
c.expect('Installing from existing repo', timeout=10)
c.expect('Continue?', timeout=20)

c.interact()
c.wait()
c.close()
print()
assert c.exitstatus == 0, f'Exit code: {c.exitstatus}'
subprocess.check_call(['rpm', '-qi', 'resilio-sync'])
subprocess.check_call(['rpm', '-qi', 'yandex-disk'])
subprocess.check_call(['rpm', '-qi', 'zfs'])
subprocess.check_call(['rpm', '-qi', 'html2text'])
