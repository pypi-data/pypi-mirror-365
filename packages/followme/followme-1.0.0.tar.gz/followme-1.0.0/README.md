# FollowMe

A command-line tool to track and report URL redirects. FollowMe helps you understand the complete redirect chain of any URL by following each redirect step-by-step and providing a detailed report.

## Features

- Track complete redirect chains for any URL
- Display status codes for each redirect step with color-coded output
- Save reports to files
- Simple command-line interface
- Cross-platform compatibility
- Colorized terminal output (with option to disable)

## Installation

### From PyPI (recommended)

```bash
pip install followme
```

### From source

```bash
git clone git@github.com:rapidrabbitsoft/followme.git
cd followme
pip install -e .
```

## Usage

### Basic usage

```bash
followme https://example.com
```

This will display the redirect chain for the specified URL.

### Save output to file

```bash
followme https://example.com -o redirect_report.txt
```

### Disable colors

```bash
followme https://example.com --no-color
```

### Examples

```bash
# Check a simple redirect
followme https://bit.ly/example

# Check a URL with multiple redirects
followme https://t.co/example

# Save the report to a file
followme https://example.com -o my_report.txt

# Disable colorized output
followme https://example.com --no-color
```

## Output Format

The tool provides a clear, numbered list of each redirect in the chain with color-coded output:

- **Bold text**: Section headers
- **Cyan**: Original URL
- **Yellow**: Step numbers and redirect status codes (301, 302, 307, 308)
- **Blue**: Source URLs in the redirect chain
- **Magenta**: Destination URLs in the redirect chain
- **Green**: Final status codes (200) and "(final)" indicator
- **Red**: Error status codes

```
Redirect chain for https://example.com:
1. https://example.com --[301]--> https://www.example.com
2. https://www.example.com --[200]--> (final)
```

You can disable colors using the `--no-color` flag.

## Requirements

- Python 3.7 or higher
- requests library
- colorama (optional, for Windows color support)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Issues

If you encounter any issues, please report them on the GitHub issue tracker. 