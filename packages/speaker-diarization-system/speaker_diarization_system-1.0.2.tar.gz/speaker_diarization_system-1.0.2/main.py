#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=broad-except

"""
Main entry point for the Speaker Diarization & Splitting System.

This script is designed for standardization and simply executes the core logic
from the `split_speakers.py` script. Running this script is equivalent to
running `split_speakers.py` directly.

Any command-line arguments provided to `main.py` will be automatically
passed along to the underlying script.

Usage:
    python main.py [speakers] [--verbose]

Example:
    python main.py 2 --verbose
"""

import sys
from split_speakers import main as split_speakers_main

if __name__ == "__main__":
    # Call the main function from the split_speakers script.
    # The argument parsing and all other logic are handled within that script.
    try:
        split_speakers_main()
    except Exception as e:
        # This is a final catch-all for any unexpected errors that might not
        # have been handled gracefully within the script.
        print(f"❌ A critical error occurred: {e}", file=sys.stderr)
        sys.exit(1)
