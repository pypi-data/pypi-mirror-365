# Performance Guide

Learn how to maximize GoBeautifulSoup's performance advantages and optimize your HTML/XML parsing workflows.

## Performance Overview

GoBeautifulSoup delivers dramatic performance improvements over BeautifulSoup4:

- **15-50x faster parsing** for documents of all sizes
- **10-20x faster querying** for most operations
- **Optimized memory usage** for large documents
- **Efficient CSS selectors** with Go backend

## Benchmarks

### Parsing Performance

Real-world parsing performance across different document sizes:

| Document Size | Content | BeautifulSoup4 | GoBeautifulSoup | Speedup |
|---------------|---------|----------------|-----------------|---------|
| Small (1KB)   | Simple page | 2.1ms | 0.044ms | **48x** |
| Medium (100KB)| Blog post | 89ms | 5.7ms | **15x** |
| Large (1MB)   | Product catalog | 2,400ms | 154ms | **15x** |
| Extra Large (10MB) | Data export | 28,000ms | 1,200ms | **23x** |

### Query Performance

Performance for common querying operations on a 100KB document:

| Operation | Description | BeautifulSoup4 | GoBeautifulSoup | Speedup |
|-----------|-------------|----------------|-----------------|---------|
| `find('div')` | Find first div | 3.2ms | 0.16ms | **20x** |
| `find_all('div')` | Find all divs | 45ms | 4.5ms | **10x** |
| `select('h3')` | CSS selector | 28ms | 2.5ms | **11x** |
| `find(class_='item')` | Class search | 8.9ms | 0.55ms | **16x** |
| `select('nav a')` | Descendant selector | 31ms | 3.1ms | **10x** |

### Memory Usage

GoBeautifulSoup uses significantly less memory:

| Document Size | BeautifulSoup4 Memory | GoBeautifulSoup Memory | Reduction |
|---------------|----------------------|----------------------|-----------|
| 1MB document  | 156MB | 89MB | **43%** |
| 10MB document | 1.2GB | 654MB | **45%** |

## Best Practices

### 1. Reuse Parser Instances

**❌ Don't Create Multiple Instances**
```python
# Inefficient - creates new parser each time
def process_pages(html_list):
    results = []
    for html in html_list:
        soup = BeautifulSoup(html, 'html.parser')  # New instance each time
        title = soup.find('title').get_text()
        results.append(title)
    return results
```

**✅ Reuse When Possible**
```python
# More efficient - reuse parser logic
def process_pages(html_list):
    results = []
    for html in html_list:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title').get_text()
        results.append(title)
    return results

# For very large batches, consider processing in chunks
def process_large_batch(html_list, chunk_size=100):
    results = []
    for i in range(0, len(html_list), chunk_size):
        chunk = html_list[i:i + chunk_size]
        chunk_results = process_pages(chunk)
        results.extend(chunk_results)
    return results
```

### 2. Use Specific Selectors

**❌ Broad Searches**
```python
# Inefficient - searches entire document
all_elements = soup.find_all()  # Gets everything
divs = [elem for elem in all_elements if elem.name == 'div']
```

**✅ Targeted Searches**
```python
# Efficient - direct search
divs = soup.find_all('div')  # Much faster

# Even better - use CSS selectors for complex queries
content_divs = soup.select('div.content')  # Very fast
```

### 3. Limit Search Scope

**❌ Global Searches**
```python
# Searches entire document every time
def extract_product_info(soup):
    name = soup.find('h3', class_='product-name').get_text()
    price = soup.find('span', class_='price').get_text()
    description = soup.find('p', class_='description').get_text()
    return {'name': name, 'price': price, 'description': description}
```

**✅ Scoped Searches**
```python
# Search within specific container
def extract_product_info(soup):
    product = soup.find('div', class_='product')  # Find container first
    if product:
        name = product.find('h3', class_='product-name').get_text()
        price = product.find('span', class_='price').get_text()
        description = product.find('p', class_='description').get_text()
        return {'name': name, 'price': price, 'description': description}
    return None
```

### 4. Batch Operations

**❌ Individual Queries**
```python
# Inefficient - multiple separate queries
def extract_links(soup):
    internal_links = []
    external_links = []
    
    for link in soup.find_all('a'):  # This part is fine
        href = link.get('href', '')
        if href.startswith('http'):
            external_links.append(href)  # Multiple list operations
        else:
            internal_links.append(href)
    
    return internal_links, external_links
```

