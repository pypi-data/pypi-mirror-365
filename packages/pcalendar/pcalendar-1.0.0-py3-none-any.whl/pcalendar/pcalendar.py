"""
Persian Calendar Library - Python Implementation

Provides functionality for conversion between Persian (Solar Hijri) and Gregorian calendars.
A Julian calendar is used as an interface for all conversions.


Example:
    >>> from pcalendar import from_gregorian_date
    >>> p_tm = from_gregorian_date(2016, 2, 21)
    >>> print(p_tm.tm_year)  # 1395
    >>> print(p_tm.tm_mon)   # 0
    >>> print(p_tm.tm_mday)  # 2
"""

import time
import math
from datetime import datetime, timezone
from typing import Optional, Union


class Tm:
    """Represents the components of a moment in time in Persian Calendar."""
    
    def __init__(self, tm_sec: int = 0, tm_min: int = 0, tm_hour: int = 0,
                 tm_mday: int = 0, tm_mon: int = 0, tm_year: int = 0,
                 tm_wday: int = 0, tm_yday: int = 0, tm_isdst: int = 0,
                 tm_utcoff: int = 0, tm_nsec: int = 0):
        """
        Initialize a Persian time object.
        
        Args:
            tm_sec: seconds [0-59]
            tm_min: minutes [0-59]
            tm_hour: hours [0-23]
            tm_mday: day of month [1-31]
            tm_mon: month since Farvardin [0-11]
            tm_year: year
            tm_wday: weekday since Shanbeh [0-6]. 0=Shanbeh, 6=Jomeh
            tm_yday: day of year since Farvardin 1 [0-365]
            tm_isdst: daylight saving time flag
            tm_utcoff: UTC offset in seconds
            tm_nsec: nanoseconds
        """
        self.tm_sec = tm_sec
        self.tm_min = tm_min
        self.tm_hour = tm_hour
        self.tm_mday = tm_mday
        self.tm_mon = tm_mon
        self.tm_year = tm_year
        self.tm_wday = tm_wday
        self.tm_yday = tm_yday
        self.tm_isdst = tm_isdst
        self.tm_utcoff = tm_utcoff
        self.tm_nsec = tm_nsec
    
    def __str__(self) -> str:
        return self.to_string("yyyy-MM-ddTHH:mm:ss.ns")
    
    def __repr__(self) -> str:
        return f"Tm(year={self.tm_year}, month={self.tm_mon}, day={self.tm_mday})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Tm):
            return False
        return (self.tm_sec == other.tm_sec and self.tm_min == other.tm_min and
                self.tm_hour == other.tm_hour and self.tm_mday == other.tm_mday and
                self.tm_mon == other.tm_mon and self.tm_year == other.tm_year and
                self.tm_wday == other.tm_wday and self.tm_yday == other.tm_yday and
                self.tm_isdst == other.tm_isdst and self.tm_utcoff == other.tm_utcoff and
                self.tm_nsec == other.tm_nsec)
    
    def __lt__(self, other) -> bool:
        return self.to_timestamp() < other.to_timestamp()
    
    def __le__(self, other) -> bool:
        return self.to_timestamp() <= other.to_timestamp()
    
    def __gt__(self, other) -> bool:
        return self.to_timestamp() > other.to_timestamp()
    
    def __ge__(self, other) -> bool:
        return self.to_timestamp() >= other.to_timestamp()
    
    def __add__(self, seconds: Union[int, float]) -> 'Tm':
        """Add seconds to this time."""
        return at_utc(self.to_timestamp() + seconds)
    
    def __sub__(self, other: Union['Tm', int, float]) -> Union['Tm', float]:
        """Subtract time or seconds from this time."""
        if isinstance(other, Tm):
            return self.to_timestamp() - other.to_timestamp()
        else:
            return at_utc(self.to_timestamp() - other)
    
    def to_gregorian(self) -> time.struct_time:
        """Convert Persian calendar to Gregorian calendar."""
        jdn = _get_jdn(self.tm_year, self.tm_mon + 1, self.tm_mday)
        
        if jdn > 2299160:
            l = jdn + 68569
            n = 4 * l // 146097
            l = l - (146097 * n + 3) // 4
            i = 4000 * (l + 1) // 1461001
            l = l - 1461 * i // 4 + 31
            j = 80 * l // 2447
            day = l - 2447 * j // 80
            l = j // 11
            month = j + 2 - 12 * l
            year = 100 * (n - 49) + i + l
        else:
            j = jdn + 1402
            k = (j - 1) // 1461
            l = j - 1461 * k
            n = (l - 1) // 365 - l // 1461
            i = l - 365 * n + 30
            j = 80 * i // 2447
            day = i - 2447 * j // 80
            i = j // 11
            month = j + 2 - 12 * i
            year = 4 * k + n + i - 4716
        
        return time.struct_time((
            year,
            month,
            day,
            self.tm_hour,
            self.tm_min,
            self.tm_sec,
            _get_gregorian_weekday(self.tm_wday),
            _get_gregorian_yday(year, month - 1, day),
            self.tm_isdst
        ))
    
    def to_timestamp(self) -> float:
        """Return the number of seconds since January 1, 1970 UTC."""
        greg_tm = self.to_gregorian()
        dt = datetime(greg_tm.tm_year, greg_tm.tm_mon, greg_tm.tm_mday,
                     greg_tm.tm_hour, greg_tm.tm_min, greg_tm.tm_sec,
                     self.tm_nsec // 1000, timezone.utc)
        return dt.timestamp()
    
    def is_leap(self) -> bool:
        """Return True if the year is a leap year."""
        return _is_persian_leap(self.tm_year)
    
    def to_local(self) -> 'Tm':
        """Convert time to the local timezone."""
        if self.tm_utcoff == 0:
            return at(self.to_timestamp())
        else:
            return self
    
    def to_utc(self) -> 'Tm':
        """Convert time to UTC."""
        if self.tm_utcoff == 0:
            return self
        else:
            return at_utc(self.to_timestamp())
    
    def to_string(self, format_str: str) -> str:
        """
        Return the formatted representation of time.
        
        Format specifiers:
            yyyy, yyy, y     year (e.g. 1394)
            yy               2-digits representation of year (e.g. 94)
            MMM              the Persian name of month (e.g. فروردین)
            MM               2-digits representation of month (e.g. 01)
            M                month (e.g. 1)
            DD               day of year (starting from 1)
            D                day of year (starting from 0)
            dd               2-digits representation of day (e.g. 01)
            d                day (e.g. 1)
            E                the Persian name of weekday (e.g. شنبه)
            e                the Persian short name of weekday (e.g. ش)
            A                the Persian name of 12-Hour marker (e.g. قبل از ظهر)
            a                the Persian short name of 12-Hour marker (e.g. ق.ظ)
            HH               2-digits representation of hour [00-23]
            H                hour [0-23]
            kk               2-digits representation of hour [01-24]
            k                hour [1-24]
            hh               2-digits representation of hour [01-12]
            h                hour [1-12]
            KK               2-digits representation of hour [00-11]
            K                hour [0-11]
            mm               2-digits representation of minute [00-59]
            m                minute [0-59]
            ss               2-digits representation of seconds [00-59]
            s                seconds [0-59]
            ns               nanoseconds
        """
        result = format_str
        
        # Year formats
        year_str = str(self.tm_year)
        result = result.replace("yyyy", year_str)
        result = result.replace("yyy", year_str)
        result = result.replace("yy", year_str[-2:] if len(year_str) >= 2 else year_str)
        result = result.replace("y", year_str)
        
        # Month formats
        month_names = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        if 0 <= self.tm_mon <= 11:
            result = result.replace("MMM", month_names[self.tm_mon])
        result = result.replace("MM", f"{self.tm_mon + 1:02d}")
        result = result.replace("M", str(self.tm_mon + 1))
        
        # Day formats
        result = result.replace("DD", str(self.tm_yday + 1))
        result = result.replace("D", str(self.tm_yday))
        result = result.replace("dd", f"{self.tm_mday:02d}")
        result = result.replace("d", str(self.tm_mday))
        
        # Weekday formats
        weekday_names = ["شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
        weekday_short = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
        if 0 <= self.tm_wday <= 6:
            result = result.replace("E", weekday_names[self.tm_wday])
            result = result.replace("e", weekday_short[self.tm_wday])
        
        # AM/PM formats
        result = result.replace("A", "قبل از ظهر" if self.tm_hour < 12 else "بعد از ظهر")
        result = result.replace("a", "ق.ظ" if self.tm_hour < 12 else "ب.ظ")
        
        # Hour formats
        result = result.replace("HH", f"{self.tm_hour:02d}")
        result = result.replace("H", str(self.tm_hour))
        result = result.replace("kk", f"{self.tm_hour + 1:02d}")
        result = result.replace("k", str(self.tm_hour + 1))
        
        hour_12 = (self.tm_hour % 12) + 1 if self.tm_hour % 12 != 0 else 12
        result = result.replace("hh", f"{hour_12:02d}")
        result = result.replace("h", str(hour_12))
        
        hour_k = self.tm_hour % 12
        result = result.replace("KK", f"{hour_k:02d}")
        result = result.replace("K", str(hour_k))
        
        # Minute formats
        result = result.replace("mm", f"{self.tm_min:02d}")
        result = result.replace("m", str(self.tm_min))
        
        # Second formats
        result = result.replace("ss", f"{self.tm_sec:02d}")
        result = result.replace("s", str(self.tm_sec))
        
        # Nanosecond format
        result = result.replace("ns", str(self.tm_nsec))
        
        return result


def empty_tm() -> Tm:
    """Create an empty Persian time object."""
    return Tm()


def from_gregorian(gregorian_tm: time.struct_time) -> Tm:
    """Convert Gregorian calendar to Persian calendar."""
    gy = gregorian_tm.tm_year
    gm = gregorian_tm.tm_mon
    gd = gregorian_tm.tm_mday
    
    if gy > 1582 or (gy == 1582 and gm > 10) or (gy == 1582 and gm == 10 and gd > 14):
        jdn = ((1461 * (gy + 4800 + ((gm - 14) // 12))) // 4 + 
               (367 * (gm - 2 - 12 * ((gm - 14) // 12))) // 12 - 
               (3 * ((gy + 4900 + ((gm - 14) // 12)) // 100)) // 4 + 
               gd - 32075)
    else:
        jdn = (367 * gy - (7 * (gy + 5001 + ((gm - 9) // 7))) // 4 + 
               (275 * gm) // 9 + gd + 1729777)
    
    dep = jdn - _get_jdn(475, 1, 1)
    cyc = dep // 1029983
    rem = dep % 1029983
    
    if rem == 1029982:
        ycyc = 2820
    else:
        a = rem // 366
        ycyc = (2134 * a + 2816 * (rem % 366) + 2815) // 1028522 + a + 1
    
    year = ycyc + 2820 * cyc + 474
    if year <= 0:
        year -= 1
    
    dy = jdn - _get_jdn(year, 1, 1) + 1
    
    if dy <= 186:
        month = math.ceil(dy / 31.0) - 1
    else:
        month = math.ceil((dy - 6) / 30.0) - 1
    
    day = jdn - _get_jdn(year, month + 1, 1) + 1
    
    return Tm(
        tm_sec=gregorian_tm.tm_sec,
        tm_min=gregorian_tm.tm_min,
        tm_hour=gregorian_tm.tm_hour,
        tm_mday=day,
        tm_mon=month,
        tm_year=year,
        tm_wday=_get_persian_weekday(gregorian_tm.tm_wday),
        tm_yday=_get_persian_yday(month, day),
        tm_isdst=gregorian_tm.tm_isdst,
        tm_utcoff=0,
        tm_nsec=0
    )


def from_gregorian_date(g_year: int, g_month: int, g_day: int) -> Optional[Tm]:
    """Create a new instance of Persian time from Gregorian date."""
    return from_gregorian_components(g_year, g_month, g_day, 0, 0, 0, 0)


def from_persian_date(p_year: int, p_month: int, p_day: int) -> Optional[Tm]:
    """Create a new instance of Persian time from Persian date."""
    return from_persian_components(p_year, p_month, p_day, 0, 0, 0, 0)


def from_gregorian_components(g_year: int, g_month: int, g_day: int, 
                            hour: int, minute: int, second: int, nanosecond: int) -> Optional[Tm]:
    """Create a new instance of Persian time from Gregorian date components."""
    if (_is_time_valid(hour, minute, second, nanosecond) and 
        _is_gregorian_date_valid(g_year, g_month, g_day)):
        
        gregorian_tm = time.struct_time((
            g_year, g_month, g_day, hour, minute, second, 0, 0, 0
        ))
        
        result = from_gregorian(gregorian_tm)
        result.tm_nsec = nanosecond
        return result
    
    return None


def from_persian_components(p_year: int, p_month: int, p_day: int,
                          hour: int, minute: int, second: int, nanosecond: int) -> Optional[Tm]:
    """Create a new instance of Persian time from Persian date components."""
    if (_is_time_valid(hour, minute, second, nanosecond) and 
        _is_persian_date_valid(p_year, p_month, p_day)):
        
        tm = Tm(
            tm_sec=second,
            tm_min=minute,
            tm_hour=hour,
            tm_mday=p_day,
            tm_mon=p_month,
            tm_year=p_year,
            tm_wday=0,
            tm_yday=_get_persian_yday(p_month, p_day),
            tm_isdst=0,
            tm_utcoff=0,
            tm_nsec=nanosecond
        )
        
        # Calculate weekday by converting to Gregorian
        greg_tm = tm.to_gregorian()
        tm.tm_wday = _get_persian_weekday(greg_tm.tm_wday)
        
        return tm
    
    return None


def at_utc(timestamp: float) -> Tm:
    """Create a new instance of Persian time from timestamp in UTC."""
    dt = datetime.fromtimestamp(timestamp, timezone.utc)
    gregorian_tm = dt.timetuple()
    result = from_gregorian(gregorian_tm)
    result.tm_nsec = dt.microsecond * 1000
    return result


def at(timestamp: float) -> Tm:
    """Create a new instance of Persian time from timestamp in local timezone."""
    dt = datetime.fromtimestamp(timestamp)
    gregorian_tm = dt.timetuple()
    result = from_gregorian(gregorian_tm)
    result.tm_nsec = dt.microsecond * 1000
    return result


def now_utc() -> Tm:
    """Create a new instance of Persian time corresponding to the current time in UTC."""
    return at_utc(time.time())


def now() -> Tm:
    """Create a new instance of Persian time corresponding to the current time in local timezone."""
    return at(time.time())


# Helper functions

def _divider(num: int, den: int) -> int:
    """Custom division function matching Rust implementation."""
    if num > 0:
        return num % den
    else:
        return num - ((((num + 1) // den) - 1) * den)


def _get_jdn(year: int, month: int, day: int) -> int:
    """Calculate Julian Day Number for Persian date."""
    base = year - 474 if year >= 0 else year - 473
    epy = 474 + (base % 2820)
    
    if month <= 7:
        md = (month - 1) * 31
    else:
        md = (month - 1) * 30 + 6
    
    return (day + md + (epy * 682 - 110) // 2816 + 
            (epy - 1) * 365 + base // 2820 * 1029983 + 1948320)


def _get_persian_weekday(wd: int) -> int:
    """Convert Gregorian weekday to Persian weekday."""
    conversion = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}
    if wd not in conversion:
        raise ValueError(f"Invalid weekday value: {wd}")
    return conversion[wd]


def _get_gregorian_weekday(wd: int) -> int:
    """Convert Persian weekday to Gregorian weekday."""
    conversion = {0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}
    if wd not in conversion:
        raise ValueError(f"Invalid weekday value: {wd}")
    return conversion[wd]


def _get_persian_yday(month: int, day: int) -> int:
    """Calculate Persian year day."""
    month_starts = [0, 31, 62, 93, 124, 155, 186, 216, 246, 276, 306, 336]
    return month_starts[month] + day - 1


def _get_gregorian_yday(year: int, month: int, day: int) -> int:
    """Calculate Gregorian year day."""
    month_starts_normal = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    month_starts_leap = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    
    if _is_gregorian_leap(year):
        return month_starts_leap[month] + day - 1
    else:
        return month_starts_normal[month] + day - 1


def _is_persian_leap(year: int) -> bool:
    """Check if Persian year is a leap year."""
    return _divider(25 * year + 11, 33) < 8


def _is_gregorian_leap(year: int) -> bool:
    """Check if Gregorian year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _is_persian_date_valid(year: int, month: int, day: int) -> bool:
    """Validate Persian date."""
    if month < 0 or month > 11:
        return False
    
    # Days in each month [normal_year, leap_year]
    days_in_month = [
        [31, 31], [31, 31], [31, 31], [31, 31], [31, 31], [31, 31],
        [30, 30], [30, 30], [30, 30], [30, 30], [30, 30], [29, 30]
    ]
    
    max_days = days_in_month[month][1 if _is_persian_leap(year) else 0]
    return 1 <= day <= max_days


def _is_gregorian_date_valid(year: int, month: int, day: int) -> bool:
    """Validate Gregorian date."""
    if month < 1 or month > 12:
        return False
    
    # Days in each month [normal_year, leap_year]
    days_in_month = [
        [31, 31], [28, 29], [31, 31], [30, 30], [31, 31], [30, 30],
        [31, 31], [31, 31], [30, 30], [31, 31], [30, 30], [31, 31]
    ]
    
    max_days = days_in_month[month - 1][1 if _is_gregorian_leap(year) else 0]
    return 1 <= day <= max_days


def _is_time_valid(hour: int, minute: int, second: int, nanosecond: int) -> bool:
    """Validate time components."""
    return (0 <= hour <= 23 and 0 <= minute <= 59 and 
            0 <= second <= 59 and 0 <= nanosecond <= 999999999)


# Example usage and tests
if __name__ == "__main__":
    # Test the example from the original documentation
    p_tm = from_gregorian_date(2016, 2, 21)
    if p_tm:
        print(f"Year: {p_tm.tm_year}")    # Should be 1395
        print(f"Month: {p_tm.tm_mon}")    # Should be 0 (Farvardin is 0-indexed)
        print(f"Day: {p_tm.tm_mday}")     # Should be 2
        print(f"Formatted: {p_tm.to_string('yyyy/MM/dd')}")
        print(f"Full format: {p_tm}")
    
    # Test current time
    current_persian = now()
    print(f"Current Persian date: {current_persian.to_string('yyyy/MM/dd E')}")
    
    # Test Persian to Gregorian conversion
    persian_date = from_persian_date(1400, 0, 1)  # 1st of Farvardin 1400
    if persian_date:
        gregorian = persian_date.to_gregorian()
        print(f"Persian 1400/01/01 = Gregorian {gregorian.tm_year}/{gregorian.tm_mon}/{gregorian.tm_mday}")