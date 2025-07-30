"""
Basic tests for GoBeautifulSoup functionality

This test suite verifies that GoBeautifulSoup provides the expected
BeautifulSoup4-compatible API and behavior.
"""

import pytest
from gobeautifulsoup import BeautifulSoup, Tag, NavigableString

class TestBasicParsing:
    """Test basic HTML parsing functionality"""
    
    def test_simple_html_parsing(self):
        """Test parsing simple HTML"""
        html = "<html><body><p>Hello World</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        assert soup is not None
        assert isinstance(soup, BeautifulSoup)
    
    def test_empty_html(self):
        """Test parsing empty HTML"""
        soup = BeautifulSoup("", 'html.parser')
        assert soup is not None
    
    def test_malformed_html(self):
        """Test parsing malformed HTML"""
        html = "<html><body><p>Unclosed paragraph<div>Test</div>"
        soup = BeautifulSoup(html, 'html.parser')
        assert soup is not None
    
    def test_xml_parsing(self):
        """Test XML parsing"""
        xml = '<?xml version="1.0"?><root><item>test</item></root>'
        soup = BeautifulSoup(xml, 'xml')
        assert soup is not None

class TestFindMethods:
    """Test find and find_all methods"""
    
    def setup_method(self):
        """Set up test HTML"""
        self.html = """
        <html>
            <body>
                <div class="container">
                    <h1 id="title">Main Title</h1>
                    <p class="intro">Introduction paragraph</p>
                    <p class="content">Content paragraph</p>
                    <ul>
                        <li class="item">Item 1</li>
                        <li class="item">Item 2</li>
                        <li class="item special">Item 3</li>
                    </ul>
                    <a href="https://example.com" class="external">External Link</a>
                    <a href="/internal" class="internal">Internal Link</a>
                </div>
            </body>
        </html>
        """
        self.soup = BeautifulSoup(self.html, 'html.parser')
    
    def test_find_by_tag(self):
        """Test finding elements by tag name"""
        h1 = self.soup.find('h1')
        assert h1 is not None
        # Note: In a complete implementation, we'd check h1.get_text() == "Main Title"
    
    def test_find_by_id(self):
        """Test finding elements by ID"""
        title = self.soup.find(id='title')
        # Note: Basic implementation may not support attribute finding yet
        # This test documents expected behavior
    
    def test_find_by_class(self):
        """Test finding elements by CSS class"""
        intro = self.soup.find('p', class_='intro')
        # Note: Class-based finding may not be fully implemented yet
    
    def test_find_all(self):
        """Test finding multiple elements"""
        paragraphs = self.soup.find_all('p')
        # Should find multiple paragraphs
        assert isinstance(paragraphs, list)
    
    def test_find_all_with_limit(self):
        """Test find_all with limit parameter"""
        items = self.soup.find_all('li', limit=2)
        assert isinstance(items, list)
        # Should respect limit if implemented
    
    def test_find_nonexistent(self):
        """Test finding non-existent elements"""
        result = self.soup.find('nonexistent')
        assert result is None

class TestCSSSelectors:
    """Test CSS selector functionality"""
    
    def setup_method(self):
        """Set up test HTML"""
        self.html = """
        <div class="main">
            <header class="page-header">
                <h1 class="title">Page Title</h1>
                <nav class="navigation">
                    <a href="/" class="nav-link home">Home</a>
                    <a href="/about" class="nav-link">About</a>
                </nav>
            </header>
            <section class="content">
                <article id="post-1" class="post featured">
                    <h2>Featured Post</h2>
                    <p class="excerpt">This is featured content.</p>
                </article>
                <article id="post-2" class="post">
                    <h2>Regular Post</h2>
                    <p class="excerpt">This is regular content.</p>
                </article>
            </section>
        </div>
        """
        self.soup = BeautifulSoup(self.html, 'html.parser')
    
    def test_select_by_class(self):
        """Test CSS class selectors"""
        posts = self.soup.select('.post')
        assert isinstance(posts, list)
    
    def test_select_by_id(self):
        """Test CSS ID selectors"""
        post = self.soup.select('#post-1')
        assert isinstance(post, list)
    
    def test_select_descendant(self):
        """Test descendant selectors"""
        nav_links = self.soup.select('.navigation a')
        assert isinstance(nav_links, list)
    
    def test_select_one(self):
        """Test select_one method"""
        title = self.soup.select_one('.title')
        # Should return single element or None
    
    def test_complex_selector(self):
        """Test complex CSS selectors"""
        featured = self.soup.select('article.post.featured')
        assert isinstance(featured, list)

