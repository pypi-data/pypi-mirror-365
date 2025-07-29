# ior-parser

A Python package for parsing IOR (Interleaved Or Random) benchmark log files. Extracts performance metrics, test configuration, and filesystem information for analysis, reporting, and automation.

## Features

- Parse IOR log files from command line or Python API
- Extracts test setup, timing, options, and results sections
- Converts sizes to bytes and timestamps to Unix time
- Outputs structured JSON for further analysis
- CLI and Python API usage
- Supports IOR logs from multiple versions and verbosity levels

## Installation

```bash
pip install ior-parser
```

Or for development:

```bash
git clone https://github.com/izzet/ior-parser.git
cd ior-parser
pip install -e .
```

## Usage

### Command Line

```bash
ior_parser tests/logs/write_only.log --json --pretty
```

Example output:

```json
{
  "test_setup": {
    "ior_version": "4.0.0",
    "command_line": "bin/ior -a POSIX -s 128 -b 4M -t 1M -F -w -o /tmp/write_only/data/testfile",
    "machine": "Linux corona211",
    "test_id": "0",
    "path": "/tmp/write_only/data/testfile.00000000",
    "file_system_info_text": "14.3 TiB   Used FS: 0.4%   Inodes: 190.7 Mi   Used Inodes: 0.4%",
    "file_system_info": {
      "total_size_bytes": 15723016277196,
      "used_fs_percent": 0.4,
      "total_inodes": 190700000,
      "used_inodes_percent": 0.4
    }
  },
  "test_times": {
    "began_text": "Sun Jul 27 08:35:50 2025",
    "began": 1753630550,
    "start_time_text": "Sun Jul 27 08:35:50 2025",
    "start_time": 1753630550,
    "finished_text": "Sun Jul 27 08:35:51 2025",
    "finished": 1753630551,
    "elapsed_seconds": 1.0
  },
  "options": {
    "api": "POSIX",
    "api_version": null,
    "test_filename": "/tmp/write_only/data/testfile",
    "access": "file-per-process",
    "type": "independent",
    "segments": 128,
    "ordering_in_file": "sequential",
    "ordering_inter_file": "no tasks offsets",
    "nodes": 1,
    "tasks": 1,
    "clients_per_node": 1,
    "repetitions": 1,
    "xfer_size_text": "1 MiB",
    "xfer_size_bytes": 1048576,
    "block_size_text": "4 MiB",
    "block_size_bytes": 4194304,
    "aggregate_file_size_text": "512 MiB",
    "aggregate_file_size_bytes": 536870912
  },
  "results": {
    "write": {
      "bandwidth_mib_max": 660.64,
      "bandwidth_mib_min": 660.64,
      "bandwidth_mib_mean": 660.64,
      "bandwidth_mib_std": 0.0,
      "ops_max": 660.64,
      "ops_min": 660.64,
      "ops_mean": 660.64,
      "ops_std": 0.0,
      "time_seconds_mean": 0.77501
    }
  },
  "_source_file": "tests/logs/write_only.log"
}
```

### Python API

```python
from ior_parser import parse_ior_log
result = parse_ior_log("path/to/ior.log")
print(result.to_dict())
```

## Output Structure

- `test_setup`: IOR version, command line, machine, path, filesystem info
- `test_times`: began, finished, elapsed (as Unix timestamps)
- `options`: parsed IOR options (API, block size, transfer size, etc.)
- `results`: read/write operation metrics (bandwidth, IOPS, time)

## Development

- Lint: `ruff check .`
- Format: `ruff format .`
- Test: `pytest`
- Pre-commit: `pre-commit run --all-files`

## License

MIT

## Author

Izzet Yildirim (<izzetcyildirim@gmail.com>)

## Links

- [GitHub](https://github.com/izzet/ior-parser)
- [Bug Tracker](https://github.com/izzet/ior-parser/issues)
