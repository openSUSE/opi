# OPI

**O**BS **P**ackage **I**nstaller

Search and install almost all packages available for openSUSE and SLE:

1. openSUSE Build Service
2. Packman
3. Popular packages for Microsoft and other vendors

## System Requirements

- openSUSE Tumbleweed, openSUSE Leap 42.1+, SLE 12+
- python3
- python3-requests
- python3-lxml
- python3-termcolor

If you want to use dnf instead of zypper, you also need:
- dnf
- libdnf-repo-config-zypp

## Install

### openSUSE Tumbleweed and Leap

```
sudo zypper install opi
```

### SLE

```
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

### Using DNF instead of Zypper
If you want to, you can use [DNF](https://en.opensuse.org/SDB:DNF) instead of Zypper.
To do this, change the content of `~/.config/opi/config.json` so that it looks like this:

```json
{
  "backend": "dnf"
}
```

If you want to go back to Zypper, just change the value of `backend` back to `zypp`.

### Packages from Other Repositories

**Packman Codecs** (enable you to play MP4 videos and YouTube)

```
opi packman

# or

opi codecs
```

```
usage: opi [-h] [-v] [-r] [query [query ...]]

openSUSE Package Installer
==========================

Search and install almost all packages available for openSUSE and SLE:
  1. openSUSE Build Service
  2. Packman
  2. Popular packages for various vendors

positional arguments:
  query                 can be any package name or part of it and will be
                        searched for both at the openSUSE Build Service and
                        Packman.
                        If multiple query arguments are provided only results
                        matching all of them are returned.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -r, --reversed-output
                        print the search results in reverse

Also these queries can be used to install packages from various other vendors:
  atom              Atom Text Editor
  brave             Brave web browser
  chrome            Google Chrome web browser
  codecs            Media Codecs from Packman and official repo
  dotnet            Microsoft .NET
  megasync          Mega Desktop App
  msedge-beta       Microsoft Edge Beta
  msedge-dev        Microsoft Edge Dev
  msteams           Microsoft Teams
  plex              Plex Media Server
  skype             Microsoft Skype
  slack             Slack messenger
  sublime           Editor for code, markup and prose
  teamviewer        TeamViewer remote access
  vivaldi           Vivaldi web browser
  vscode            Microsoft Visual Studio Code
  vscodium          Visual Studio Codium
  yandex-disk       Yandex.Disk cloud storage client
  zoom              Zoom Video Conference
```
