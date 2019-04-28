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
sudo zypper install perl perl-libwww-perl perl-XML-LibXML perl-URI perl-Config-Tiny
wget https://github.com/openSUSE-zh/opi/raw/master/opi
install opi ~/bin
```

## Use

Command:

```
./opi pcsx2
```

Output:

```
1. pcsx2
2. pcsx2-32bit
3. pcsx2-git
Choose a number: 1
You have selected package name: pcsx2
1. Emulators + | 1.5.0~git20190426 | i586
2. home:bosconovic:branches:Emulators ? | 1.5.0~git20190426 | i586
3. home:deabru:games ? | 1.5.0~git20190426 | i586
4. home:cabelo ? | 1.5.0~git20180228 | i586
5. home:creamcast ? | master | i586
Choose a number: 1
```
