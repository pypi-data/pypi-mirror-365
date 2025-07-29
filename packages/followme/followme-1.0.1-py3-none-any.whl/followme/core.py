"""
Core functionality for FollowMe URL redirect tracking.
"""

import requests
from urllib.parse import urljoin


def log_redirects(url):
    """
    Track and log all redirects for a given URL.
    
    Args:
        url (str): The URL to check for redirects
        
    Returns:
        list: List of tuples containing (status_code, from_url, to_url) for each redirect
              Returns None if there's an error
    """
    redirects = []
    try:
        response = requests.get(url, allow_redirects=False)
        while response.is_redirect or response.is_permanent_redirect:
            location = response.headers.get('Location')
            if not location:
                break
            redirects.append((response.status_code, response.url, location))
            if location.startswith('/'):
                location = urljoin(response.url, location)
            response = requests.get(location, allow_redirects=False)
        redirects.append((response.status_code, response.url, None))
        return redirects
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def format_report(url, redirects, colorize=True):
    """
    Format the redirect chain into a readable table report.
    
    Args:
        url (str): The original URL that was checked
        redirects (list): List of redirect tuples from log_redirects()
        colorize (bool): Whether to add color to the output
        
    Returns:
        str: Formatted table report string
    """
    if redirects is None:
        return "No redirects logged due to error."
    
    # Color codes
    colors = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
    }
    
    def color(text, color_name):
        if colorize:
            return f"{colors[color_name]}{text}{colors['reset']}"
        return text
    
    # Header
    lines = [f"{color('Redirect chain for', 'bold')} {color(url, 'cyan')}:"]
    lines.append("")  # Empty line for spacing
    
    # Table header
    header_step = color("Step", 'bold')
    header_status = color("Status", 'bold')
    header_from = color("From URL", 'bold')
    header_to = color("To URL", 'bold')
    
    # Calculate column widths
    max_step_width = max(len("Step"), len(str(len(redirects))))
    max_status_width = max(len("Status"), max(len(f"[{status}]") for status, _, _ in redirects))
    max_from_width = max(len("From URL"), max(len(from_url) for _, from_url, _ in redirects))
    max_to_width = max(len("To URL"), max(len(to_url or "(final)") for _, _, to_url in redirects))
    
    # Create header row
    header_format = f"{{:<{max_step_width}}}  {{:<{max_status_width}}}  {{:<{max_from_width}}}  {{:<{max_to_width}}}"
    lines.append(header_format.format(header_step, header_status, header_from, header_to))
    
    # Separator line
    separator = "-" * (max_step_width + max_status_width + max_from_width + max_to_width + 6)
    lines.append(color(separator, 'white'))
    
    # Data rows
    for i, (status, from_url, to_url) in enumerate(redirects):
        step_num = color(f"{i+1}", 'yellow')
        
        # Color status codes based on type
        if status == 200:
            status_colored = color(f"[{status}]", 'green')
        elif status in [301, 302, 307, 308]:
            status_colored = color(f"[{status}]", 'yellow')
        else:
            status_colored = color(f"[{status}]", 'red')
        
        from_url_colored = color(from_url, 'blue')
        
        if to_url:
            to_url_colored = color(to_url, 'magenta')
        else:
            to_url_colored = color("(final)", 'green')
        
        # Format the row
        row_format = f"{{:<{max_step_width}}}  {{:<{max_status_width}}}  {{:<{max_from_width}}}  {{:<{max_to_width}}}"
        lines.append(row_format.format(step_num, status_colored, from_url_colored, to_url_colored))
    
    return "\n".join(lines) 