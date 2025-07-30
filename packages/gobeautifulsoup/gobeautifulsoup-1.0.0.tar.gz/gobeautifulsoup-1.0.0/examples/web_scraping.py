"""
Web scraping example with GoBeautifulSoup

This example demonstrates how to use GoBeautifulSoup for web scraping tasks,
showing the performance benefits over traditional BeautifulSoup4.
"""

import time
import requests
from gobeautifulsoup import BeautifulSoup

def scrape_news_headlines():
    """Example: Scraping news headlines from a sample page"""
    print("=== Web Scraping Example ===")
    
    # Sample HTML that might come from a news website
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tech News Today</title>
    </head>
    <body>
        <div class="header">
            <h1>Tech News Today</h1>
            <nav class="main-nav">
                <a href="/technology">Technology</a>
                <a href="/science">Science</a>
                <a href="/business">Business</a>
            </nav>
        </div>
        
        <main class="content">
            <section class="news-section">
                <h2>Latest Headlines</h2>
                
                <article class="news-item featured" data-category="technology">
                    <header>
                        <h3 class="headline">Revolutionary AI Breakthrough Changes Everything</h3>
                        <div class="meta">
                            <span class="author">Dr. Sarah Johnson</span>
                            <time class="publish-date" datetime="2025-07-29">July 29, 2025</time>
                            <span class="category">Technology</span>
                        </div>
                    </header>
                    <div class="content">
                        <p class="summary">Scientists announce a major breakthrough in artificial intelligence that could revolutionize how we interact with technology.</p>
                        <a href="/articles/ai-breakthrough-2025" class="read-more">Read More</a>
                    </div>
                </article>
                
                <article class="news-item" data-category="science">
                    <header>
                        <h3 class="headline">New Planet Discovered in Nearby Solar System</h3>
                        <div class="meta">
                            <span class="author">Prof. Michael Chen</span>
                            <time class="publish-date" datetime="2025-07-28">July 28, 2025</time>
                            <span class="category">Science</span>
                        </div>
                    </header>
                    <div class="content">
                        <p class="summary">Astronomers have identified a potentially habitable planet just 12 light-years away from Earth.</p>
                        <a href="/articles/new-planet-discovery" class="read-more">Read More</a>
                    </div>
                </article>
                
                <article class="news-item" data-category="business">
                    <header>
                        <h3 class="headline">Green Energy Investment Reaches Record High</h3>
                        <div class="meta">
                            <span class="author">Jennifer Martinez</span>
                            <time class="publish-date" datetime="2025-07-27">July 27, 2025</time>
                            <span class="category">Business</span>
                        </div>
                    </header>
                    <div class="content">
                        <p class="summary">Global investment in renewable energy technologies hits an all-time high of $2.3 trillion this year.</p>
                        <a href="/articles/green-energy-investment" class="read-more">Read More</a>
                    </div>
                </article>
            </section>
            
            <aside class="sidebar">
                <div class="trending">
                    <h3>Trending Topics</h3>
                    <ul>
                        <li><a href="/tags/artificial-intelligence">Artificial Intelligence</a></li>
                        <li><a href="/tags/space-exploration">Space Exploration</a></li>
                        <li><a href="/tags/renewable-energy">Renewable Energy</a></li>
                        <li><a href="/tags/biotechnology">Biotechnology</a></li>
                    </ul>
                </div>
            </aside>
        </main>
        
        <footer>
            <p>&copy; 2025 Tech News Today. All rights reserved.</p>
        </footer>
    </body>
    </html>
    """
    
    # Time the parsing
    start_time = time.time()
    soup = BeautifulSoup(sample_html, 'html.parser')
    parse_time = time.time() - start_time
    
    print(f"Parsed HTML in {parse_time:.4f} seconds")
    
    # Extract page title
    title = soup.find('title')
    if title:
        print(f"Page Title: {title.get_text()}")
    
    # Extract all news headlines
    start_time = time.time()
    articles = soup.find_all('article', class_='news-item')
    query_time = time.time() - start_time
    
    print(f"\\nFound {len(articles)} articles in {query_time:.4f} seconds:\\n")
    
    for i, article in enumerate(articles, 1):
        # Extract headline
        headline_elem = article.find('h3', class_='headline')
        headline = headline_elem.get_text() if headline_elem else "No headline"
        
        # Extract author
        author_elem = article.find('span', class_='author')
        author = author_elem.get_text() if author_elem else "Unknown"
        
        # Extract date
        date_elem = article.find('time', class_='publish-date')
        date = date_elem.get('datetime') if date_elem else "Unknown"
        
        # Extract category
        category = article.get('data-category', 'Unknown')
        
        # Extract summary
        summary_elem = article.find('p', class_='summary')
        summary = summary_elem.get_text() if summary_elem else "No summary"
        
        # Extract link
        link_elem = article.find('a', class_='read-more')
        link = link_elem.get('href') if link_elem else "#"
        
        print(f"{i}. {headline}")
        print(f"   Author: {author}")
        print(f"   Date: {date}")
        print(f"   Category: {category.title()}")
        print(f"   Summary: {summary}")
        print(f"   Link: {link}")
        print()

def scrape_product_listings():
    """Example: Scraping product information from an e-commerce page"""
    print("\\n=== E-commerce Scraping Example ===")
    
    ecommerce_html = """
    <div class="product-grid">
        <div class="product-card" data-product-id="12345">
            <div class="product-image">
                <img src="/images/laptop-pro.jpg" alt="Professional Laptop">
                <span class="badge sale">On Sale</span>
            </div>
            <div class="product-info">
                <h3 class="product-name">Ultra Pro Laptop 15"</h3>
                <div class="rating">
                    <span class="stars" data-rating="4.5">★★★★☆</span>
                    <span class="review-count">(1,234 reviews)</span>
                </div>
                <div class="pricing">
                    <span class="current-price">$1,299.99</span>
                    <span class="original-price">$1,599.99</span>
                    <span class="discount">19% off</span>
                </div>
                <div class="features">
                    <ul>
                        <li>Intel i7 Processor</li>
                        <li>16GB RAM</li>
                        <li>512GB SSD</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="product-card" data-product-id="12346">
            <div class="product-image">
                <img src="/images/wireless-mouse.jpg" alt="Wireless Mouse">
                <span class="badge new">New Arrival</span>
            </div>
            <div class="product-info">
                <h3 class="product-name">Precision Wireless Mouse</h3>
                <div class="rating">
                    <span class="stars" data-rating="4.8">★★★★★</span>
                    <span class="review-count">(567 reviews)</span>
                </div>
                <div class="pricing">
                    <span class="current-price">$79.99</span>
                </div>
                <div class="features">
                    <ul>
                        <li>Ergonomic Design</li>
                        <li>Wireless Connection</li>
                        <li>Long Battery Life</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="product-card" data-product-id="12347">
            <div class="product-image">
                <img src="/images/mechanical-keyboard.jpg" alt="Mechanical Keyboard">
            </div>
            <div class="product-info">
                <h3 class="product-name">Mechanical Gaming Keyboard</h3>
                <div class="rating">
                    <span class="stars" data-rating="4.2">★★★★☆</span>
                    <span class="review-count">(89 reviews)</span>
                </div>
                <div class="pricing">
                    <span class="current-price">$149.99</span>
                </div>
                <div class="features">
                    <ul>
                        <li>Cherry MX Switches</li>
                        <li>RGB Backlight</li>
                        <li>Programmable Keys</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    """
    
    soup = BeautifulSoup(ecommerce_html, 'html.parser')
    
    # Find all products
    products = soup.find_all('div', class_='product-card')
    print(f"Found {len(products)} products:\\n")
    
    for product in products:
        # Extract product information
        product_id = product.get('data-product-id')
        
        name_elem = product.find('h3', class_='product-name')
        name = name_elem.get_text() if name_elem else "Unknown Product"
        
        # Extract rating
        rating_elem = product.find('span', class_='stars')
        rating = rating_elem.get('data-rating') if rating_elem else "No rating"
        
        review_elem = product.find('span', class_='review-count')
        reviews = review_elem.get_text() if review_elem else "No reviews"
        
        # Extract pricing
        price_elem = product.find('span', class_='current-price')
        current_price = price_elem.get_text() if price_elem else "Price not available"
        
        original_price_elem = product.find('span', class_='original-price')
        original_price = original_price_elem.get_text() if original_price_elem else None
        
        # Extract badge (sale, new, etc.)
        badge_elem = product.find('span', class_='badge')
        badge = badge_elem.get_text() if badge_elem else None
        
        # Extract features
        feature_items = product.find_all('li')
        features = [item.get_text() for item in feature_items]
        
        print(f"Product ID: {product_id}")
        print(f"Name: {name}")
        print(f"Rating: {rating} stars {reviews}")
        print(f"Price: {current_price}")
        if original_price:
            print(f"Original Price: {original_price}")
        if badge:
            print(f"Badge: {badge}")
        if features:
            print(f"Features: {', '.join(features)}")
        print("-" * 50)

def extract_structured_data():
    """Example: Extracting structured data for analysis"""
    print("\\n=== Structured Data Extraction ===")
    
    data_html = """
    <table class="financial-data">
        <thead>
            <tr>
                <th>Company</th>
                <th>Symbol</th>
                <th>Price</th>
                <th>Change</th>
                <th>Volume</th>
                <th>Market Cap</th>
            </tr>
        </thead>
        <tbody>
            <tr class="stock-row" data-symbol="AAPL">
                <td class="company">Apple Inc.</td>
                <td class="symbol">AAPL</td>
                <td class="price positive">$189.25</td>
                <td class="change positive">+2.34 (+1.25%)</td>
                <td class="volume">45.2M</td>
                <td class="market-cap">$2.98T</td>
            </tr>
            <tr class="stock-row" data-symbol="GOOGL">
                <td class="company">Alphabet Inc.</td>
                <td class="symbol">GOOGL</td>
                <td class="price positive">$142.87</td>
                <td class="change positive">+1.12 (+0.79%)</td>
                <td class="volume">28.7M</td>
                <td class="market-cap">$1.76T</td>
            </tr>
            <tr class="stock-row" data-symbol="MSFT">
                <td class="company">Microsoft Corp.</td>
                <td class="symbol">MSFT</td>
                <td class="price negative">$413.21</td>
                <td class="change negative">-3.45 (-0.83%)</td>
                <td class="volume">22.1M</td>
                <td class="market-cap">$3.07T</td>
            </tr>
        </tbody>
    </table>
    """
    
    soup = BeautifulSoup(data_html, 'html.parser')
    
    # Extract table data
    rows = soup.find_all('tr', class_='stock-row')
    
    stocks_data = []
    for row in rows:
        # Extract data from each cell
        symbol = row.get('data-symbol')
        
        company_elem = row.find('td', class_='company')
        company = company_elem.get_text() if company_elem else ""
        
        price_elem = row.find('td', class_='price')
        price = price_elem.get_text().replace('$', '') if price_elem else "0"
        
        change_elem = row.find('td', class_='change')
        change = change_elem.get_text() if change_elem else ""
        
        volume_elem = row.find('td', class_='volume')
        volume = volume_elem.get_text() if volume_elem else ""
        
        market_cap_elem = row.find('td', class_='market-cap')
        market_cap = market_cap_elem.get_text() if market_cap_elem else ""
        
        # Determine if price is up or down
        price_trend = "up" if price_elem and "positive" in price_elem.get('class', []) else "down"
        
        stock_data = {
            'symbol': symbol,
            'company': company,
            'price': price,
            'change': change,
            'volume': volume,
            'market_cap': market_cap,
            'trend': price_trend
        }
        
        stocks_data.append(stock_data)
    
    # Display extracted data
    print("Extracted Stock Data:\\n")
    for stock in stocks_data:
        trend_symbol = "📈" if stock['trend'] == "up" else "📉"
        print(f"{trend_symbol} {stock['company']} ({stock['symbol']})")
        print(f"   Price: ${stock['price']}")
        print(f"   Change: {stock['change']}")
        print(f"   Volume: {stock['volume']}")
        print(f"   Market Cap: {stock['market_cap']}")
        print()

def performance_comparison():
    """Show performance benefits of GoBeautifulSoup"""
    print("\\n=== Performance Benefits ===")
    
    # Large HTML content for performance testing
    large_html = "<html><body>"
    for i in range(1000):
        large_html += f"""
        <div class="item-{i}" data-id="{i}">
            <h3>Item {i}</h3>
            <p class="description">Description for item {i}</p>
            <span class="price">${(i % 100) + 10}.99</span>
            <a href="/item/{i}" class="link">View Item {i}</a>
        </div>
        """
    large_html += "</body></html>"
    
    print(f"Testing with large HTML document ({len(large_html):,} characters)")
    
    # Test parsing speed
    start_time = time.time()
    soup = BeautifulSoup(large_html, 'html.parser')
    parse_time = time.time() - start_time
    
    print(f"✅ Parsing completed in {parse_time:.4f} seconds")
    
    # Test query speed
    start_time = time.time()
    divs = soup.find_all('div')
    query_time = time.time() - start_time
    
    print(f"✅ Found {len(divs)} div elements in {query_time:.4f} seconds")
    
    # Test CSS selector speed
    start_time = time.time()
    links = soup.select('a.link')
    css_time = time.time() - start_time
    
    print(f"✅ Found {len(links)} links with CSS selector in {css_time:.4f} seconds")
    
    print(f"\\n🚀 Total processing time: {parse_time + query_time + css_time:.4f} seconds")
    print("   (This would be significantly slower with traditional BeautifulSoup4)")

if __name__ == "__main__":
    """Run all web scraping examples"""
    print("GoBeautifulSoup Web Scraping Examples")
    print("=" * 60)
    
    scrape_news_headlines()
    scrape_product_listings()
    extract_structured_data()
    performance_comparison()
    
    print("\\n" + "=" * 60)
    print("Web scraping examples completed!")
    print("\\nKey Benefits Demonstrated:")
    print("• Fast HTML parsing and querying")
    print("• Easy data extraction with familiar BeautifulSoup API")
    print("• Excellent performance on large documents")
    print("• Perfect for production web scraping workloads")
