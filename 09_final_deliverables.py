#!/usr/bin/env python3
"""Alias: run 09_deliverables.py (importlib — module names cannot start with a digit)."""

from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "09_deliverables.py"), run_name="__main__")
