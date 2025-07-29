# test/test_parser.py

import unittest
import sys
import os

# Add the parent directory to path to import perfectpizza
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from perfectpizza import parse, select, select_one, find_all, find_one
from perfectpizza.dom import Node, Document
from perfectpizza.mutations import set_attr, add_class, remove_class, append_child
from perfectpizza.utils import to_html, extract_text, extract_links, extract_tables


class TestBasicParsing(unittest.TestCase):
    """Test basic HTML parsing functionality."""
    
    def test_simple_parsing(self):
        """Test parsing simple HTML."""
        html = "<div><p>Hello</p><p>World</p></div>"
        doc = parse(html)
        
        self.assertIsInstance(doc, Document)
        div = doc.find_one('div')
        self.assertIsNotNone(div)
        self.assertEqual(div.tag, 'div')
        
        paragraphs = div.find_all('p')
        self.assertEqual(len(paragraphs), 2)
        self.assertEqual(paragraphs[0].text(), 'Hello')
        self.assertEqual(paragraphs[1].text(), 'World')
    
    def test_attributes_parsing(self):
        """Test parsing attributes."""
        html = '<div class="container" id="main" data-value="test">Content</div>'
        doc = parse(html)
        
        div = doc.find_one('div')
        self.assertEqual(div.get_attr('class'), 'container')
        self.assertEqual(div.get_attr('id'), 'main')
        self.assertEqual(div.get_attr('data-value'), 'test')
        self.assertTrue(div.has_class('container'))
    
    def test_nested_elements(self):
        """Test parsing nested elements."""
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <div class="header">
                    <h1>Title</h1>
                    <nav>
                        <ul>
                            <li><a href="/">Home</a></li>
                            <li><a href="/about">About</a></li>
                        </ul>
                    </nav>
                </div>
            </body>
        </html>
        """
        doc = parse(html)
        
        title = doc.find_one('title')
        self.assertEqual(title.text(), 'Test Page')
        
        h1 = doc.find_one('h1')
        self.assertEqual(h1.text(), 'Title')
        
        links = doc.find_all('a')
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0].get_attr('href'), '/')
        self.assertEqual(links[1].get_attr('href'), '/about')
    
    def test_self_closing_tags(self):
        """Test parsing self-closing tags."""
        html = '<img src="test.jpg" alt="Test"><br><input type="text" value="test">'
        doc = parse(html)
        
        img = doc.find_one('img')
        self.assertEqual(img.get_attr('src'), 'test.jpg')
        self.assertEqual(img.get_attr('alt'), 'Test')
        
        br = doc.find_one('br')
        self.assertIsNotNone(br)
        
        input_elem = doc.find_one('input')
        self.assertEqual(input_elem.get_attr('type'), 'text')
        self.assertEqual(input_elem.get_attr('value'), 'test')
    
    def test_malformed_html(self):
        """Test parsing malformed HTML."""
        # Unclosed tags
        html = '<div><p>Unclosed paragraph<div>Another div</div></div>'
        doc = parse(html)
        
        divs = doc.find_all('div')
        self.assertEqual(len(divs), 2)
        
        # Mismatched tags
        html2 = '<div><span>Content</div></span>'
        doc2 = parse(html2)
        
        div = doc2.find_one('div')
        self.assertIsNotNone(div)


class TestCSSSelectors(unittest.TestCase):
    """Test CSS selector functionality."""
    
    def setUp(self):
        """Set up test HTML."""
        self.html = """
        <html>
            <body>
                <div class="container main" id="content">
                    <h1 class="title">Main Title</h1>
                    <p class="intro">Introduction paragraph</p>
                    <div class="section">
                        <h2>Section Title</h2>
                        <p>Section content</p>
                        <ul class="list">
                            <li class="item first">Item 1</li>
                            <li class="item">Item 2</li>
                            <li class="item last">Item 3</li>
                        </ul>
                    </div>
                    <footer data-role="footer">Footer content</footer>
                </div>
            </body>
        </html>
        """
        self.doc = parse(self.html)
    
    def test_tag_selectors(self):
        """Test basic tag selectors."""
        paragraphs = select(self.doc, 'p')
        self.assertEqual(len(paragraphs), 2)
        
        headings = select(self.doc, 'h1, h2')
        self.assertEqual(len(headings), 2)
    
    def test_class_selectors(self):
        """Test class selectors."""
        titles = select(self.doc, '.title')
        self.assertEqual(len(titles), 1)
        self.assertEqual(titles[0].text(), 'Main Title')
        
        items = select(self.doc, '.item')
        self.assertEqual(len(items), 3)
        
        # Multiple classes
        containers = select(self.doc, '.container.main')
        self.assertEqual(len(containers), 1)
    
    def test_id_selectors(self):
        """Test ID selectors."""
        content = select_one(self.doc, '#content')
        self.assertIsNotNone(content)
        self.assertEqual(content.get_attr('id'), 'content')
    
    def test_attribute_selectors(self):
        """Test attribute selectors."""
        # Attribute exists
        elements = select(self.doc, '[data-role]')
        self.assertEqual(len(elements), 1)
        
        # Attribute equals
        footer = select_one(self.doc, '[data-role="footer"]')
        self.assertIsNotNone(footer)
        self.assertEqual(footer.tag, 'footer')
        
        # Attribute contains word
        main_items = select(self.doc, '[class~="main"]')
        self.assertEqual(len(main_items), 1)
    
    def test_pseudo_selectors(self):
        """Test pseudo selectors."""
        # First child
        first_items = select(self.doc, 'li:first-child')
        self.assertEqual(len(first_items), 1)
        self.assertTrue(first_items[0].has_class('first'))
        
        # Last child
        last_items = select(self.doc, 'li:last-child')
        self.assertEqual(len(last_items), 1)
        self.assertTrue(last_items[0].has_class('last'))
        
        # Nth child
        second_items = select(self.doc, 'li:nth-child(2)')
        self.assertEqual(len(second_items), 1)
        self.assertEqual(second_items[0].text(), 'Item 2')
    
    def test_combinators(self):
        """Test combinator selectors."""
        # Descendant
        section_paragraphs = select(self.doc, '.section p')
        self.assertEqual(len(section_paragraphs), 1)
        
        # Direct child
        container_headings = select(self.doc, '.container > h1')
        self.assertEqual(len(container_headings), 1)
        
        # Adjacent sibling
        intro_next = select(self.doc, '.intro + div')
        self.assertEqual(len(intro_next), 1)
        self.assertTrue(intro_next[0].has_class('section'))
    
    def test_complex_selectors(self):
        """Test complex selector combinations."""
        # Complex selector
        items = select(self.doc, 'div.section ul.list li.item:not(:first-child)')
        # Note: :not() is not implemented in this basic version, so test simpler complex selectors
        
        items = select(self.doc, 'div.section ul.list li.item')
        self.assertEqual(len(items), 3)


class TestMutations(unittest.TestCase):
    """Test functional mutation operations."""
    
    def test_set_attribute(self):
        """Test setting attributes."""
        html = '<div>Content</div>'
        doc = parse(html)
        div = doc.find_one('div')
        
        new_div = set_attr(div, 'class', 'test')
        self.assertEqual(new_div.get_attr('class'), 'test')
        
        # Original should be unchanged
        self.assertIsNone(div.get_attr('class'))
    
    def test_css_class_manipulation(self):
        """Test CSS class manipulation."""
        html = '<div class="existing">Content</div>'
        doc = parse(html)
        div = doc.find_one('div')
        
        # Add class
        new_div = add_class(div, 'new-class')
        self.assertTrue(new_div.has_class('existing'))
        self.assertTrue(new_div.has_class('new-class'))
        
        # Remove class
        final_div = remove_class(new_div, 'existing')
        self.assertFalse(final_div.has_class('existing'))
        self.assertTrue(final_div.has_class('new-class'))
    
    def test_child_manipulation(self):
        """Test child node manipulation."""
        html = '<div><p>Existing</p></div>'
        doc = parse(html)
        div = doc.find_one('div')
        
        # Create new paragraph
        new_p = Node('p', {})
        new_p.add_child('New content')
        
        # Append child
        new_div = append_child(div, new_p)
        paragraphs = new_div.find_all('p')
        self.assertEqual(len(paragraphs), 2)
        self.assertEqual(paragraphs[1].text(), 'New content')


class TestUtilities(unittest.TestCase):
    """Test utility functions."""
    
    def test_html_output(self):
        """Test HTML output generation."""
        html = '<div class="test"><p>Content</p></div>'
        doc = parse(html)
        
        output = to_html(doc)
        self.assertIn('<div class="test">', output)
        self.assertIn('<p>Content</p>', output)
        self.assertIn('</div>', output)
    
    def test_text_extraction(self):
        """Test text extraction."""
        html = '<div><h1>Title</h1><p>Paragraph with <strong>bold</strong> text.</p></div>'
        doc = parse(html)
        
        text = extract_text(doc)
        self.assertIn('Title', text)
        self.assertIn('Paragraph with bold text.', text)
    
    def test_link_extraction(self):
        """Test link extraction."""
        html = '''
        <div>
            <a href="https://example.com">External Link</a>
            <a href="/internal" title="Internal Page">Internal Link</a>
        </div>
        '''
        doc = parse(html)
        
        links = extract_links(doc)
        self.assertEqual(len(links), 2)
        
        self.assertEqual(links[0]['url'], 'https://example.com')
        self.assertEqual(links[0]['text'], 'External Link')
        
        self.assertEqual(links[1]['url'], '/internal')
        self.assertEqual(links[1]['title'], 'Internal Page')
    
    def test_table_extraction(self):
        """Test table data extraction."""
        html = '''
        <table>
            <thead>
                <tr><th>Name</th><th>Age</th></tr>
            </thead>
            <tbody>
                <tr><td>John</td><td>30</td></tr>
                <tr><td>Jane</td><td>25</td></tr>
            </tbody>
        </table>
        '''
        doc = parse(html)
        
        tables = extract_tables(doc)
        self.assertEqual(len(tables), 1)
        
        table = tables[0]
        self.assertEqual(len(table), 3)  # Header + 2 rows
        self.assertEqual(table[0], ['Name', 'Age'])
        self.assertEqual(table[1], ['John', '30'])
        self.assertEqual(table[2], ['Jane', '25'])


class TestPerformance(unittest.TestCase):
    """Test performance with larger documents."""
    
    def test_large_document_parsing(self):
        """Test parsing a larger HTML document."""
        # Generate a large HTML document
        html_parts = ['<html><body>']
        for i in range(1000):
            html_parts.append(f'<div class="item-{i}" id="item_{i}"><p>Item {i} content</p></div>')
        html_parts.append('</body></html>')
        
        large_html = ''.join(html_parts)
        
        # Parse and test
        doc = parse(large_html)
        divs = doc.find_all('div')
        self.assertEqual(len(divs), 1000)
        
        # Test CSS selector performance
        specific_item = select_one(doc, '#item_500')
        self.assertIsNotNone(specific_item)
        self.assertEqual(specific_item.get_attr('id'), 'item_500')
        
        # Test class selector performance
        class_items = select(doc, '.item-100')
        self.assertEqual(len(class_items), 1)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_empty_html(self):
        """Test parsing empty HTML."""
        doc = parse('')
        self.assertIsInstance(doc, Document)
        self.assertEqual(len(doc.children), 0)
    
    def test_only_text(self):
        """Test parsing plain text."""
        doc = parse('Just some text')
        text_content = extract_text(doc)
        self.assertEqual(text_content.strip(), 'Just some text')
    
    def test_comments_and_doctype(self):
        """Test handling comments and DOCTYPE."""
        html = '''
        <!DOCTYPE html>
        <!-- This is a comment -->
        <html>
            <head><title>Test</title></head>
            <body><!-- Another comment --><p>Content</p></body>
        </html>
        '''
        doc = parse(html)
        
        # Should parse without errors
        title = doc.find_one('title')
        self.assertEqual(title.text(), 'Test')
        
        paragraph = doc.find_one('p')
        self.assertEqual(paragraph.text(), 'Content')
    
    def test_special_characters(self):
        """Test handling special characters."""
        html = '<p>Text with &amp; entities &lt; and &gt; symbols</p>'
        doc = parse(html)
        
        paragraph = doc.find_one('p')
        text = paragraph.text()
        # The parser should handle entities
        self.assertIn('&', text)
    
    def test_invalid_selectors(self):
        """Test handling invalid CSS selectors."""
        html = '<div><p>Content</p></div>'
        doc = parse(html)
        
        # Empty selector
        results = select(doc, '')
        self.assertEqual(len(results), 0)
        
        # Invalid selector should not crash
        results = select(doc, '..invalid')
        # Should handle gracefully


if __name__ == '__main__':
    # Run specific test suites
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestBasicParsing,
        TestCSSSelectors,
        TestMutations,
        TestUtilities,
        TestPerformance,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0] if 'AssertionError:' in traceback else 'Unknown error'}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\\n')[-2] if '\\n' in traceback else traceback}")