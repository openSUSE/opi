# OPI

**O**BS **P**ackage **I**nstaller

## System Requirements

- openSUSE Tumbleweed, openSUSE Leap 42.1+, SLE 12+
- perl
- perl-libwww-perl
- perl-XML-LibXML
- perl-URI
- perl-Config-Tiny

## Install

```
sudo zypper addrepo https://download.opensuse.org/repositories/home:guoyunhe/openSUSE_Tumbleweed/home:guoyunhe.repo
sudo zypper refresh
sudo zypper install opi
```

## Use

Command:

```
opi filezilla
```

Output:

![Screenshot](screenshot.png)

### Packages from Other Repositories

**Visual Studio Code**

```
opi vs code
```
