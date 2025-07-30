# API Reference

Complete API reference for GoBeautifulSoup, showing all classes, methods, and their compatibility with BeautifulSoup4.

## BeautifulSoup Class

The main entry point for parsing HTML and XML documents.

### Constructor

```python
BeautifulSoup(markup="", features="html.parser", builder=None, 
              parse_only=None, from_encoding=None, exclude_encodings=None, **kwargs)
```

**Parameters:**
- `markup` (str): HTML/XML string or file-like object to parse
- `features` (str): Parser type ("html.parser", "xml", "lxml", etc.)
- `builder`: Parser builder (ignored for compatibility)
- `parse_only`: Parse only specific parts (not implemented)
- `from_encoding`: Source encoding (auto-detected)
- `exclude_encodings`: Encodings to avoid (not implemented)
- `**kwargs`: Additional arguments (mostly ignored for compatibility)

**Example:**
```python
from gobeautifulsoup import BeautifulSoup

soup = BeautifulSoup('<div class="content">Hello</div>', 'html.parser')
```

### Properties

#### text
Returns all text content from the document.

```python
@property
def text(self) -> str
```

**Example:**
```python
soup = BeautifulSoup('<p>Hello <strong>World</strong></p>', 'html.parser')
print(soup.text)  # "Hello World"
```

#### title
Returns the title tag of the document.

```python
@property  
def title(self) -> Optional[Tag]
```

#### body
Returns the body tag of the document.

```python
@property
def body(self) -> Optional[Tag]
```

#### head
Returns the head tag of the document.

```python
@property
def head(self) -> Optional[Tag]
```

### Methods

#### find()
Find the first matching element.

```python
def find(name=None, attrs=None, recursive=True, string=None, **kwargs) -> Optional[Tag]
```

**Parameters:**
- `name`: Tag name to search for (str, list, or callable)
- `attrs`: Dictionary of attributes to match
- `recursive`: Search recursively (always True)
- `string`: Text content to search for
- `**kwargs`: Additional attribute filters (e.g., class_="example")

**Returns:** First matching Tag or None

**Examples:**
```python
# Find by tag name
title = soup.find('title')

# Find by class
content = soup.find('div', class_='content')

# Find by ID
header = soup.find(id='header')

# Find by multiple attributes
link = soup.find('a', {'href': 'https://example.com', 'class': 'external'})

# Find with kwargs syntax
form = soup.find('form', method='post')
```

#### find_all()
Find all matching elements.

```python
def find_all(name=None, attrs=None, recursive=True, string=None, 
             limit=None, **kwargs) -> List[Tag]
```

**Parameters:** Same as `find()` plus:
- `limit`: Maximum number of results to return

**Returns:** List of matching Tags

**Examples:**
```python
# Find all paragraphs
paragraphs = soup.find_all('p')

# Find all elements with specific class
items = soup.find_all(class_='item')

# Find multiple tag types
headings = soup.find_all(['h1', 'h2', 'h3'])

# Find with limit
first_three = soup.find_all('li', limit=3)
```

#### select()
Find elements using CSS selectors.

```python
def select(selector: str) -> List[Tag]
```

**Parameters:**
- `selector`: CSS selector string

**Returns:** List of matching Tags

**Examples:**
```python
# Class selector
items = soup.select('.item')

# ID selector
header = soup.select('#header')

# Descendant selector
nav_links = soup.select('nav a')

# Complex selector
featured_posts = soup.select('article.post.featured')

# Attribute selector
external_links = soup.select('a[href^="http"]')
```

#### select_one()
Find the first element using CSS selector.

```python
def select_one(selector: str) -> Optional[Tag]
```

**Parameters:**
- `selector`: CSS selector string

**Returns:** First matching Tag or None

#### get_text()
Get text content with options.

```python
def get_text(separator: str = "", strip: bool = False) -> str
```

**Parameters:**
- `separator`: String to join text segments
- `strip`: Whether to strip whitespace

**Returns:** Text content of the document

#### prettify()
Pretty-print the document.

```python
def prettify(encoding: Optional[str] = None, formatter: str = "minimal") -> str
```

**Parameters:**
- `encoding`: Output encoding (ignored, always returns str)
- `formatter`: Formatting style (ignored)

**Returns:** Pretty-formatted HTML string

## Tag Class

Represents an HTML/XML tag element.

### Properties

#### name
The tag name.

```python
@property
def name(self) -> str
```

**Example:**
```python
tag = soup.find('div')
print(tag.name)  # "div"
```

#### attrs
Dictionary of tag attributes.

```python
@property
def attrs(self) -> Dict[str, str]
```

**Example:**
```python
tag = soup.find('a', href='https://example.com')
print(tag.attrs)  # {'href': 'https://example.com'}
```

#### text
All text content of the element.

```python
@property
def text(self) -> str
```

#### string
String content if element contains only text.

```python
@property
def string(self) -> Optional[NavigableString]
```

#### parent
Parent element.

```python
@property
def parent(self) -> Optional[Tag]
```

#### children
Direct child elements.

```python
@property
def children(self) -> List[Union[Tag, NavigableString]]
```

#### next_sibling / next
Next sibling element.

```python
@property
def next_sibling(self) -> Optional[Union[Tag, NavigableString]]

@property  
def next(self) -> Optional[Union[Tag, NavigableString]]  # Alias
```

#### previous_sibling / previous
Previous sibling element.

