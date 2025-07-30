"""
DataTidy: A configuration-driven data processing and cleaning package.

This package provides a unified interface for data processing tasks through
YAML configuration files. It supports multiple input sources including
CSV files, Excel files, and various databases.
"""

from .core import DataTidy
from .config.parser import ConfigParser
from .input.readers import DataReader

__version__ = "1.0.1"
__all__ = ["DataTidy", "ConfigParser", "DataReader"]