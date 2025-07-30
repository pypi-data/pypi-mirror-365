#PCalendar - Persian Calendar Library

A comprehensive Python library for working with the Persian (Solar Hijri) calendar. This library provides functionality for conversion between Persian and Gregorian calendars, date manipulation, and formatting.

## Features

- **Accurate Calendar Conversion**: Convert between Persian (Solar Hijri) and Gregorian calendars
- **Date Arithmetic**: Add/subtract time intervals and compare dates
- **Flexible Formatting**: Format dates with customizable Persian and English patterns
- **Leap Year Support**: Proper handling of Persian leap years
- **Timezone Aware**: Support for UTC and local timezone operations
- **Pure Python**: No external dependencies, uses only Python standard library

## Installation

```bash
pip install pcalendar
```

## Quick Start

```python
from pcalendar import from_gregorian_date, now, from_persian_date

# Convert Gregorian to Persian
persian_date = from_gregorian_date(2024, 1, 1)
print(f"Gregorian 2024/1/1 = Persian {persian_date.tm_year}/{persian_date.tm_mon + 1}/{persian_date.tm_mday}")

# Get current Persian date
today = now()
print(f"Today: {today.to_string('yyyy/MM/dd E')}")

# Create Persian date
nowruz = from_persian_date(1403, 1, 1)  # Persian New Year 1403
print(f"Nowruz 1403: {nowruz.to_string('yyyy MMM dd E')}")

# Date arithmetic
tomorrow = today + 86400  # Add one day (86400 seconds)
print(f"Tomorrow: {tomorrow.to_string('yyyy/MM/dd')}")
```

## Usage Examples

### Creating Persian Dates

```python
from pcalendar import from_persian_date, from_gregorian_date, from_persian_components

# From Persian date
persian_date = from_persian_date(1400, 0, 1)  # 1st Farvardin 1400 (months are 0-indexed)

# From Gregorian date
persian_from_greg = from_gregorian_date(2021, 3, 21)

# With time components
precise_date = from_persian_components(1400, 0, 1, 14, 30, 0, 0)  # 2:30 PM
```

### Date Formatting

The library supports extensive formatting options:

```python
date = from_persian_date(1400, 0, 15)

# Various format examples
print(date.to_string("yyyy/MM/dd"))           # 1400/01/15
print(date.to_string("yyyy MMM dd"))          # 1400 فروردین 15
print(date.to_string("E, dd MMM yyyy"))       # دوشنبه, 15 فروردین 1400
print(date.to_string("yyyy-MM-dd HH:mm:ss"))  # 1400-01-15 00:00:00
```

### Format Specifiers

| Format | Description | Example |
|--------|-------------|---------|
| `yyyy` | 4-digit year | 1400 |
| `yy` | 2-digit year | 00 |
| `MMM` | Persian month name | فروردین |
| `MM` | 2-digit month | 01 |
| `M` | Month | 1 |
| `dd` | 2-digit day | 15 |
| `d` | Day | 15 |
| `E` | Persian weekday name | دوشنبه |
| `e` | Persian weekday short | د |
| `HH` | 24-hour format hour | 14 |
| `hh` | 12-hour format hour | 02 |
| `mm` | Minutes | 30 |
| `ss` | Seconds | 45 |
| `a` | AM/PM in Persian | ب.ظ |

### Date Arithmetic and Comparison

```python
from pcalendar import now

date1 = now()
date2 = date1 + 3600  # Add one hour

# Comparison
print(date2 > date1)  # True

# Calculate difference
diff = date2 - date1  # Returns seconds
print(f"Difference: {diff} seconds")

# Convert to different timezones
utc_date = date1.to_utc()
local_date = utc_date.to_local()
```

### Working with Timestamps

```python
from pcalendar import at, at_utc
import time

# From Unix timestamp
timestamp = time.time()
persian_time = at(timestamp)          # Local timezone
persian_utc = at_utc(timestamp)       # UTC

# Convert to timestamp
unix_timestamp = persian_time.to_timestamp()
```

### Leap Year Handling

```python
from pcalendar import from_persian_date

# Check if a Persian year is leap
date = from_persian_date(1399, 0, 1)  # Year 1399 is a leap year
print(date.is_leap())  # True

# Leap years have 30 days in Esfand (month 11), normal years have 29
leap_esfand = from_persian_date(1399, 11, 30)  # Valid
normal_esfand = from_persian_date(1400, 11, 30)  # None (invalid)
```

## Calendar System

The Persian calendar (Solar Hijri) used in Iran, Afghanistan, and other regions:

- **Year**: Starts with spring equinox (around March 21)
- **Months**: 
  - First 6 months: 31 days each (Farvardin to Shahrivar)
  - Next 5 months: 30 days each (Mehr to Bahman)
  - Last month (Esfand): 29 days (30 in leap years)
- **Week**: Starts with Shanbeh (Saturday)
- **Leap Years**: Follow a 33-year cycle

### Month Names

| Index | Persian Name | Transliteration | Days |
|-------|--------------|-----------------|------|
| 0 | فروردین | Farvardin | 31 |
| 1 | اردیبهشت | Ordibehesht | 31 |
| 2 | خرداد | Khordad | 31 |
| 3 | تیر | Tir | 31 |
| 4 | مرداد | Mordad | 31 |
| 5 | شهریور | Shahrivar | 31 |
| 6 | مهر | Mehr | 30 |
| 7 | آبان | Aban | 30 |
| 8 | آذر | Azar | 30 |
| 9 | دی | Dey | 30 |
| 10 | بهمن | Bahman | 30 |
| 11 | اسفند | Esfand | 29/30 |

### Weekday Names

| Index | Persian Name | Transliteration |
|-------|--------------|-----------------|
| 0 | شنبه | Shanbeh (Saturday) |
| 1 | یک‌شنبه | Yekshanbeh (Sunday) |
| 2 | دوشنبه | Doshanbeh (Monday) |
| 3 | سه‌شنبه | Seshhanbeh (Tuesday) |
| 4 | چهارشنبه | Chaharshanbeh (Wednesday) |
| 5 | پنج‌شنبه | Panjshanbeh (Thursday) |
| 6 | جمعه | Jomeh (Friday) |


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgments
- Persian calendar calculations based on Kazimierz M. Borkowski's algorithms
- Thanks to the Persian calendar research community

## License

This project is licensed under the GNU General Public License v3.0  see the `LICENSE` file for details.

