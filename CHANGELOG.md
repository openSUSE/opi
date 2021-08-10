# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.1] - 2021-08-10

### Added

- Plugin for Brave Browser [#60](https://github.com/openSUSE/opi/pull/60)

## [2.1.0] - 2021-07-05

### Added

- Support for dnf backend [#58](https://github.com/openSUSE/opi/pull/58)

### Changed

- Deduplicated packman repo creation code

## [2.0.0] - 2021-05-03

### Added

- [Automated tests](https://github.com/openSUSE/opi/actions)
- Extensible Plugin interface for plugins (eg. [this one](https://github.com/openSUSE/opi/blob/master/opi/plugins/vivaldi.py))
- Added plugins for chrome, dotnet, edge, teams, packman, plex, skype, slack, teamviewer, vivaldi, vscode, vscodium, zoom

### Changed

- Rewrote the complete tool in python3

## [0.10.0] - 2021-01-17

### Added

- Microsoft Teams installer [#34](https://github.com/openSUSE/opi/pulls/34)
- Warning for personal repository [#35](https://github.com/openSUSE/opi/pulls/35)

## [0.9.0] - 2020-10-03

### Added

- Help (-h, --help) and version (-v, --version) option

### Changed

- Filter out -devel, -docs and -lang packages [#30](https://github.com/openSUSE/opi/pulls/30)
- Don't show i586 packages on x86_64 system

## [0.8.3] - 2020-07-25

### Fixed

- ffmpeg/libav packages due to Packman update

## [0.8.2] - 2020-05-16

### Fixed

- Ghost process on XML parsing failure [#27](https://github.com/openSUSE/opi/pulls/27)

## [0.8.1] - 2020-04-03

### Fixed

- OBS limit error when searching php, test, etc.

## [0.8.0]

### Changed

- Type number `0` to exit [#26](https://github.com/openSUSE/opi/pulls/26)

## [0.7.1]

### Fixed

- Missing `use File::Temp;` [#24](https://github.com/openSUSE/opi/issues/24)

## [0.7.0]

### Changed

- Force repo URL to HTTPS [#22](https://github.com/openSUSE/opi/issues/22)

### Fixed

- Ctrl + C handling of spinner

## [0.6.0]

### Added

- Search spinner [#21](https://github.com/openSUSE/opi/issues/21)

### Fixed

- Packman repo doesn't have *.repo file [#19](https://github.com/openSUSE/opi/issues/19)
- Long version numbers are cutted [#17](https://github.com/openSUSE/opi/issues/17)

## [0.5.2]

### Fixed

- Trim "NAME" and "VERSION" string [#13](https://github.com/openSUSE/opi/issues/13)

## [0.5.1]

### Fixed

- Fix dependency not found issue [#11](https://github.com/openSUSE/opi/issues/11)

## [0.5.0]

### Added

- API proxy server to prevent hard-coded passwords in the script [#4](https://github.com/openSUSE/opi/issues/4)

## [0.4.0]

### Added

- PMBS (Packman Build Service) support [#5](https://github.com/openSUSE/opi/issues/5)

## [0.3.2]

### Fixed

- `opi opi` cannot find `opi` [#9](https://github.com/openSUSE/opi/issues/9)

## [0.3.1]

### Fixed

- Remove quotes from version number. So Leap and SLE can search packages.

## [0.3.0]

### Added

- Support SLE [#8](https://github.com/openSUSE/opi/issues/8)

### Changed

- Better print column alignment

## [0.2.0]

### Added

- Install Packman Codecs with `opi packman` or `opi codecs` [#6](https://github.com/openSUSE/opi/issues/6)
- Install Skype with `opi skype` [#6](https://github.com/openSUSE/opi/issues/6)
- Install VS Code with `opi vs code` [#6](https://github.com/openSUSE/opi/issues/6)

## [0.1.2]

### Fixed

- Fixed lost of "noarch" packages [#3](https://github.com/openSUSE/opi/issues/3)
- Be able to search with dashes in keywords [#2](https://github.com/openSUSE/opi/issues/2)

## [0.1.1]

### Fixed

- Removed XML dump which may cause problems.

## [0.1.0]

### Added

- Search packages from OBS
- List properly sorted search result
- Use different colors for official, experimental and personal projects
- Choose package and install
- Keep or remove repository after installation

[Unreleased]: https://github.com/openSUSE/opi/compare/v0.10.0...HEAD
[0.10.0]: https://github.com/openSUSE/opi/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/openSUSE/opi/compare/v0.8.3...v0.9.0
[0.8.3]: https://github.com/openSUSE/opi/compare/v0.8.2...v0.8.3
[0.8.2]: https://github.com/openSUSE/opi/compare/v0.8.1...v0.8.2
[0.8.1]: https://github.com/openSUSE/opi/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/openSUSE/opi/compare/v0.7.1...v0.8.0
[0.7.1]: https://github.com/openSUSE/opi/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/openSUSE/opi/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/openSUSE/opi/compare/v0.5.2...v0.6.0
[0.5.2]: https://github.com/openSUSE/opi/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/openSUSE/opi/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/openSUSE/opi/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/openSUSE/opi/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/openSUSE/opi/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/openSUSE/opi/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/openSUSE/opi/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/openSUSE/opi/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/openSUSE/opi/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/openSUSE/opi/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/openSUSE/opi/releases/tag/v0.1.0