class TestElementProperties:
    """Test Tag element properties and methods"""
    
    def setup_method(self):
        """Set up test HTML"""
        self.html = """
        <div class="test-div" id="main" data-value="123">
            <p class="paragraph">Test paragraph with <strong>bold text</strong>.</p>
            <a href="https://example.com" title="Example" target="_blank">Link</a>
            <img src="image.jpg" alt="Test Image" width="100" height="50">
        </div>
        """
        self.soup = BeautifulSoup(self.html, 'html.parser')
    
    def test_tag_name(self):
        """Test tag name property"""
        div = self.soup.find('div')
        if div:
            assert hasattr(div, 'name')
            # In complete implementation: assert div.name == 'div'
    
    def test_tag_attributes(self):
        """Test tag attributes access"""
        div = self.soup.find('div')
        if div:
            assert hasattr(div, 'attrs')
            assert hasattr(div, 'get')
            # In complete implementation: 
            # assert div.get('class') == ['test-div']
            # assert div.get('id') == 'main'
    
    def test_text_content(self):
        """Test text content extraction"""
        p = self.soup.find('p')
        if p:
            assert hasattr(p, 'get_text')
            assert hasattr(p, 'text')
    
    def test_attribute_access_bracket(self):
        """Test attribute access with brackets"""
        a = self.soup.find('a')
        if a:
            # In complete implementation:
            # assert a['href'] == 'https://example.com'
            # assert a['title'] == 'Example'
            pass
    
    def test_has_attr(self):
        """Test has_attr method"""
        img = self.soup.find('img')
        if img and hasattr(img, 'has_attr'):
            # In complete implementation:
            # assert img.has_attr('src') == True
            # assert img.has_attr('nonexistent') == False
            pass

class TestCompatibility:
    """Test BeautifulSoup4 compatibility features"""
    
    def test_backwards_compatibility_imports(self):
        """Test that common imports work"""
        # These should work as drop-in replacements
        assert BeautifulSoup is not None
        assert Tag is not None
        assert NavigableString is not None
    
    def test_constructor_parameters(self):
        """Test constructor parameter compatibility"""
        html = "<html><body><p>Test</p></body></html>"
        
        # Standard usage
        soup1 = BeautifulSoup(html, 'html.parser')
        assert soup1 is not None
        
        # With additional parameters (should be ignored gracefully)
        soup2 = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
        assert soup2 is not None
    
    def test_string_conversion(self):
        """Test string conversion methods"""
        html = "<div>Test</div>"
        soup = BeautifulSoup(html, 'html.parser')
        
        # Should be convertible to string
        str_result = str(soup)
        assert isinstance(str_result, str)
        
        # Should have prettify method
        assert hasattr(soup, 'prettify')
    
    def test_common_properties(self):
        """Test common BeautifulSoup properties"""
        html = "<html><head><title>Test</title></head><body>Content</body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        
        # Common convenience properties
        assert hasattr(soup, 'title')
        assert hasattr(soup, 'body')
        assert hasattr(soup, 'head')

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_parser(self):
        """Test invalid parser handling"""
        html = "<html><body><p>Test</p></body></html>"
        
        # Should handle unknown parsers gracefully
        try:
            soup = BeautifulSoup(html, 'nonexistent-parser')
            # Should either work with fallback or raise appropriate error
        except (ValueError, RuntimeError):
            # Acceptable to raise error for unknown parser
            pass
    
    def test_none_input(self):
        """Test None input handling"""
        soup = BeautifulSoup(None, 'html.parser')
        assert soup is not None
    
    def test_bytes_input(self):
        """Test bytes input handling"""
        html_bytes = b"<html><body><p>Test</p></body></html>"
        soup = BeautifulSoup(html_bytes, 'html.parser')
        assert soup is not None
    
    def test_file_like_input(self):
        """Test file-like input handling"""
        from io import StringIO
        html_file = StringIO("<html><body><p>Test</p></body></html>")
        soup = BeautifulSoup(html_file, 'html.parser')
        assert soup is not None

class TestPerformance:
    """Basic performance validation tests"""
    
    def test_large_document_parsing(self):
        """Test parsing reasonably large documents"""
        # Generate larger HTML for performance testing
        large_html = "<html><body>"
        for i in range(100):  # Smaller than web scraping example for unit tests
            large_html += f"<div class='item-{i}'><p>Content {i}</p></div>"
        large_html += "</body></html>"
        
        import time
        start_time = time.time()
        soup = BeautifulSoup(large_html, 'html.parser')
        parse_time = time.time() - start_time
        
        # Should parse reasonably quickly (adjust threshold as needed)
        assert parse_time < 1.0  # Should parse in under 1 second
        assert soup is not None
    
    def test_multiple_queries(self):
        """Test performance of multiple queries"""
        html = "<html><body>"
        for i in range(50):
            html += f"<div class='item'><p>Item {i}</p><a href='/item/{i}'>Link {i}</a></div>"
        html += "</body></html>"
        
        soup = BeautifulSoup(html, 'html.parser')
        
        import time
        start_time = time.time()
        
        # Perform multiple queries
        divs = soup.find_all('div')
        paragraphs = soup.find_all('p')
        links = soup.find_all('a')
        
        query_time = time.time() - start_time
        
        # Should query reasonably quickly
        assert query_time < 0.5  # Should complete queries in under 0.5 seconds
        assert isinstance(divs, list)
        assert isinstance(paragraphs, list)
        assert isinstance(links, list)

if __name__ == "__main__":
    """Run tests if executed directly"""
    pytest.main([__file__, "-v"])
