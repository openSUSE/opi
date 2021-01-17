# OPI

**O**BS **P**ackage **I**nstaller

Search and install almost all packages available for openSUSE and SLE:

1. openSUSE Build Service
2. Packman
3. Popular packages for Microsoft and other vendors

## System Requirements

- openSUSE Tumbleweed, openSUSE Leap 42.1+, SLE 12+
- perl
- perl-libwww-perl
- perl-XML-LibXML
- perl-URI
- perl-Config-Tiny

## Install

### openSUSE Tumbleweed

```
sudo zypper install opi
```

## Leap and SLE

```
# Leap 15.0
sudo zypper addrepo --refresh https://download.opensuse.org/repositories/home:guoyunhe/openSUSE_Leap_15.0/home:guoyunhe.repo
# Leap 15.1
sudo zypper addrepo --refresh https://download.opensuse.org/repositories/home:guoyunhe/openSUSE_Leap_15.1/home:guoyunhe.repo
# Leap 42.3
sudo zypper addrepo --refresh https://download.opensuse.org/repositories/home:guoyunhe/openSUSE_Leap_42.3/home:guoyunhe.repo
# SLE 15
sudo zypper addrepo --refresh https://download.opensuse.org/repositories/home:guoyunhe/SLE_15/home:guoyunhe.repo

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

**Packman Codecs** (enable you to play MP4 videos and YouTube)

```
opi packman

# or

opi codecs
```

**Skype**

```
opi skype
```

**Visual Studio Code**

```
opi vs code
```

**Miscrosoft Teams**

```
opi teams
```
