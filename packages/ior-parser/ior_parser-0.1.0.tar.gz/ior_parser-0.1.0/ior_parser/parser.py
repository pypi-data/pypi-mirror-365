"""
IOR Log Parser

This module parses IOR log files to extract performance metrics for analysis and reporting.
"""

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, Union, Optional

from .utils import parse_datetime_to_timestamp, parse_size_to_bytes


@dataclass
class IORFilesystemInfo:
    """Parsed filesystem information."""

    total_size_bytes: Optional[int] = None
    used_fs_percent: Optional[float] = None
    total_inodes: Optional[int] = None
    used_inodes_percent: Optional[float] = None


@dataclass
class IORTestTimes:
    """Test timing information."""

    began_text: Optional[str] = None
    began: Optional[int] = None  # Unix timestamp
    start_time_text: Optional[str] = None
    start_time: Optional[int] = None  # Unix timestamp
    finished_text: Optional[str] = None
    finished: Optional[int] = None  # Unix timestamp
    elapsed_seconds: Optional[float] = None  # Calculated elapsed time


@dataclass
class IORTestSetup:
    """Test setup information from the header."""

    ior_version: Optional[str] = None
    command_line: Optional[str] = None
    machine: Optional[str] = None
    test_id: Optional[str] = None
    path: Optional[str] = None
    file_system_info_text: Optional[str] = None
    file_system_info: Optional[IORFilesystemInfo] = None


@dataclass
class IOROptions:
    """Options section data."""

    api: Optional[str] = None
    api_version: Optional[str] = None
    test_filename: Optional[str] = None
    access: Optional[str] = None
    type: Optional[str] = None
    segments: Optional[int] = None
    ordering_in_file: Optional[str] = None
    ordering_inter_file: Optional[str] = None
    nodes: Optional[int] = None
    tasks: Optional[int] = None
    clients_per_node: Optional[int] = None
    repetitions: Optional[int] = None
    xfer_size_text: Optional[str] = None
    xfer_size_bytes: Optional[int] = None
    block_size_text: Optional[str] = None
    block_size_bytes: Optional[int] = None
    aggregate_file_size_text: Optional[str] = None
    aggregate_file_size_bytes: Optional[int] = None


@dataclass
class IOROperationResult:
    """Results for a single operation (read or write)."""

    bandwidth_mib_max: Optional[float] = None
    bandwidth_mib_min: Optional[float] = None
    bandwidth_mib_mean: Optional[float] = None
    bandwidth_mib_std: Optional[float] = None
    ops_max: Optional[float] = None
    ops_min: Optional[float] = None
    ops_mean: Optional[float] = None
    ops_std: Optional[float] = None
    time_seconds_mean: Optional[float] = None


@dataclass
class IORResults:
    """
    Complete IOR benchmark results organized into sections.
    """

    test_setup: IORTestSetup
    test_times: IORTestTimes
    options: IOROptions
    results: Dict[str, IOROperationResult]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self, indent: Optional[int] = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IORResults":
        """Create from dictionary."""
        return cls(**data)

    def get_combined_metrics(self) -> Dict[str, Optional[float]]:
        """
        Calculate combined read+write metrics.
        """
        combined = {}

        write_result = self.results.get("write")
        read_result = self.results.get("read")

        if (
            write_result
            and read_result
            and write_result.time_seconds_mean is not None
            and read_result.time_seconds_mean is not None
            and self.options.aggregate_file_size_bytes is not None
        ):
            total_time = write_result.time_seconds_mean + read_result.time_seconds_mean
            total_data_bytes = (
                self.options.aggregate_file_size_bytes * 2
            )  # write + read
            total_data_mib = total_data_bytes / (1024**2)
            combined["total_time_s"] = total_time
            combined["total_data_mib"] = total_data_mib
            combined["combined_bandwidth_mib_s"] = (
                total_data_mib / total_time if total_time > 0 else None
            )

        return combined