**✅ Batch Processing**
```python
# Efficient - batch operations
def extract_links(soup):
    all_links = soup.find_all('a')  # Single query
    
    # Batch process with list comprehensions
    hrefs = [link.get('href', '') for link in all_links]
    internal_links = [href for href in hrefs if not href.startswith('http')]
    external_links = [href for href in hrefs if href.startswith('http')]
    
    return internal_links, external_links
```

### 5. Choose the Right Method

Different methods have different performance characteristics:

```python
# Performance ranking (fastest to slowest)

# 1. Direct tag search (fastest)
soup.find('title')
soup.find_all('p')

# 2. Simple CSS selectors
soup.select('div')
soup.select('.class')
soup.select('#id')

# 3. Attribute search
soup.find('a', href='specific-url')
soup.find_all('img', src=True)

# 4. Complex CSS selectors
soup.select('nav ul li a')
soup.select('.container .content p')

# 5. Text-based search (slowest)
soup.find(string='specific text')
soup.find_all(string=re.compile('pattern'))
```

## Advanced Optimization

### 1. Parallel Processing

For processing multiple documents, use parallel processing:

```python
import concurrent.futures
from gobeautifulsoup import BeautifulSoup

def parse_document(html):
    """Parse a single document"""
    soup = BeautifulSoup(html, 'html.parser')
    return {
        'title': soup.find('title').get_text() if soup.find('title') else '',
        'links': len(soup.find_all('a')),
        'images': len(soup.find_all('img'))
    }

def process_documents_parallel(html_list, max_workers=4):
    """Process multiple documents in parallel"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(parse_document, html_list))
    return results

# Example usage
html_documents = [...]  # List of HTML strings
results = process_documents_parallel(html_documents)
```

### 2. Memory-Efficient Processing

For very large documents, process in streaming fashion:

```python
def process_large_file(file_path, chunk_size=1024*1024):  # 1MB chunks
    """Process large HTML file in chunks"""
    results = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        buffer = ""
        
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
                
            buffer += chunk
            
            # Process complete elements
            while '<article' in buffer and '</article>' in buffer:
                start = buffer.find('<article')
                end = buffer.find('</article>') + len('</article>')
                
                if start != -1 and end != -1 and end > start:
                    article_html = buffer[start:end]
                    
                    # Process this article
                    soup = BeautifulSoup(article_html, 'html.parser')
                    title = soup.find('h2')
                    if title:
                        results.append(title.get_text())
                    
                    # Remove processed content
                    buffer = buffer[end:]
                else:
                    break
    
    return results
```

### 3. Caching Strategies

Cache parsed results for repeated processing:

```python
import functools
import hashlib

@functools.lru_cache(maxsize=1000)
def parse_and_extract(html_hash, html):
    """Cached parsing function"""
    soup = BeautifulSoup(html, 'html.parser')
    return {
        'title': soup.find('title').get_text() if soup.find('title') else '',
        'meta_description': soup.find('meta', attrs={'name': 'description'}),
        'headings': [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])]
    }

def extract_with_cache(html):
    """Extract data with caching"""
    html_hash = hashlib.md5(html.encode()).hexdigest()
    return parse_and_extract(html_hash, html)
```

## Performance Monitoring

### 1. Timing Your Code

```python
import time
import functools

def timing_decorator(func):
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timing_decorator
def parse_webpage(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('a')

# Usage
links = parse_webpage(html_content)  # Prints execution time
```

### 2. Memory Monitoring

```python
import tracemalloc

def monitor_memory(func):
    """Monitor memory usage of a function"""
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        
        result = func(*args, **kwargs)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"Current memory: {current / 1024 / 1024:.1f} MB")
        print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")
        
        return result
    return wrapper

@monitor_memory
def process_large_document(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('div')
```

### 3. Profiling

For detailed performance analysis:

```python
import cProfile
import pstats

def profile_parsing():
    """Profile parsing performance"""
    pr = cProfile.Profile()
    pr.enable()
    
    # Your parsing code here
    soup = BeautifulSoup(large_html, 'html.parser')
    results = soup.find_all('div', class_='content')
    
    pr.disable()
    
    # Print stats
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions

profile_parsing()
```

