#!/usr/bin/env python
"""
Weather Dashboard CLI - Simple Entry Point

Run this file directly: python weather.py
Or just: ./weather.py (on Mac/Linux)
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main

if __name__ == "__main__":
    sys.exit(main())
