#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI ToolShed package initializer.
Provides unified access to CLI and bootstrap utilities.
"""

from toolshed.cli import main as _main


def main():
    """Entry point for python -m toolshed"""
    _main()


__all__ = ["main"]
