#!/usr/bin/env python3
"""
Command-line interface for IOR log parser.
"""

import argparse
import sys
from pathlib import Path

from .parser import parse_ior_log, print_ior_metrics


def main() -> int:
    """Main command-line entry point."""
    parser = argparse.ArgumentParser(
        description="Parse IOR benchmark log files and extract performance metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a single log file and print human-readable output
  python -m ior_parser tests/logs/basic_sequential.log
  
  # Parse a log file and output JSON
  python -m ior_parser tests/logs/basic_sequential.log --json
  
  # Save JSON output to file
  python -m ior_parser tests/logs/basic_sequential.log --json --output results.json
  
  # Parse multiple files and output JSON array
  python -m ior_parser tests/logs/*.log --json
        """,
    )

    parser.add_argument("log_files", nargs="+", help="IOR log file(s) to parse")

    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )

    parser.add_argument(
        "--output", "-o", type=str, help="Output file path (default: stdout)"
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (ignored if --json not specified)",
    )

    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress error messages"
    )

    args = parser.parse_args()

    # Validate input files
    log_files = []
    for log_file_path in args.log_files:
        path = Path(log_file_path)
        if not path.exists():
            if not args.quiet:
                print(f"Error: File not found: {log_file_path}", file=sys.stderr)
            return 1
        log_files.append(path)

    # Parse all files
    results = []
    for log_file in log_files:
        try:
            result = parse_ior_log(log_file)
            if args.json:
                result_dict = result.to_dict()
                result_dict["_source_file"] = str(log_file)
                results.append(result_dict)
            else:
                print_ior_metrics(result, f"Results from {log_file.name}")
        except Exception as e:
            if not args.quiet:
                print(f"Error parsing {log_file}: {e}", file=sys.stderr)
            return 1

    # Output JSON if requested
    if args.json:
        import json

        if len(results) == 1:
            output_data = results[0]
        else:
            output_data = results

        json_str = json.dumps(output_data, indent=2 if args.pretty else None)

        if args.output:
            try:
                with open(args.output, "w") as f:
                    f.write(json_str)
                if not args.quiet:
                    print(f"Results written to {args.output}")
            except Exception as e:
                if not args.quiet:
                    print(f"Error writing to {args.output}: {e}", file=sys.stderr)
                return 1
        else:
            print(json_str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
