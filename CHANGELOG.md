# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- API proxy server to prevent hard-coded passwords in the script [#4](https://github.com/openSUSE-zh/opi/issues/4)

## [0.4.0]

### Added

- PMBS (Packman Build Service) support [#5](https://github.com/openSUSE-zh/opi/issues/5)

## [0.3.2]

### Fixed

- `opi opi` cannot find `opi` [#9](https://github.com/openSUSE-zh/opi/issues/9)

## [0.3.1]

### Fixed

- Remove quotes from version number. So Leap and SLE can search packages.

## [0.3.0]

### Added

- Support SLE [#8](https://github.com/openSUSE-zh/opi/issues/8)

### Changed

- Better print column alignment

## [0.2.0]

### Added

- Install Packman Codecs with `opi packman` or `opi codecs` [#6](https://github.com/openSUSE-zh/opi/issues/6)
- Install Skype with `opi skype` [#6](https://github.com/openSUSE-zh/opi/issues/6)
- Install VS Code with `opi vs code` [#6](https://github.com/openSUSE-zh/opi/issues/6)

## [0.1.2]

### Fixed

- Fixed lost of "noarch" packages [#3](https://github.com/openSUSE-zh/opi/issues/3)
- Be able to search with dashes in keywords [#2](https://github.com/openSUSE-zh/opi/issues/3)

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

[Unreleased]: https://github.com/openSUSE-zh/opi/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/openSUSE-zh/opi/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/openSUSE-zh/opi/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/openSUSE-zh/opi/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/openSUSE-zh/opi/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/openSUSE-zh/opi/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/openSUSE-zh/opi/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/openSUSE-zh/opi/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/openSUSE-zh/opi/releases/tag/v0.1.0
