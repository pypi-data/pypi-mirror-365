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
python -m ior_parser path/to/ior.log --json
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
