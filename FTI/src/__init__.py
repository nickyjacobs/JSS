"""
File Type Identifier (FTI) - A tool for file type identification using magic numbers.
"""

__version__ = "1.0.0"
__author__ = "FTI Contributors"

from .identifier import identify, print_report
from .magic_db import MAGIC_DATABASE, get_all_signatures

__all__ = ["identify", "print_report", "MAGIC_DATABASE", "get_all_signatures"]
