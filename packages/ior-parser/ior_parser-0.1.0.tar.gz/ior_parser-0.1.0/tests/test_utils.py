"""
Tests for utility functions in the ior_parser.utils module.
"""

from ior_parser.utils import parse_size_to_bytes, parse_datetime_to_timestamp


class TestParseSizeToBytes:
    """Test cases for parse_size_to_bytes function."""

    def test_binary_units(self):
        """Test parsing of binary units (base 1024)."""
        # Bytes
        assert parse_size_to_bytes("1 B") == 1
        assert parse_size_to_bytes("100 B") == 100

        # KiB (1024 bytes)
        assert parse_size_to_bytes("1 KiB") == 1024
        assert parse_size_to_bytes("2 KiB") == 2048

        # MiB (1024^2 bytes)
        assert parse_size_to_bytes("1 MiB") == 1048576
        assert parse_size_to_bytes("4 MiB") == 4194304
        assert parse_size_to_bytes("512 MiB") == 536870912

        # GiB (1024^3 bytes)
        assert parse_size_to_bytes("1 GiB") == 1073741824
        assert parse_size_to_bytes("2 GiB") == 2147483648

        # TiB (1024^4 bytes)
        assert parse_size_to_bytes("1 TiB") == 1099511627776
        assert parse_size_to_bytes("2 TiB") == 2199023255552

    def test_decimal_units(self):
        """Test parsing of decimal units (base 1000)."""
        # KB (1000 bytes)
        assert parse_size_to_bytes("1 KB") == 1000
        assert parse_size_to_bytes("2 KB") == 2000

        # MB (1000^2 bytes)
        assert parse_size_to_bytes("1 MB") == 1000000
        assert parse_size_to_bytes("512 MB") == 512000000

        # GB (1000^3 bytes)
        assert parse_size_to_bytes("1 GB") == 1000000000
        assert parse_size_to_bytes("4 GB") == 4000000000

        # TB (1000^4 bytes)
        assert parse_size_to_bytes("1 TB") == 1000000000000
        assert parse_size_to_bytes("2 TB") == 2000000000000

    def test_float_values(self):
        """Test parsing of floating-point values."""
        assert parse_size_to_bytes("1.5 MiB") == 1572864  # 1.5 * 1024^2
        assert parse_size_to_bytes("2.5 GiB") == 2684354560  # 2.5 * 1024^3
        assert parse_size_to_bytes("0.5 TiB") == 549755813888  # 0.5 * 1024^4
        assert parse_size_to_bytes("1.5 GB") == 1500000000  # 1.5 * 1000^3

    def test_whitespace_handling(self):
        """Test that function handles whitespace correctly."""
        assert parse_size_to_bytes(" 1 MiB ") == 1048576
        assert parse_size_to_bytes("  4  GiB  ") == 4294967296
        assert parse_size_to_bytes("\t1\tTiB\t") == 1099511627776

    def test_invalid_inputs(self):
        """Test that function returns None for invalid inputs."""
        # Empty or None input
        assert parse_size_to_bytes("") is None
        assert parse_size_to_bytes(None) is None

        # Missing unit
        assert parse_size_to_bytes("1024") is None

        # Missing value
        assert parse_size_to_bytes("MiB") is None

        # Invalid unit
        assert parse_size_to_bytes("1 XiB") is None
        assert parse_size_to_bytes("1 invalid") is None

        # Invalid value
        assert parse_size_to_bytes("invalid MiB") is None
        assert parse_size_to_bytes("abc GiB") is None

        # Too many parts
        assert parse_size_to_bytes("1 2 MiB") is None
        assert parse_size_to_bytes("1 MiB extra") is None

        # Negative values (should parse but may not be meaningful)
        assert parse_size_to_bytes("-1 MiB") == -1048576  # Function allows negative

    def test_ior_typical_values(self):
        """Test typical values found in IOR logs."""
        # Common transfer sizes
        assert parse_size_to_bytes("1 MiB") == 1048576

        # Common block sizes
        assert parse_size_to_bytes("4 MiB") == 4194304
        assert parse_size_to_bytes("16 MiB") == 16777216

        # Common aggregate file sizes
        assert parse_size_to_bytes("512 MiB") == 536870912
        assert parse_size_to_bytes("1 GiB") == 1073741824

        # Filesystem sizes (from FS info)
        assert parse_size_to_bytes("14.3 TiB") == 15723016277196  # 14.3 * 1024^4

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Zero value
        assert parse_size_to_bytes("0 B") == 0
        assert parse_size_to_bytes("0 MiB") == 0

        # Very small decimal values
        assert parse_size_to_bytes("0.1 MiB") == 104857  # 0.1 * 1024^2, truncated

        # Case sensitivity (units should be case-sensitive)
        assert parse_size_to_bytes("1 mib") is None  # lowercase should fail
        assert parse_size_to_bytes("1 MIB") is None  # uppercase should fail

    def test_return_type(self):
        """Test that function returns integers for valid inputs."""
        result = parse_size_to_bytes("1 MiB")
        assert isinstance(result, int)
        assert result == 1048576

        # Even for float inputs, should return int
        result = parse_size_to_bytes("1.5 MiB")
        assert isinstance(result, int)
        assert result == 1572864


