"""
Tests for the IOR log parser functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from ior_parser.parser import parse_ior_log, IORResults


@pytest.fixture
def logs_dir():
    """Return the path to the test logs directory."""
    return Path(__file__).parent / "logs"


@pytest.fixture
def basic_sequential_log(logs_dir):
    """Return path to basic sequential log file."""
    return logs_dir / "basic_sequential.log"


@pytest.fixture
def write_only_log(logs_dir):
    """Return path to write-only log file."""
    return logs_dir / "write_only.log"


@pytest.fixture
def direct_io_log(logs_dir):
    """Return path to direct I/O log file."""
    return logs_dir / "direct_io.log"


@pytest.fixture
def large_blocks_log(logs_dir):
    """Return path to large blocks log file."""
    return logs_dir / "large_blocks.log"


@pytest.fixture
def small_blocks_log(logs_dir):
    """Return path to small blocks log file."""
    return logs_dir / "small_blocks.log"


@pytest.fixture
def verbose1_log(logs_dir):
    """Return path to verbose level 1 log file."""
    return logs_dir / "direct_io_verbose1.log"


@pytest.fixture
def verbose2_log(logs_dir):
    """Return path to verbose level 2 log file."""
    return logs_dir / "direct_io_verbose2.log"


class TestBasicParsing:
    """Test basic parsing functionality."""

    def test_parse_basic_sequential(self, basic_sequential_log):
        """Test parsing of basic sequential read+write log."""
        result = parse_ior_log(basic_sequential_log)

        # Check basic structure
        assert isinstance(result, IORResults)
        assert result.test_setup is not None
        assert result.test_times is not None
        assert result.options is not None
        assert result.results is not None

        # Check test setup fields (allow different versions)
        assert result.test_setup.ior_version in ["3.3.0+dev", "4.0.0"]
        assert result.test_setup.command_line is not None

        # Check test times
        assert result.test_times.began is not None
        assert result.test_times.finished is not None
        assert result.test_times.elapsed_seconds is not None

        # Check that we have read and write results
        assert result.results.get("read") is not None
        assert result.results.get("write") is not None

        # Check bandwidth fields exist and are numeric
        read_result = result.results["read"]
        write_result = result.results["write"]
        assert hasattr(read_result, "bandwidth_mib_mean")
        assert hasattr(write_result, "bandwidth_mib_mean")
        assert isinstance(read_result.bandwidth_mib_mean, (int, float))
        assert isinstance(write_result.bandwidth_mib_mean, (int, float))

        # Check filesystem info
        assert result.test_setup.file_system_info is not None
        assert hasattr(result.test_setup.file_system_info, "total_size_bytes")

    def test_parse_write_only(self, write_only_log):
        """Test parsing of write-only log."""
        result = parse_ior_log(write_only_log)

        # Should have write results but possibly no read results
        assert result.results.get("write") is not None

        # Check write operation details
        write_result = result.results["write"]
        assert hasattr(write_result, "bandwidth_mib_mean")
        assert hasattr(write_result, "ops_mean")
        assert isinstance(write_result.bandwidth_mib_mean, (int, float))
        assert isinstance(write_result.ops_mean, (int, float))

    def test_parse_direct_io(self, direct_io_log):
        """Test parsing of direct I/O log."""
        result = parse_ior_log(direct_io_log)

        # Check that parsing works for direct I/O
        assert result.options is not None

        # Basic structure validation
        assert result.test_setup is not None
        assert result.results is not None

    def test_parse_verbose_logs(self, verbose1_log, verbose2_log):
        """Test parsing of verbose logs with different verbosity levels."""
        # Test verbose level 1
        result1 = parse_ior_log(verbose1_log)
        assert isinstance(result1, IORResults)
        assert result1.test_setup is not None

        # Test verbose level 2
        result2 = parse_ior_log(verbose2_log)
        assert isinstance(result2, IORResults)
        assert result2.test_setup is not None

        # Both should have valid structure despite verbosity differences
        for result in [result1, result2]:
            assert result.test_times is not None
            assert result.options is not None
            assert result.results is not None


class TestAllLogFiles:
    """Test parsing of all available log files."""

    def test_all_logs_parse_successfully(self, logs_dir):
        """Test that all log files in the logs directory can be parsed without errors."""
        log_files = list(logs_dir.glob("*.log"))
        assert len(log_files) > 0, "No log files found in logs directory"

        results = {}
        for log_file in log_files:
            try:
                result = parse_ior_log(log_file)
                results[log_file.name] = result

                # Basic validation for each file
                assert isinstance(result, IORResults)
                assert result.test_setup is not None
                assert result.test_times is not None
                assert result.options is not None
                assert result.results is not None

            except Exception as e:
                pytest.fail(f"Failed to parse {log_file.name}: {e}")

        # Check that we parsed multiple files
        assert len(results) >= 5, f"Expected at least 5 log files, got {len(results)}"


class TestDataStructures:
    """Test data structure functionality."""

    def test_to_dict_method(self, basic_sequential_log):
        """Test the to_dict method of IORResults."""
        result = parse_ior_log(basic_sequential_log)
        data_dict = result.to_dict()

        # Check that all main sections are present
        assert "test_setup" in data_dict
        assert "test_times" in data_dict
        assert "options" in data_dict
        assert "results" in data_dict

        # Check nested structure
        assert isinstance(data_dict["test_setup"], dict)
        assert isinstance(data_dict["test_times"], dict)
        assert isinstance(data_dict["results"], dict)

    def test_to_json_method(self, basic_sequential_log):
        """Test the to_json method of IORResults."""
        result = parse_ior_log(basic_sequential_log)
        json_str = result.to_json()

        # Should be valid JSON string
        import json

        parsed_json = json.loads(json_str)

        # Check structure
        assert "test_setup" in parsed_json
        assert "test_times" in parsed_json
        assert "options" in parsed_json
        assert "results" in parsed_json

    def test_combined_metrics(self, basic_sequential_log):
        """Test combined read+write metrics calculation."""
        result = parse_ior_log(basic_sequential_log)

        read_result = result.results.get("read")
        write_result = result.results.get("write")

        if read_result and write_result:
            # Check that both read and write have metrics
            assert hasattr(read_result, "bandwidth_mib_mean")
            assert hasattr(write_result, "bandwidth_mib_mean")

            # Values should be positive
            assert read_result.bandwidth_mib_mean > 0
            assert write_result.bandwidth_mib_mean > 0

    def test_combined_metrics_write_only(self, write_only_log):
        """Test metrics for write-only operations."""
        result = parse_ior_log(write_only_log)

        # Should have write metrics
        write_result = result.results.get("write")
        assert write_result is not None
        assert write_result.bandwidth_mib_mean > 0


class TestFieldValidation:
    """Test field validation and data types."""

    def test_size_parsing(self, basic_sequential_log):
        """Test that size fields are properly parsed to bytes."""
        result = parse_ior_log(basic_sequential_log)

        # Check that size fields exist and are integers (bytes)
        assert hasattr(result.options, "xfer_size_bytes")
        assert hasattr(result.options, "block_size_bytes")

        if result.options.xfer_size_bytes is not None:
            assert isinstance(result.options.xfer_size_bytes, int)
            assert result.options.xfer_size_bytes > 0

        if result.options.block_size_bytes is not None:
            assert isinstance(result.options.block_size_bytes, int)
            assert result.options.block_size_bytes > 0

    def test_datetime_parsing(self, basic_sequential_log):
        """Test that datetime fields are properly parsed to timestamps."""
        result = parse_ior_log(basic_sequential_log)

        # Check that timestamp fields exist and are integers (Unix timestamps)
        assert result.test_times.began is not None
        assert result.test_times.finished is not None
        assert isinstance(result.test_times.began, int)
        assert isinstance(result.test_times.finished, int)

        # Finished should be after began
        assert result.test_times.finished >= result.test_times.began

        # Elapsed should be calculated correctly
        expected_elapsed = result.test_times.finished - result.test_times.began
        assert result.test_times.elapsed_seconds == expected_elapsed

    def test_filesystem_info_parsing(self, basic_sequential_log):
        """Test that filesystem information is properly parsed."""
        result = parse_ior_log(basic_sequential_log)

        assert result.test_setup.file_system_info is not None
        assert hasattr(result.test_setup.file_system_info, "total_size_bytes")
        assert hasattr(result.test_setup.file_system_info, "used_fs_percent")

        # Values should be numeric if present
        if result.test_setup.file_system_info.total_size_bytes:
            assert isinstance(result.test_setup.file_system_info.total_size_bytes, int)
            assert result.test_setup.file_system_info.total_size_bytes > 0

        if result.test_setup.file_system_info.used_fs_percent:
            assert isinstance(result.test_setup.file_system_info.used_fs_percent, float)
            assert 0 <= result.test_setup.file_system_info.used_fs_percent <= 100


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_nonexistent_file(self):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError):
            parse_ior_log(Path("/nonexistent/file.log"))

    def test_empty_file(self):
        """Test handling of empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            temp_path = Path(f.name)

        try:
            result = parse_ior_log(temp_path)
            # Should return an IORResults object but with minimal data
            assert isinstance(result, IORResults)
        finally:
            os.unlink(temp_path)

    def test_invalid_file_content(self):
        """Test handling of file with invalid content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write("This is not a valid IOR log file\n")
            f.write("Random content that doesn't match IOR format\n")
            temp_path = Path(f.name)

        try:
            result = parse_ior_log(temp_path)
            # Should return an IORResults object but with minimal data
            assert isinstance(result, IORResults)
        finally:
            os.unlink(temp_path)


class TestPerformanceMetrics:
    """Test performance-related metrics and calculations."""

    def test_bandwidth_metrics(self, basic_sequential_log):
        """Test bandwidth metric calculations and consistency."""
        result = parse_ior_log(basic_sequential_log)

        read_result = result.results.get("read")
        if read_result:
            # Check bandwidth fields
            assert hasattr(read_result, "bandwidth_mib_mean")
            assert hasattr(read_result, "bandwidth_mib_max")
            assert hasattr(read_result, "bandwidth_mib_min")

            # Mean should be between min and max
            if (
                read_result.bandwidth_mib_min is not None
                and read_result.bandwidth_mib_max is not None
            ):
                assert (
                    read_result.bandwidth_mib_min
                    <= read_result.bandwidth_mib_mean
                    <= read_result.bandwidth_mib_max
                )

        write_result = result.results.get("write")
        if write_result:
            # Same checks for write operations
            assert hasattr(write_result, "bandwidth_mib_mean")
            if (
                write_result.bandwidth_mib_min is not None
                and write_result.bandwidth_mib_max is not None
            ):
                assert (
                    write_result.bandwidth_mib_min
                    <= write_result.bandwidth_mib_mean
                    <= write_result.bandwidth_mib_max
                )

    def test_performance_consistency(self, logs_dir):
        """Test that performance metrics are consistent across different log files."""
        log_files = list(logs_dir.glob("*.log"))
        bandwidth_values = []

        for log_file in log_files:
            try:
                result = parse_ior_log(log_file)

                # Collect bandwidth values
                read_result = result.results.get("read")
                write_result = result.results.get("write")

                if read_result and read_result.bandwidth_mib_mean:
                    bandwidth_values.append(read_result.bandwidth_mib_mean)
                if write_result and write_result.bandwidth_mib_mean:
                    bandwidth_values.append(write_result.bandwidth_mib_mean)

            except Exception:
                continue  # Skip files that can't be parsed

        # All bandwidth values should be positive
        for bw in bandwidth_values:
            assert bw > 0, f"Bandwidth value should be positive, got {bw}"

        # Should have at least some bandwidth measurements
        assert len(bandwidth_values) > 0, "No bandwidth values found in any log files"
