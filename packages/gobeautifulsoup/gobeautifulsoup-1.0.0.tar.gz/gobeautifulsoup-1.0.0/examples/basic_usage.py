"""
Basic usage examples for GoBeautifulSoup

This file demonstrates the most common usage patterns and shows how
GoBeautifulSoup provides a drop-in replacement for BeautifulSoup4.
"""

from gobeautifulsoup import BeautifulSoup

def basic_parsing_example():
    """Basic HTML parsing example"""
    print("=== Basic HTML Parsing ===")
    
    html = """
    <html>
        <head><title>Example Page</title></head>
        <body>
            <div class="container">
                <h1 id="main-title">Welcome to GoBeautifulSoup</h1>
                <p class="intro">This is a high-performance HTML parser.</p>
                <ul class="features">
                    <li>Fast parsing</li>
                    <li>BeautifulSoup compatibility</li>
                    <li>Go-powered backend</li>
                </ul>
            </div>
        </body>
    </html>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract title
    title = soup.find('title').get_text()
    print(f"Page title: {title}")
    
    # Find by tag and class
    heading = soup.find('h1', class_='main-title')
    if heading:
        print(f"Main heading: {heading.get_text()}")
    
    # Find by ID
    main_title = soup.find(id='main-title')
    if main_title:
        print(f"Title by ID: {main_title.get_text()}")
    
    # Get all text
    intro = soup.find('p', class_='intro')
    if intro:
        print(f"Introduction: {intro.get_text()}")

def css_selectors_example():
    """CSS selectors example"""
    print("\n=== CSS Selectors ===")
    
    html = """
    <article class="blog-post">
        <header>
            <h2 class="post-title">Understanding HTML Parsing</h2>
            <div class="meta">
                <span class="author">John Doe</span>
                <time class="date">2025-07-29</time>
            </div>
        </header>
        <div class="content">
            <p class="paragraph">HTML parsing is essential for web scraping.</p>
            <p class="paragraph">GoBeautifulSoup makes it fast and easy.</p>
        </div>
        <footer class="tags">
            <span class="tag python">Python</span>
            <span class="tag performance">Performance</span>
        </footer>
    </article>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # CSS class selector
    title = soup.select_one('.post-title')
    if title:
        print(f"Post title: {title.get_text()}")
    
    # Multiple class selector
    meta_info = soup.select('.meta span')
    for span in meta_info:
        print(f"Meta: {span.get_text()}")
    
    # Descendant selector
    paragraphs = soup.select('.content .paragraph')
    print(f"Found {len(paragraphs)} paragraphs:")
    for i, p in enumerate(paragraphs, 1):
        print(f"  {i}. {p.get_text()}")
    
    # Attribute selector
    tags = soup.select('.tag')
    print("Tags:", [tag.get_text() for tag in tags])

def find_methods_example():
    """Demonstration of find and find_all methods"""
    print("\n=== Find Methods ===")
    
    html = """
    <div class="products">
        <div class="product" data-id="1">
            <h3>Laptop</h3>
            <span class="price">$999</span>
            <a href="/product/1" class="view-link">View Details</a>
        </div>
        <div class="product" data-id="2">
            <h3>Mouse</h3>
            <span class="price">$29</span>
            <a href="/product/2" class="view-link">View Details</a>
        </div>
        <div class="product" data-id="3">
            <h3>Keyboard</h3>
            <span class="price">$79</span>
            <a href="/product/3" class="view-link">View Details</a>
        </div>
    </div>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find first product
    first_product = soup.find('div', class_='product')
    if first_product:
        name = first_product.find('h3').get_text()
        price = first_product.find('span', class_='price').get_text()
        print(f"First product: {name} - {price}")
    
    # Find all products
    all_products = soup.find_all('div', class_='product')
    print(f"\nAll products ({len(all_products)} found):")
    for product in all_products:
        name = product.find('h3').get_text()
        price = product.find('span', class_='price').get_text()
        product_id = product.get('data-id')
        print(f"  ID {product_id}: {name} - {price}")
    
    # Find all links
    links = soup.find_all('a')
    print(f"\nLinks ({len(links)} found):")
    for link in links:
        href = link.get('href')
        text = link.get_text()
        print(f"  {text}: {href}")

def attribute_access_example():
    """Working with element attributes"""
    print("\n=== Attribute Access ===")
    
    html = """
    <form id="contact-form" method="post" action="/submit" class="form modern">
        <input type="text" name="name" placeholder="Your Name" required>
        <input type="email" name="email" placeholder="Email Address" required>
        <textarea name="message" rows="5" cols="40" placeholder="Your Message"></textarea>
        <button type="submit" class="btn btn-primary" disabled>Send Message</button>
    </form>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Access form attributes
    form = soup.find('form')
    if form:
        print(f"Form ID: {form.get('id')}")
        print(f"Form method: {form.get('method')}")
        print(f"Form action: {form.get('action')}")
        print(f"Form classes: {form.get('class')}")
    
    # Access input attributes
    inputs = soup.find_all('input')
    print(f"\nInputs ({len(inputs)} found):")
    for inp in inputs:
        input_type = inp.get('type')
        name = inp.get('name')
        placeholder = inp.get('placeholder', 'No placeholder')
        required = inp.has_attr('required')
        print(f"  {input_type} input '{name}': {placeholder} (required: {required})")
    
    # Access textarea
    textarea = soup.find('textarea')
    if textarea:
        print(f"\nTextarea: {textarea.get('rows')}x{textarea.get('cols')}")
    
    # Access button
    button = soup.find('button')
    if button:
        disabled = button.has_attr('disabled')
        classes = button.get('class', [])
        print(f"\nButton: {button.get_text()} (disabled: {disabled}, classes: {classes})")

def navigation_example():
    """Element navigation example"""
    print("\n=== Element Navigation ===")
    
    html = """
    <div class="container">
        <header>
            <h1>Main Title</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
        </header>
        <main>
            <section class="content">
                <h2>Section Title</h2>
                <p>First paragraph.</p>
                <p>Second paragraph.</p>
            </section>
        </main>
    </div>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find a starting element
    h2 = soup.find('h2')
    if h2:
        print(f"Found H2: {h2.get_text()}")
        
        # Note: Full navigation not implemented in current version
        # These would work in a complete implementation:
        # parent = h2.parent
        # siblings = h2.next_siblings
        # children = h2.children
        
        print("(Navigation features will be available in future versions)")

if __name__ == "__main__":
    """Run all examples"""
    print("GoBeautifulSoup Examples")
    print("=" * 50)
    
    basic_parsing_example()
    css_selectors_example()
    find_methods_example()
    attribute_access_example()
    navigation_example()
    
    print("\n" + "=" * 50)
    print("Examples completed successfully!")
    print("For more advanced usage, see the documentation at:")
    print("https://github.com/coffeecms/gobeautifulsoup")