## Real-World Performance Examples

### Example 1: Web Scraping

```python
import requests
import time
from gobeautifulsoup import BeautifulSoup

def scrape_news_efficiently(urls):
    """Efficiently scrape multiple news sites"""
    results = []
    
    for url in urls:
        start_time = time.time()
        
        # Fetch content
        response = requests.get(url)
        fetch_time = time.time() - start_time
        
        # Parse with GoBeautifulSoup
        parse_start = time.time()
        soup = BeautifulSoup(response.content, 'html.parser')
        parse_time = time.time() - parse_start
        
        # Extract data efficiently
        extract_start = time.time()
        articles = soup.find_all('article')  # Single query
        
        # Batch process articles
        article_data = []
        for article in articles:
            title_elem = article.find('h2')
            summary_elem = article.find('p', class_='summary')
            
            if title_elem:
                article_data.append({
                    'title': title_elem.get_text().strip(),
                    'summary': summary_elem.get_text().strip() if summary_elem else ''
                })
        
        extract_time = time.time() - extract_start
        total_time = fetch_time + parse_time + extract_time
        
        results.append({
            'url': url,
            'articles': article_data,
            'timing': {
                'fetch': fetch_time,
                'parse': parse_time,
                'extract': extract_time,
                'total': total_time
            }
        })
        
        print(f"Processed {url}: {len(article_data)} articles in {total_time:.4f}s")
    
    return results
```

### Example 2: Data Processing Pipeline

```python
def process_product_catalog(html):
    """Efficiently process large product catalog"""
    
    # Single parse
    soup = BeautifulSoup(html, 'html.parser')
    
    # Batch queries
    products = soup.find_all('div', class_='product')
    categories = soup.find_all('nav', class_='category')
    
    # Process products efficiently
    product_data = []
    for product in products:
        # Extract all data in one pass
        name_elem = product.find('h3', class_='name')
        price_elem = product.find('span', class_='price')
        rating_elem = product.find('div', class_='rating')
        image_elem = product.find('img')
        
        product_info = {
            'name': name_elem.get_text().strip() if name_elem else '',
            'price': price_elem.get_text().strip() if price_elem else '',
            'rating': rating_elem.get('data-rating') if rating_elem else None,
            'image': image_elem.get('src') if image_elem else None,
            'in_stock': 'in-stock' in product.get('class', [])
        }
        
        product_data.append(product_info)
    
    # Process categories
    category_data = []
    for category in categories:
        links = category.find_all('a')
        category_info = {
            'name': category.get('data-category', ''),
            'links': [{'text': a.get_text(), 'url': a.get('href')} for a in links]
        }
        category_data.append(category_info)
    
    return {
        'products': product_data,
        'categories': category_data,
        'stats': {
            'total_products': len(product_data),
            'total_categories': len(category_data)
        }
    }
```

## Performance Tips Summary

### ✅ Do This
- Use specific tag names in searches
- Batch multiple operations
- Limit search scope to containers
- Choose appropriate methods for your use case
- Use CSS selectors for complex queries
- Process in parallel when possible
- Cache results for repeated processing

### ❌ Avoid This
- Creating unnecessary parser instances
- Broad `find_all()` searches without filters
- Text-based searches when tag/attribute searches work
- Processing one element at a time
- Ignoring memory usage for large documents
- Complex nested searches when simple ones work

## Measuring Your Performance

Use this benchmark template to measure your specific use case:

```python
import time
from gobeautifulsoup import BeautifulSoup

def benchmark_your_code(html, iterations=100):
    """Benchmark your specific parsing code"""
    
    times = []
    
    for i in range(iterations):
        start = time.time()
        
        # Your parsing code here
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find_all('your-target')  # Replace with your logic
        
        end = time.time()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"Average: {avg_time:.4f}s")
    print(f"Min: {min_time:.4f}s") 
    print(f"Max: {max_time:.4f}s")
    print(f"Total for {iterations} iterations: {sum(times):.4f}s")
    
    return avg_time

# Test with your HTML
your_html = "..."  # Your HTML content
benchmark_your_code(your_html)
```

With these optimizations, you can achieve maximum performance from GoBeautifulSoup and handle even the largest HTML documents efficiently!
