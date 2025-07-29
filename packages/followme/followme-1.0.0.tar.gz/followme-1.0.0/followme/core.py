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
    Format the redirect chain into a readable report.
    
    Args:
        url (str): The original URL that was checked
        redirects (list): List of redirect tuples from log_redirects()
        colorize (bool): Whether to add color to the output
        
    Returns:
        str: Formatted report string
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
    
    lines = [f"{color('Redirect chain for', 'bold')} {color(url, 'cyan')}:"]
    
    for i, (status, from_url, to_url) in enumerate(redirects):
        step_num = color(f"{i+1}.", 'yellow')
        from_url_colored = color(from_url, 'blue')
        
        # Color status codes based on type
        if status == 200:
            status_colored = color(f"[{status}]", 'green')
        elif status in [301, 302, 307, 308]:
            status_colored = color(f"[{status}]", 'yellow')
        else:
            status_colored = color(f"[{status}]", 'red')
        
        if to_url:
            to_url_colored = color(to_url, 'magenta')
            lines.append(f"{step_num} {from_url_colored} --{status_colored}--> {to_url_colored}")
        else:
            final_text = color("(final)", 'green')
            lines.append(f"{step_num} {from_url_colored} --{status_colored}--> {final_text}")
    
    return "\n".join(lines) 