def parse_filesystem_info(fs_str: str) -> IORFilesystemInfo:
    """
    Parse filesystem info like '14.3 TiB   Used FS: 0.4%   Inodes: 190.7 Mi   Used Inodes: 0.4%'
    """
    fs_info = IORFilesystemInfo()

    if not fs_str:
        return fs_info

    try:
        # Parse total size (e.g., "14.3 TiB") and convert to bytes
        size_match = re.search(r"(\d+\.?\d*)\s*(TiB|GiB|MiB|TB|GB|MB)", fs_str)
        if size_match:
            size_value = float(size_match.group(1))
            unit = size_match.group(2)

            # Convert to bytes
            if unit == "TiB":
                fs_info.total_size_bytes = int(size_value * (1024**4))
            elif unit == "GiB":
                fs_info.total_size_bytes = int(size_value * (1024**3))
            elif unit == "MiB":
                fs_info.total_size_bytes = int(size_value * (1024**2))
            elif unit == "TB":
                fs_info.total_size_bytes = int(size_value * (1000**4))
            elif unit == "GB":
                fs_info.total_size_bytes = int(size_value * (1000**3))
            elif unit == "MB":
                fs_info.total_size_bytes = int(size_value * (1000**2))

        # Parse Used FS percentage
        used_fs_match = re.search(r"Used FS:\s*(\d+\.?\d*)%", fs_str)
        if used_fs_match:
            fs_info.used_fs_percent = float(used_fs_match.group(1))

        # Parse total inodes (e.g., "190.7 Mi") - Mi = Million (1,000,000)
        inodes_match = re.search(r"Inodes:\s*(\d+\.?\d*)\s*(Mi|Gi|Ti|M|G|T)", fs_str)
        if inodes_match:
            inodes_value = float(inodes_match.group(1))
            unit = inodes_match.group(2)

            # Convert to actual count
            if unit in ["Mi", "M"]:
                fs_info.total_inodes = int(inodes_value * 1000000)  # Million
            elif unit in ["Gi", "G"]:
                fs_info.total_inodes = int(inodes_value * 1000000000)  # Billion
            elif unit in ["Ti", "T"]:
                fs_info.total_inodes = int(inodes_value * 1000000000000)  # Trillion

        # Parse Used Inodes percentage
        used_inodes_match = re.search(r"Used Inodes:\s*(\d+\.?\d*)%", fs_str)
        if used_inodes_match:
            fs_info.used_inodes_percent = float(used_inodes_match.group(1))

    except (ValueError, AttributeError):
        pass

    return fs_info


