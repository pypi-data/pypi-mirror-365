"""
GoBeautifulSoup - A high-performance BeautifulSoup replacement powered by Go

GoBeautifulSoup provides a 100% compatible API with BeautifulSoup4, but with
dramatically improved performance thanks to a Go-powered backend.

Example:
    from gobeautifulsoup import BeautifulSoup
    
    html = "<html><body><p>Hello World!</p></body></html>"
    soup = BeautifulSoup(html, 'html.parser')
    print(soup.find('p').get_text())  # "Hello World!"
"""

__version__ = "1.0.0"
__author__ = "CoffeeCMS Team"
__email__ = "team@coffeecms.com"
__license__ = "MIT"
__description__ = "A high-performance BeautifulSoup replacement powered by Go"
__url__ = "https://github.com/coffeecms/gobeautifulsoup"

from .soup import BeautifulSoup
from .element import Tag, NavigableString

__all__ = ['BeautifulSoup', 'Tag', 'NavigableString']

# For backwards compatibility
def __getattr__(name):
    """Provide backwards compatibility for common BeautifulSoup4 imports"""
    if name == "Comment":
        return NavigableString
    elif name == "CData":
        return NavigableString
    elif name == "ProcessingInstruction":
        return NavigableString
    elif name == "Doctype":
        return NavigableString
    elif name == "NavigableString":
        return NavigableString
    elif name == "Tag":
        return Tag
    elif name == "BeautifulSoup":
        return BeautifulSoup
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
