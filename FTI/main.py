#!/usr/bin/env python3
"""
File Type Identifier - CLI entry point.
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import from src.main module
import importlib.util
spec = importlib.util.spec_from_file_location("src_main", src_path / "main.py")
src_main = importlib.util.module_from_spec(spec)
sys.modules["src_main"] = src_main
spec.loader.exec_module(src_main)

if __name__ == "__main__":
    src_main.main()
