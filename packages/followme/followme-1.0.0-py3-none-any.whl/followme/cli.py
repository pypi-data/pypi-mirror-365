"""
Command-line interface for FollowMe.
"""

import argparse
import sys
import os
from .core import log_redirects, format_report


def supports_color():
    """
    Check if the terminal supports color output.
    """
    # Check if we're in a terminal
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    
    # Check for common environment variables that disable colors
    if os.environ.get('NO_COLOR') or os.environ.get('TERM') == 'dumb':
        return False
    
    # Check if we're on Windows and using a compatible terminal
    if os.name == 'nt':
        try:
            import colorama
            return True
        except ImportError:
            return False
    
    return True


def main():
    """
    Main entry point for the command-line interface.
    """
    parser = argparse.ArgumentParser(
        description="Log and report redirects from a URL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  followme https://example.com
  followme https://bit.ly/example -o report.txt
  followme https://example.com --no-color
        """
    )
    parser.add_argument(
        "url", 
        help="The URL to check redirects for"
    )
    parser.add_argument(
        "-o", "--output", 
        help="Output file to save the report", 
        default=None
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colorized output"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="followme 1.0.0"
    )
    
    args = parser.parse_args()

    # Determine if we should use colors
    use_colors = not args.no_color and supports_color()

    redirects = log_redirects(args.url)
    report = format_report(args.url, redirects, colorize=use_colors)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"Report saved to {args.output}")
        except IOError as e:
            print(f"Error saving report: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(report)


if __name__ == "__main__":
    main() 