class TestParseDatetimeToTimestamp:
    """Test cases for parse_datetime_to_timestamp function."""

    def test_valid_ior_timestamps(self):
        """Test parsing of valid IOR timestamp format."""
        # Test that timestamps are parsed and are reasonable
        result1 = parse_datetime_to_timestamp("Sun Jul 27 08:35:34 2025")
        result2 = parse_datetime_to_timestamp("Sun Jul 27 08:35:37 2025")

        assert result1 is not None
        assert result2 is not None
        assert result2 - result1 == 3  # 3 seconds difference

        # Test that 2024 timestamp is reasonable (around Jan 1, 2024)
        jan_2024 = parse_datetime_to_timestamp("Mon Jan 01 00:00:00 2024")
        assert jan_2024 is not None
        assert jan_2024 > 1704000000  # Should be roughly around Jan 1, 2024
        assert jan_2024 < 1705000000  # But not too far off

        # Test end of 2023
        dec_2023 = parse_datetime_to_timestamp("Fri Dec 31 23:59:59 2023")
        assert dec_2023 is not None
        assert jan_2024 > dec_2023  # Jan 2024 should be after Dec 2023

    def test_different_weekdays(self):
        """Test that different weekdays are parsed correctly."""
        # All should parse regardless of weekday
        assert parse_datetime_to_timestamp("Mon Jul 27 08:35:34 2025") is not None
        assert parse_datetime_to_timestamp("Tue Jul 27 08:35:34 2025") is not None
        assert parse_datetime_to_timestamp("Wed Jul 27 08:35:34 2025") is not None
        assert parse_datetime_to_timestamp("Thu Jul 27 08:35:34 2025") is not None
        assert parse_datetime_to_timestamp("Fri Jul 27 08:35:34 2025") is not None
        assert parse_datetime_to_timestamp("Sat Jul 27 08:35:34 2025") is not None
        assert parse_datetime_to_timestamp("Sun Jul 27 08:35:34 2025") is not None

    def test_different_months(self):
        """Test that different months are parsed correctly."""
        assert parse_datetime_to_timestamp("Sun Jan 01 12:00:00 2025") is not None
        assert parse_datetime_to_timestamp("Sun Feb 01 12:00:00 2025") is not None
        assert parse_datetime_to_timestamp("Sun Mar 01 12:00:00 2025") is not None
        assert parse_datetime_to_timestamp("Sun Apr 01 12:00:00 2025") is not None
        assert parse_datetime_to_timestamp("Sun May 01 12:00:00 2025") is not None
        assert parse_datetime_to_timestamp("Sun Jun 01 12:00:00 2025") is not None
        assert parse_datetime_to_timestamp("Sun Jul 01 12:00:00 2025") is not None
        assert parse_datetime_to_timestamp("Sun Aug 01 12:00:00 2025") is not None
        assert parse_datetime_to_timestamp("Sun Sep 01 12:00:00 2025") is not None
        assert parse_datetime_to_timestamp("Sun Oct 01 12:00:00 2025") is not None
        assert parse_datetime_to_timestamp("Sun Nov 01 12:00:00 2025") is not None
        assert parse_datetime_to_timestamp("Sun Dec 01 12:00:00 2025") is not None

    def test_whitespace_handling(self):
        """Test that function handles whitespace correctly."""
        # Compute expected timestamp using local time, so test is robust to environment
        from datetime import datetime

        base_str = "Sun Jul 27 08:35:34 2025"
        expected = int(datetime.strptime(base_str, "%a %b %d %H:%M:%S %Y").timestamp())
        assert parse_datetime_to_timestamp(" Sun Jul 27 08:35:34 2025 ") == expected
        assert parse_datetime_to_timestamp("\tSun Jul 27 08:35:34 2025\t") == expected
        assert parse_datetime_to_timestamp("  Sun Jul 27 08:35:34 2025  ") == expected

    def test_invalid_inputs(self):
        """Test that function returns None for invalid inputs."""
        # Empty or None input
        assert parse_datetime_to_timestamp("") is None
        assert parse_datetime_to_timestamp(None) is None

        # Wrong format
        assert parse_datetime_to_timestamp("2025-07-27 08:35:34") is None  # ISO format
        assert parse_datetime_to_timestamp("07/27/2025 08:35:34") is None  # US format
        assert parse_datetime_to_timestamp("27/07/2025 08:35:34") is None  # EU format

        # Invalid components
        assert (
            parse_datetime_to_timestamp("Sun Jul 32 08:35:34 2025") is None
        )  # Invalid day
        assert (
            parse_datetime_to_timestamp("Sun Jul 27 25:35:34 2025") is None
        )  # Invalid hour
        assert (
            parse_datetime_to_timestamp("Sun Jul 27 08:65:34 2025") is None
        )  # Invalid minute
        assert (
            parse_datetime_to_timestamp("Sun Jul 27 08:35:65 2025") is None
        )  # Invalid second
        assert (
            parse_datetime_to_timestamp("Sun Xyz 27 08:35:34 2025") is None
        )  # Invalid month

        # Incomplete
        assert (
            parse_datetime_to_timestamp("Sun Jul 27 08:35:34") is None
        )  # Missing year
        assert (
            parse_datetime_to_timestamp("Jul 27 08:35:34 2025") is None
        )  # Missing weekday

        # Completely invalid
        assert parse_datetime_to_timestamp("invalid") is None
        assert parse_datetime_to_timestamp("not a date") is None

    def test_year_range(self):
        """Test different years."""
        # Past years
        assert parse_datetime_to_timestamp("Sun Jul 27 08:35:34 2020") is not None
        assert parse_datetime_to_timestamp("Sun Jul 27 08:35:34 2000") is not None
        assert parse_datetime_to_timestamp("Sun Jul 27 08:35:34 1990") is not None

        # Future years
        assert parse_datetime_to_timestamp("Sun Jul 27 08:35:34 2030") is not None
        assert parse_datetime_to_timestamp("Sun Jul 27 08:35:34 2050") is not None

    def test_time_variations(self):
        """Test different time components."""
        # Midnight
        assert parse_datetime_to_timestamp("Sun Jul 27 00:00:00 2025") is not None

        # Noon
        assert parse_datetime_to_timestamp("Sun Jul 27 12:00:00 2025") is not None

        # Almost midnight
        assert parse_datetime_to_timestamp("Sun Jul 27 23:59:59 2025") is not None

        # Various times
        assert parse_datetime_to_timestamp("Sun Jul 27 01:23:45 2025") is not None
        assert parse_datetime_to_timestamp("Sun Jul 27 13:47:19 2025") is not None

    def test_elapsed_time_calculation(self):
        """Test that timestamps can be used for elapsed time calculation."""
        start = parse_datetime_to_timestamp("Sun Jul 27 08:35:34 2025")
        end = parse_datetime_to_timestamp("Sun Jul 27 08:35:37 2025")

        assert start is not None
        assert end is not None
        assert end - start == 3  # 3 seconds difference

    def test_return_type(self):
        """Test that function returns integers for valid inputs."""
        result = parse_datetime_to_timestamp("Sun Jul 27 08:35:34 2025")
        assert isinstance(result, int)
        assert result > 0  # Should be a positive timestamp

    def test_ior_typical_values(self):
        """Test with actual values from IOR logs."""
        # These are real timestamps from the test logs
        began = parse_datetime_to_timestamp("Sun Jul 27 08:35:34 2025")
        finished = parse_datetime_to_timestamp("Sun Jul 27 08:35:37 2025")

        assert began is not None
        assert finished is not None
        assert finished > began  # Finished should be after began
        assert finished - began == 3  # Should be 3 seconds apart

        # Test with write-only log timestamps
        began_write = parse_datetime_to_timestamp("Sun Jul 27 08:35:50 2025")
        finished_write = parse_datetime_to_timestamp("Sun Jul 27 08:35:51 2025")

        assert began_write is not None
        assert finished_write is not None
        assert finished_write > began_write
        assert finished_write - began_write == 1  # 1 second apart
