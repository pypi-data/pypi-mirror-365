# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to the principles of [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-28

### Added
- Initial public release of `pcalendar` under the GPLv3 license.
- Support for Persian (Solar Hijri) ? Gregorian date conversion.
- `Tm` class to represent parsed or constructed Persian time values.
- Conversion from:
  - Gregorian `date` object
  - Gregorian components (year, month, day)
  - Persian components (year, month, day)
- Utility functions:
  - `now()` and `now_utc()` for current Persian time
  - `at()` and `at_utc()` to construct time objects from timestamps
  - `empty_tm()` for zero-initialized Persian time structure
- Python 3.7+ compatibility.
- No external dependencies (pure standard library).

### Changed
- N/A

### Fixed
- N/A

---

