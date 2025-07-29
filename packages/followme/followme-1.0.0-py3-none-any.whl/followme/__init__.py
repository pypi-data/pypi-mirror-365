"""
FollowMe - A command-line tool to track and report URL redirects.
"""

__version__ = "1.0.0"

from .core import log_redirects, format_report

__all__ = ["log_redirects", "format_report"] 