"""
Utility functions for IOR log parsing.
"""

from datetime import datetime
from typing import Optional


def parse_size_to_bytes(size_str: str) -> Optional[int]:
    """
    Parse size strings like '1 MiB', '4 MiB', '512 MiB' into bytes.

    Args:
        size_str: Size string with value and unit (e.g., "1 MiB", "4 GiB")

    Returns:
        Size in bytes, or None if parsing fails

    Examples:
        >>> parse_size_to_bytes("1 MiB")
        1048576
        >>> parse_size_to_bytes("4 GiB")
        4294967296
        >>> parse_size_to_bytes("512 MB")
        512000000
        >>> parse_size_to_bytes("invalid")
        None
    """
    if not size_str:
        return None

    parts = size_str.strip().split()
    if len(parts) != 2:
        return None

    try:
        value = float(parts[0])
        unit = parts[1]

        # Convert to bytes
        unit_multipliers = {
            "B": 1,
            "KiB": 1024,
            "MiB": 1024**2,
            "GiB": 1024**3,
            "TiB": 1024**4,
            "KB": 1000,
            "MB": 1000**2,
            "GB": 1000**3,
            "TB": 1000**4,
        }

        if unit in unit_multipliers:
            return int(value * unit_multipliers[unit])
        return None
    except (ValueError, IndexError):
        return None


def parse_datetime_to_timestamp(date_str: str) -> Optional[int]:
    """
    Parse datetime strings like 'Sun Jul 27 08:35:34 2025' to Unix timestamp.

    Args:
        date_str: Datetime string in IOR format (e.g., "Sun Jul 27 08:35:34 2025")

    Returns:
        Unix timestamp as integer, or None if parsing fails

    Examples:
        >>> parse_datetime_to_timestamp("Sun Jul 27 08:35:34 2025")
        1753630534
        >>> parse_datetime_to_timestamp("Mon Jan 01 00:00:00 2024")
        1704067200
        >>> parse_datetime_to_timestamp("invalid")
        None
    """
    if not date_str:
        return None

    try:
        # Try to parse the IOR timestamp format as local time
        dt = datetime.strptime(date_str.strip(), "%a %b %d %H:%M:%S %Y")
        # dt.timestamp() returns local time as Unix timestamp
        return int(dt.timestamp())
    except ValueError:
        # If parsing fails, return None
        return None
