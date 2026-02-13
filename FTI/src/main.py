#!/usr/bin/env python3
"""
File Type Identifier - CLI entry point.
"""

import argparse
import sys
from pathlib import Path

import sys
from pathlib import Path

# Try to import config from parent directory
try:
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from config import VIRUSTOTAL_API_KEY
except ImportError:
    VIRUSTOTAL_API_KEY = None

# Use absolute imports when run as script, relative when imported as package
try:
    from .identifier import identify, print_report
except ImportError:
    from identifier import identify, print_report


def main():
    parser = argparse.ArgumentParser(
        description="File Type Identifier - Detect file types using magic numbers"
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="File to analyze",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch web GUI",
    )
    parser.add_argument(
        "--vt-api-key",
        type=str,
        help="VirusTotal API key (overrides config.py)",
    )
    parser.add_argument(
        "--no-file-cmd",
        action="store_true",
        help="Don't use system 'file' command",
    )

    args = parser.parse_args()

    if args.gui:
        try:
            from .gui_web import main as gui_main
        except ImportError:
            from gui_web import main as gui_main
        gui_main()
        return

    if not args.file:
        parser.print_help()
        sys.exit(1)

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    api_key = args.vt_api_key or VIRUSTOTAL_API_KEY
    result = identify(
        filepath,
        use_file_cmd=not args.no_file_cmd,
        virustotal_api_key=api_key,
    )

    print_report(result)

    if result.get("mismatch"):
        sys.exit(1)


if __name__ == "__main__":
    main()