def parse_ior_log(log_file_path: Union[str, Path]) -> IORResults:
    """
    Parse IOR log file to extract performance metrics.

    Args:
        log_file_path: Path to the IOR log file

    Returns:
        IORResults object containing parsed metrics

    Raises:
        FileNotFoundError: If the log file doesn't exist
        ValueError: If the log file cannot be parsed
    """
    log_file_path = Path(log_file_path)

    if not log_file_path.exists():
        raise FileNotFoundError(f"Log file not found: {log_file_path}")

    try:
        with open(log_file_path, "r") as f:
            content = f.read()
    except Exception as e:
        raise ValueError(f"Cannot read log file {log_file_path}: {e}")

    # Parse test setup section
    test_setup = IORTestSetup()
    test_times = IORTestTimes()

    # Parse IOR version
    version_match = re.search(r"IOR-([0-9.]+)", content)
    if version_match:
        test_setup.ior_version = version_match.group(1)

    # Parse began
    began_match = re.search(r"Began\s*:\s*(.+)", content)
    if began_match:
        test_times.began_text = began_match.group(1).strip()
        test_times.began = parse_datetime_to_timestamp(test_times.began_text)

    # Parse command line
    command_match = re.search(r"Command line\s*:\s*(.+)", content)
    if command_match:
        test_setup.command_line = command_match.group(1).strip()

    # Parse machine
    machine_match = re.search(r"Machine\s*:\s*(.+)", content)
    if machine_match:
        test_setup.machine = machine_match.group(1).strip()

    # Parse TestID
    testid_match = re.search(r"TestID\s*:\s*(.+)", content)
    if testid_match:
        test_setup.test_id = testid_match.group(1).strip()

    # Parse StartTime
    starttime_match = re.search(r"StartTime\s*:\s*(.+)", content)
    if starttime_match:
        test_times.start_time_text = starttime_match.group(1).strip()
        test_times.start_time = parse_datetime_to_timestamp(test_times.start_time_text)

    # Parse Path
    path_match = re.search(r"Path\s*:\s*(.+)", content)
    if path_match:
        test_setup.path = path_match.group(1).strip()

    # Parse FS info
    fs_match = re.search(r"FS\s*:\s*(.+)", content)
    if fs_match:
        test_setup.file_system_info_text = fs_match.group(1).strip()
        test_setup.file_system_info = parse_filesystem_info(
            test_setup.file_system_info_text
        )

    # Parse finished
    finished_match = re.search(r"Finished\s*:\s*(.+)", content)
    if finished_match:
        test_times.finished_text = finished_match.group(1).strip()
        test_times.finished = parse_datetime_to_timestamp(test_times.finished_text)

    # Calculate elapsed time
    if test_times.began is not None and test_times.finished is not None:
        test_times.elapsed_seconds = float(test_times.finished - test_times.began)

    # Parse options section - use line-by-line parsing to avoid regex issues
    options = IOROptions()

    # Find the Options section
    options_section = re.search(
        r"Options:\s*\n(.*?)(?=\nResults:|\Z)", content, re.DOTALL
    )
    if options_section:
        options_text = options_section.group(1)
        lines = options_text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key == "api":
                    options.api = value
                elif key == "apiVersion":
                    options.api_version = value if value else None
                elif key == "test filename":
                    options.test_filename = value
                elif key == "access":
                    options.access = value
                elif key == "type":
                    options.type = value
                elif key == "segments":
                    try:
                        options.segments = int(value)
                    except ValueError:
                        pass
                elif key == "ordering in a file":
                    options.ordering_in_file = value
                elif key == "ordering inter file":
                    options.ordering_inter_file = value
                elif key == "nodes":
                    try:
                        options.nodes = int(value)
                    except ValueError:
                        pass
                elif key == "tasks":
                    try:
                        options.tasks = int(value)
                    except ValueError:
                        pass
                elif key == "clients per node":
                    try:
                        options.clients_per_node = int(value)
                    except ValueError:
                        pass
                elif key == "repetitions":
                    try:
                        options.repetitions = int(value)
                    except ValueError:
                        pass
                elif key == "xfersize":
                    options.xfer_size_text = value
                    options.xfer_size_bytes = parse_size_to_bytes(value)
                elif key == "blocksize":
                    options.block_size_text = value
                    options.block_size_bytes = parse_size_to_bytes(value)
                elif key == "aggregate filesize":
                    options.aggregate_file_size_text = value
                    options.aggregate_file_size_bytes = parse_size_to_bytes(value)

    # Parse Summary section for results
    results = {}

    summary_section = re.search(
        r"Summary of all tests:\s*\n(.*?)(?=\nFinished|\Z)", content, re.DOTALL
    )
    if summary_section:
        summary_text = summary_section.group(1)

        # Split into lines and process each operation (write/read)
        lines = [line.strip() for line in summary_text.split("\n") if line.strip()]

        for line in lines:
            if line.startswith("write") or line.startswith("read"):
                parts = line.split()
                if len(parts) >= 23:  # Ensure we have enough parts
                    operation = parts[0]  # 'write' or 'read'

                    try:
                        # Extract metrics based on actual column positions from IOR output
                        bandwidth_mib_max = float(parts[1])  # Max(MiB)
                        bandwidth_mib_min = float(parts[2])  # Min(MiB)
                        bandwidth_mib_mean = float(parts[3])  # Mean(MiB)
                        bandwidth_mib_stddev = float(parts[4])  # StdDev
                        ops_max = float(parts[5])  # Max(OPs)
                        ops_min = float(parts[6])  # Min(OPs)
                        ops_mean = float(parts[7])  # Mean(OPs)
                        ops_stddev = float(parts[8])  # StdDev
                        time_s_mean = float(parts[9])  # Mean(s)

                        # Later columns: ... blksiz xsize aggs(MiB) API ...
                        # Index positions: 22: blksiz, 23: xsize, 24: aggs(MiB), 25: API
                        # Note: These values are already captured in test_setup and options sections

                        # Create operation result
                        op_result = IOROperationResult(
                            bandwidth_mib_max=bandwidth_mib_max,
                            bandwidth_mib_min=bandwidth_mib_min,
                            bandwidth_mib_mean=bandwidth_mib_mean,
                            bandwidth_mib_std=bandwidth_mib_stddev,
                            ops_max=ops_max,
                            ops_min=ops_min,
                            ops_mean=ops_mean,
                            ops_std=ops_stddev,
                            time_seconds_mean=time_s_mean,
                        )

                        results[operation] = op_result

                    except (ValueError, IndexError):
                        # Continue parsing even if one line fails
                        continue

    # Create final result object
    ior_results = IORResults(
        test_setup=test_setup, test_times=test_times, options=options, results=results
    )

    return ior_results