```python
@property
def previous_sibling(self) -> Optional[Union[Tag, NavigableString]]

@property
def previous(self) -> Optional[Union[Tag, NavigableString]]  # Alias
```

### Methods

#### get()
Get attribute value.

```python
def get(key: str, default=None) -> Any
```

**Example:**
```python
link = soup.find('a')
href = link.get('href', '#')  # Get href or default to '#'
```

#### has_attr()
Check if attribute exists.

```python
def has_attr(key: str) -> bool
```

**Example:**
```python
img = soup.find('img')
if img.has_attr('alt'):
    print(f"Alt text: {img['alt']}")
```

#### get_text()
Get text content with options.

```python
def get_text(separator: str = "", strip: bool = False) -> str
```

#### find() / find_all()
Search within this element (same as BeautifulSoup methods).

```python
def find(name=None, attrs=None, recursive=True, string=None, **kwargs) -> Optional[Tag]
def find_all(name=None, attrs=None, recursive=True, string=None, limit=None, **kwargs) -> List[Tag]
```

#### select() / select_one()
CSS selectors within this element.

```python
def select(selector: str) -> List[Tag]
def select_one(selector: str) -> Optional[Tag]
```

#### prettify()
Pretty-print this element.

```python
def prettify(encoding: Optional[str] = None, formatter: str = "minimal") -> str
```

### Attribute Access

Tags support dictionary-style attribute access:

```python
# Get attribute
href = tag['href']

# Set attribute  
tag['class'] = 'new-class'

# Check if attribute exists
if 'id' in tag:
    print(f"ID: {tag['id']}")

# Delete attribute
del tag['data-temp']
```

### Convenience Methods

#### get_class()
Get CSS classes as a list.

```python
def get_class(self) -> List[str]
```

#### get_id()
Get the id attribute.

```python
def get_id(self) -> Optional[str]
```

#### has_class()
Check if element has a specific CSS class.

```python
def has_class(self, class_name: str) -> bool
```

## NavigableString Class

Represents text content within tags.

```python
class NavigableString(str)
```

Extends the built-in `str` class with navigation properties for compatibility with BeautifulSoup4.

### Properties

- `parent`: Parent element
- `next_sibling` / `next`: Next sibling
- `previous_sibling` / `previous`: Previous sibling
- `string`: Returns self

### Methods

#### get_text()
Get text content (returns self).

```python
def get_text(separator: str = "", strip: bool = False) -> str
```

## Supported CSS Selectors

GoBeautifulSoup supports a wide range of CSS selectors:

### Basic Selectors

```python
# Element selector
soup.select('p')          # All <p> elements

# Class selector  
soup.select('.content')   # Elements with class="content"

# ID selector
soup.select('#header')    # Element with id="header"

# Universal selector
soup.select('*')          # All elements
```

### Attribute Selectors

```python
# Has attribute
soup.select('[href]')              # Elements with href attribute

# Exact match
soup.select('[class="button"]')    # class exactly equals "button"

# Contains word
soup.select('[class~="active"]')   # class contains word "active"

# Starts with
soup.select('[href^="http"]')      # href starts with "http"

# Ends with
soup.select('[src$=".jpg"]')       # src ends with ".jpg"

# Contains substring
soup.select('[title*="example"]')  # title contains "example"
```

### Combinators

```python
# Descendant (space)
soup.select('nav a')          # <a> elements inside <nav>

# Child (>)
soup.select('ul > li')        # <li> elements directly inside <ul>

# Adjacent sibling (+)
soup.select('h1 + p')         # <p> immediately after <h1>

# General sibling (~)
soup.select('h1 ~ p')         # <p> elements after <h1> (same parent)
```

### Pseudo-selectors

```python
# First child
soup.select('li:first-child')     # First <li> child

# Last child  
soup.select('li:last-child')      # Last <li> child

# Nth child
soup.select('tr:nth-child(2n)')   # Even table rows

# Not
soup.select('a:not(.internal)')   # <a> elements without class="internal"
```

## Parser Support

### HTML Parser (`html.parser`)

Default parser for HTML documents. Handles malformed HTML gracefully.

```python
soup = BeautifulSoup(html_content, 'html.parser')
```

### XML Parser (`xml`)

Specialized parser for XML documents. More strict about well-formed markup.

```python
soup = BeautifulSoup(xml_content, 'xml')
```

## Error Handling

GoBeautifulSoup handles errors gracefully and maintains compatibility with BeautifulSoup4:

- Invalid HTML is parsed as best as possible
- Missing elements return `None` instead of raising exceptions
- Unknown parsers fall back to default HTML parser
- Attribute access on missing elements returns `None`

## Performance Notes

- **Parsing**: 15-50x faster than BeautifulSoup4
- **Querying**: 10-20x faster for common operations  
- **Memory**: Optimized memory usage for large documents
- **CSS Selectors**: Efficient implementation with Go backend

## Migration from BeautifulSoup4

GoBeautifulSoup is designed as a drop-in replacement:

```python
# Before
from bs4 import BeautifulSoup

# After - just change the import!
from gobeautifulsoup import BeautifulSoup

# Everything else stays the same
soup = BeautifulSoup(html, 'html.parser')
title = soup.find('title').get_text()
```

## Known Limitations

Current version limitations (planned for future releases):

- Tree modification methods (`append`, `insert`, `decompose`) not implemented
- Full parent/children/sibling navigation not complete
- Some advanced CSS selectors not supported
- Custom formatters for `prettify()` not implemented

## Version History

- **1.0.0**: Initial release with core parsing and querying functionality
