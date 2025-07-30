# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to the principles of [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-07-29

### Added
- New calendar-related methods in the `Tm` class:
  - `get_quarter()` – Returns the quarter of the Persian year.
  - `get_week_number()` – Returns the simple week number based on `tm_yday`.
  - `get_week_number_iso()` – Returns an ISO-style week number for the Persian calendar.
  - `is_weekend()` – Identifies if the day is an Iranian weekend (Thursday or Friday).
  - `is_workday()` – Identifies if the day is a working day (Saturday to Wednesday).
  - `week_start_date()` – Gets the `Tm` object representing the start of the week (Shanbeh).
  - `days_in_month()` – Returns the number of days in the current Persian month.
  - `calendar_grid()` – Returns a 6-week calendar grid (42 days) for the current Persian month.

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
