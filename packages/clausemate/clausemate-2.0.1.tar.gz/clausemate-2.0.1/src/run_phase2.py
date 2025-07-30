#!/usr/bin/env python3
"""Entry point for the Clause Mates Analyzer - Production Ready v2.1.

This script provides the main command-line interface for running the production-ready
clause mates analysis pipeline with 100% file format compatibility.
"""

import sys
from pathlib import Path

from src.main import main

# Add parent directory to path so we can import src modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))


if __name__ == "__main__":
    sys.exit(main())
