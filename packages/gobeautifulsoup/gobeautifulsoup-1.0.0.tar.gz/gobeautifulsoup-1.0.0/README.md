# GoBeautifulSoup

[![PyPI version](https://badge.fury.io/py/gobeautifulsoup.svg)](https://badge.fury.io/py/gobeautifulsoup)
[![Python versions](https://img.shields.io/pypi/pyversions/gobeautifulsoup.svg)](https://pypi.org/project/gobeautifulsoup/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/gobeautifulsoup)](https://pepy.tech/project/gobeautifulsoup)

**GoBeautifulSoup** is a high-performance HTML/XML parsing library that provides a 100% compatible API with BeautifulSoup4, but powered by Go for dramatically improved performance. It's designed as a drop-in replacement for BeautifulSoup4 with significant speed improvements.

## 🚀 Why GoBeautifulSoup?

- **🔥 Up to 10-50x faster** than BeautifulSoup4 for parsing and querying
- **🔄 100% API Compatible** - Drop-in replacement for BeautifulSoup4
- **⚡ Go-Powered Backend** - Leverages Go's performance for HTML/XML processing
- **🌐 Cross-Platform** - Works on Windows, macOS, and Linux (x64/ARM64)
- **💾 Memory Efficient** - Optimized memory usage for large documents
- **🛡️ Production Ready** - Thoroughly tested with comprehensive benchmarks

## 📊 Performance Comparison

GoBeautifulSoup dramatically outperforms BeautifulSoup4 across all operations:

### Parsing Performance

| Document Size | GoBeautifulSoup | BeautifulSoup4 (html.parser) | BeautifulSoup4 (lxml) | Speed Improvement |
|---------------|-----------------|-------------------------------|----------------------|-------------------|
| Small (1KB)   | 0.044ms        | 2.1ms                        | 1.8ms               | **48x faster**    |
| Medium (100KB)| 5.7ms          | 89ms                         | 76ms                | **15x faster**    |
| Large (1MB)   | 154ms          | 2,400ms                      | 1,980ms             | **15x faster**    |

### Query Performance (Medium Document)

| Operation              | GoBeautifulSoup | BeautifulSoup4 | Speed Improvement |
|------------------------|-----------------|----------------|-------------------|
| `find('div')`         | 0.16ms         | 3.2ms         | **20x faster**    |
| `find_all('div')`     | 4.5ms          | 45ms          | **10x faster**    |
| `select('h3')`        | 2.5ms          | 28ms          | **11x faster**    |
| `find(class_='item')` | 0.55ms         | 8.9ms         | **16x faster**    |

## 🔧 Installation

```bash
pip install gobeautifulsoup
```

## 📖 Quick Start

GoBeautifulSoup provides the exact same API as BeautifulSoup4:

```python
from gobeautifulsoup import BeautifulSoup

# Parse HTML
html = """
<html>
    <head><title>Example</title></head>
    <body>
        <div class="container">
            <p class="highlight">Hello World!</p>
            <a href="https://example.com">Link</a>
        </div>
    </body>
</html>
"""

soup = BeautifulSoup(html, 'html.parser')

# All familiar BeautifulSoup methods work exactly the same
title = soup.find('title').get_text()
print(title)  # "Example"

paragraph = soup.find('p', class_='highlight')
print(paragraph.get_text())  # "Hello World!"

links = soup.find_all('a')
for link in links:
    print(link.get('href'))  # "https://example.com"
```

## 💡 Usage Examples

### 1. Basic HTML Parsing

```python
from gobeautifulsoup import BeautifulSoup

html = """
<html>
    <body>
        <h1>Welcome</h1>
        <p class="intro">This is an introduction.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
        </ul>
    </body>
</html>
"""

soup = BeautifulSoup(html, 'html.parser')

# Find elements
heading = soup.find('h1')
print(f"Heading: {heading.get_text()}")

# Find by class
intro = soup.find('p', class_='intro')
print(f"Introduction: {intro.get_text()}")

# Find all list items
items = soup.find_all('li')
for i, item in enumerate(items, 1):
    print(f"Item {i}: {item.get_text()}")
```

### 2. Web Scraping with Requests

```python
import requests
from gobeautifulsoup import BeautifulSoup

# Scrape a webpage
url = "https://httpbin.org/html"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract all links
links = soup.find_all('a')
for link in links:
    href = link.get('href')
    text = link.get_text().strip()
    if href:
        print(f"Link: {text} -> {href}")

# Extract all headings
for heading in soup.find_all(['h1', 'h2', 'h3']):
    print(f"{heading.name}: {heading.get_text()}")
```

### 3. CSS Selector Support

```python
from gobeautifulsoup import BeautifulSoup

html = """
<div class="content">
    <article id="post-1" class="post featured">
        <h2>Featured Post</h2>
        <p class="excerpt">This is a featured post excerpt.</p>
    </article>
    <article id="post-2" class="post">
        <h2>Regular Post</h2>
        <p class="excerpt">This is a regular post excerpt.</p>
    </article>
</div>
"""

soup = BeautifulSoup(html, 'html.parser')

# CSS selectors work exactly like BeautifulSoup4
featured_posts = soup.select('.post.featured')
print(f"Featured posts: {len(featured_posts)}")

# Complex selectors
excerpts = soup.select('article p.excerpt')
for excerpt in excerpts:
    print(f"Excerpt: {excerpt.get_text()}")

# ID selectors
specific_post = soup.select('#post-1 h2')[0]
print(f"Specific post title: {specific_post.get_text()}")
```

### 4. XML Processing

```python
from gobeautifulsoup import BeautifulSoup

xml_data = """
<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <book id="1">
        <title>Python Programming</title>
        <author>John Doe</author>
        <price currency="USD">29.99</price>
    </book>
    <book id="2">
        <title>Web Development</title>
        <author>Jane Smith</author>
        <price currency="USD">34.99</price>
    </book>
</catalog>
"""

soup = BeautifulSoup(xml_data, 'xml')

# Process XML data
books = soup.find_all('book')
for book in books:
    book_id = book.get('id')
    title = book.find('title').get_text()
    author = book.find('author').get_text()
    price = book.find('price')
    
    print(f"Book {book_id}: {title} by {author}")
    print(f"Price: {price.get('currency')} {price.get_text()}")
    print("-" * 40)
```

### 5. Advanced Data Extraction

```python
from gobeautifulsoup import BeautifulSoup
import re

html = """
<table class="data-table">
    <thead>
        <tr>
            <th>Product</th>
            <th>Price</th>
            <th>Stock</th>
        </tr>
    </thead>
    <tbody>
        <tr data-product-id="123">
            <td class="product-name">Laptop</td>
            <td class="price">$999.99</td>
            <td class="stock in-stock">Available</td>
        </tr>
        <tr data-product-id="124">
            <td class="product-name">Mouse</td>
            <td class="price">$29.99</td>
            <td class="stock out-of-stock">Out of Stock</td>
        </tr>
    </tbody>
</table>
"""

soup = BeautifulSoup(html, 'html.parser')

# Extract structured data
products = []
rows = soup.select('tbody tr')

for row in rows:
    product_id = row.get('data-product-id')
    name = row.select_one('.product-name').get_text()
    price_text = row.select_one('.price').get_text()
    stock_cell = row.select_one('.stock')
    
    # Extract price using regex
    price_match = re.search(r'\$(\d+\.?\d*)', price_text)
    price = float(price_match.group(1)) if price_match else 0.0
    
    # Determine stock status
    in_stock = 'in-stock' in stock_cell.get('class', [])
    
    products.append({
        'id': product_id,
        'name': name,
        'price': price,
        'in_stock': in_stock
    })

# Display extracted data
for product in products:
    status = "✅ Available" if product['in_stock'] else "❌ Out of Stock"
    print(f"{product['name']} (ID: {product['id']})")
    print(f"Price: ${product['price']:.2f} | Status: {status}")
    print("-" * 50)
```

## 🔄 Migration from BeautifulSoup4

GoBeautifulSoup is designed as a drop-in replacement. Simply change your import:

```python
# Before
from bs4 import BeautifulSoup

# After  
from gobeautifulsoup import BeautifulSoup

# Everything else stays exactly the same!
```

## 📋 Supported Features

✅ **Full BeautifulSoup4 API Compatibility**
- `find()` and `find_all()` methods
- CSS selector support with `select()`
- Tree navigation (parent, children, siblings)
- Attribute access and modification
- Text extraction and manipulation

✅ **Parser Support**
- HTML parser (`html.parser`)
- XML parser (`xml`) 
- Automatic encoding detection

✅ **Advanced Features**
- Regular expression search
- Custom attribute filters
- Tree modification methods
- Pretty printing

## 🏗️ Architecture

GoBeautifulSoup consists of two main components:

1. **Go Core**: High-performance HTML/XML parsing engine written in Go
2. **Python Wrapper**: Provides BeautifulSoup4-compatible API

The Go core handles all the heavy lifting (parsing, querying, tree traversal), while the Python wrapper ensures 100% API compatibility.

## 🌟 Performance Tips

1. **Reuse Parser**: For multiple documents, reuse the BeautifulSoup instance when possible
2. **Use Specific Selectors**: More specific CSS selectors perform better than broad searches
3. **Limit Search Scope**: Use `find()` instead of `find_all()` when you only need one result
4. **Choose Right Parser**: Use 'html.parser' for HTML and 'xml' for XML documents

## 📚 Documentation

- **API Reference**: [docs/api.md](docs/api.md)
- **Migration Guide**: [docs/migration.md](docs/migration.md)
- **Performance Guide**: [docs/performance.md](docs/performance.md)
- **Examples**: [examples/](examples/)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Bug Reports

Found a bug? Please create an issue on [GitHub Issues](https://github.com/coffeecms/gobeautifulsoup/issues) with:

- Python version
- Operating system
- Minimal code example
- Expected vs actual behavior

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the excellent [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) library by Leonard Richardson
- Built with [Go](https://golang.org/) for maximum performance
- Thanks to all contributors and users

## 📊 Project Stats

- **GitHub**: https://github.com/coffeecms/gobeautifulsoup
- **PyPI**: https://pypi.org/project/gobeautifulsoup/
- **Documentation**: https://gobeautifulsoup.readthedocs.io/
- **Benchmarks**: [benchmarks/](benchmarks/)

---

**Ready to supercharge your HTML parsing? Install GoBeautifulSoup today and experience the performance difference!**

```bash
pip install gobeautifulsoup
```
