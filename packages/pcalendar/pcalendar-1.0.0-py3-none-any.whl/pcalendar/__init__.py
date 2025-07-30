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

__version__ = "1.0.0"
__author__ = "Ali Miracle"
__email__ = "alimiracle@riseup.net"
__license__ = "GPLv3"

from .pcalendar import (
    # Main class
    Tm,

    # Creation functions
    empty_tm,
    from_gregorian,
    from_gregorian_date,
    from_persian_date,
    from_gregorian_components,
    from_persian_components,

    # Time functions
    at_utc,
    at,
    now_utc,
    now,
)

__all__ = [
    # Main class
    "Tm",

    # Creation functions
    "empty_tm",
    "from_gregorian",
    "from_gregorian_date",
    "from_persian_date",
    "from_gregorian_components",
    "from_persian_components",

    # Time functions
    "at_utc",
    "at",
    "now_utc",
    "now",
]