def print_ior_metrics(results: IORResults, title: str = "IOR Metrics") -> None:
    """
    Pretty print the extracted IOR metrics.

    Args:
        results: IORResults object containing parsed metrics
        title: Title for the output
    """
    print(f"\n=== {title} ===")

    # Test setup
    if results.test_setup.ior_version:
        print(f"IOR Version: {results.test_setup.ior_version}")
    if results.test_setup.machine:
        print(f"Machine: {results.test_setup.machine}")
    if results.options.nodes:
        print(f"Nodes: {results.options.nodes}")
    if results.options.tasks:
        print(f"Tasks: {results.options.tasks}")

    # Test timing
    if results.test_times.began_text and results.test_times.finished_text:
        print(
            f"Test Duration: {results.test_times.began_text} → {results.test_times.finished_text}"
        )
        if results.test_times.elapsed_seconds:
            print(f"Elapsed Time: {results.test_times.elapsed_seconds:.1f} seconds")

    # Options
    print(f"Access Pattern: {results.options.access or 'N/A'}")
    print(f"Ordering in File: {results.options.ordering_in_file or 'N/A'}")
    print(f"API: {results.options.api or 'N/A'}")

    # Size information
    if results.options.block_size_text:
        print(
            f"Block Size: {results.options.block_size_text or 'N/A'} ({results.options.block_size_bytes or 'N/A'} bytes)"
        )
    else:
        print("Block Size: N/A")

    if results.options.xfer_size_text:
        print(
            f"Transfer Size: {results.options.xfer_size_text or 'N/A'} ({results.options.xfer_size_bytes or 'N/A'} bytes)"
        )
    else:
        print("Transfer Size: N/A")

    if results.options.aggregate_file_size_text:
        print(
            f"Aggregate Size: {results.options.aggregate_file_size_text or 'N/A'} ({results.options.aggregate_file_size_bytes or 'N/A'} bytes)"
        )
    else:
        print("Aggregate Size: N/A")

    # Filesystem info
    if results.test_setup.file_system_info:
        fs_info = results.test_setup.file_system_info
        total_size_tib = (
            fs_info.total_size_bytes / (1024**4) if fs_info.total_size_bytes else 0
        )
        print(
            f"Filesystem: {total_size_tib:.1f} TiB total, {fs_info.used_fs_percent:.1f}% used"
        )

    # Write metrics
    write_result = results.results.get("write")
    if write_result and write_result.bandwidth_mib_mean is not None:
        print("\nWrite Performance:")
        print(
            f"  Bandwidth: {write_result.bandwidth_mib_mean:.2f} ± {write_result.bandwidth_mib_std or 0:.2f} MiB/s"
        )
        print(
            f"  Operations: {write_result.ops_mean:.2f} ± {write_result.ops_std or 0:.2f} ops/s"
        )
        print(f"  Time: {write_result.time_seconds_mean:.3f} seconds")

    # Read metrics
    read_result = results.results.get("read")
    if read_result and read_result.bandwidth_mib_mean is not None:
        print("\nRead Performance:")
        print(
            f"  Bandwidth: {read_result.bandwidth_mib_mean:.2f} ± {read_result.bandwidth_mib_std or 0:.2f} MiB/s"
        )
        print(
            f"  Operations: {read_result.ops_mean:.2f} ± {read_result.ops_std or 0:.2f} ops/s"
        )
        print(f"  Time: {read_result.time_seconds_mean:.3f} seconds")

    # Combined metrics
    combined = results.get_combined_metrics()
    if combined.get("total_time_s"):
        print("\nCombined Performance:")
        print(f"  Total Time: {combined['total_time_s']:.3f} seconds")
        print(f"  Total Data: {combined['total_data_mib']:.2f} MiB")
        print(f"  Combined Bandwidth: {combined['combined_bandwidth_mib_s']:.2f} MiB/s")
