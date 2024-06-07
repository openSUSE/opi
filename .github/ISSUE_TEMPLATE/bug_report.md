---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---

**Please also attach the output of these commands to your bug**
```
cat /etc/os-release
(cd /etc/zypp/repos.d; \ls | while read line ; do echo -e "\n----\n$(ls -l $line):"; cat "$line" ; done)
```
