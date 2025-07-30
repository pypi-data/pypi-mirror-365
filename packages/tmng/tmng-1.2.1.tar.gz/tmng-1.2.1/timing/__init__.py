# path: timing/__init__.py
"""
Performance Timing Module

A framework-agnostic, process-safe, local performance timer for Python applications.

Provides three ways to measure code execution time:
- A context manager: `with time_block()`
- A decorator: `@time_function`
- Manual controls: `time_start()` and `time_stop()`
"""

from .api import time_block, time_function, time_start, time_stop

__all__ = ["time_block", "time_function", "time_start", "time_stop"]
