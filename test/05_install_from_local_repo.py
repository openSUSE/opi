#!/usr/bin/python3

import sys
import pexpect

c = pexpect.spawn('./bin/opi -v htop', logfile=sys.stdout.buffer, echo=False)

c.expect(r'([0-9]+)\. htop', timeout=10)
entry_id = c.match.groups()[0]
print(f'PEXPECT: Found entry id {entry_id!r}')
c.expect('Pick a number')
c.sendline(entry_id)

c.expect(r'([0-9]+)\. [^ ]*(openSUSE-Tumbleweed-Oss|Main Repository)', timeout=10)
entry_id = c.match.groups()[0]
print(f'PEXPECT: Found entry id {entry_id!r}')
c.sendline(entry_id)

c.expect('Installing from existing repo', timeout=10)
c.expect('Continue?', timeout=10)
c.sendline('n')

c.interact()
c.wait()
c.close()
print()
assert c.exitstatus == 0, f'Exit code: {c.exitstatus}'
