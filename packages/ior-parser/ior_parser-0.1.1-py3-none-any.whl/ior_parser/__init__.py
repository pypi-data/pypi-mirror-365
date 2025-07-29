"""
ior-parser: IOR benchmark log file parser

This package provides parsing capabilities for IOR (Interleaved Or Random)
benchmark log files, enabling extraction of performance metrics and test
configuration data for analysis and comparison.
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("ior-parser")
except importlib.metadata.PackageNotFoundError:
    # Package not installed, fallback for development
    __version__ = "0.0.0+dev"

# Import the main parser functions and classes
from .parser import parse_ior_log, IORResults

__all__ = ["parse_ior_log", "IORResults", "__version__"]
