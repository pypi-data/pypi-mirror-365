# example.py

"""
🍕 PerfectPizza Example Usage

This example demonstrates the key features of PerfectPizza:
- Fast HTML parsing
- CSS4 selectors
- Functional mutations
- Text and data extraction
- Pretty HTML output
"""

from perfectpizza import parse, select, select_one, pizza
from perfectpizza.mutations import set_attr, add_class, remove_class, append_child, clone_node
from perfectpizza.utils import to_html, pretty_html, extract_text, extract_links, extract_tables
from perfectpizza.dom import Node

def main():
    print("🍕 PerfectPizza Example - Modern HTML Parsing")
    print("=" * 50)
    
    # Example 1: Basic Parsing and Querying
    print("\n1. Basic HTML Parsing")
    html = """
    <html>
        <head>
            <title>PerfectPizza Demo</title>
            <meta name="description" content="A blazing-fast HTML parser">
        </head>
        <body>
            <div class="container main" id="content">
                <h1 class="title">Welcome to PerfectPizza! 🍕</h1>
                <p class="intro">The fastest, most functional HTML parser for Python.</p>
                
                <div class="features">
                    <h2>Key Features</h2>
                    <ul class="feature-list">
                        <li class="feature">Lightning-fast parsing</li>
                        <li class="feature">Full CSS4 selector support</li>
                        <li class="feature">Functional mutations</li>
                        <li class="feature">Beautiful output generation</li>
                    </ul>
                </div>
                
                <div class="links">
                    <h2>Useful Links</h2>
                    <a href="https://github.com/perfectpizza" target="_blank">GitHub Repository</a>
                    <a href="/documentation" title="Complete Documentation">Documentation</a>
                </div>
                
                <table class="stats">
                    <thead>
                        <tr><th>Metric</th><th>Value</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>Parse Speed</td><td>10x faster</td></tr>
                        <tr><td>Memory Usage</td><td>50% less</td></tr>
                        <tr><td>Features</td><td>Complete CSS4</td></tr>
                    </tbody>
                </table>
            </div>
        </body>
    </html>
    """
    
    # Parse the HTML
    doc = parse(html)
    print(f"✅ Parsed HTML document with {len(list(doc.descendants()))} elements")
    
    # Example 2: CSS Selectors
    print("\n2. CSS Selector Examples")
    
    # Basic selectors
    title = select_one(doc, 'h1.title')
    print(f"📝 Page title: {title.text()}")
    
    features = select(doc, '.feature-list .feature')
    print(f"🎯 Found {len(features)} features:")
    for i, feature in enumerate(features, 1):
        print(f"   {i}. {feature.text()}")
    
    # Advanced selectors
    first_feature = select_one(doc, '.feature:first-child')
    print(f"🥇 First feature: {first_feature.text()}")
    
    external_links = select(doc, 'a[target="_blank"]')
    print(f"🔗 External links: {len(external_links)}")
    
    # Complex selectors
    intro_next = select(doc, '.intro + div')
    print(f"📄 Element after intro: {intro_next[0].get_attr('class') if intro_next else 'None'}")
    
    # Example 3: Functional Mutations
    print("\n3. Functional Mutations (Immutable)")
    
    # Clone and modify the title
    original_title = select_one(doc, 'h1')
    modified_title = add_class(original_title, 'highlighted')
    modified_title = set_attr(modified_title, 'data-version', '2.0')
    
    print(f"📝 Original title classes: {original_title.get_classes()}")
    print(f"✨ Modified title classes: {modified_title.get_classes()}")
    print(f"🏷️  Modified title data-version: {modified_title.get_attr('data-version')}")
    
    # Create and append new content
    new_feature = Node('li', {'class': 'feature new'})
    new_feature.add_child('Immutable operations')
    
    feature_list = select_one(doc, '.feature-list')
    updated_list = append_child(feature_list, new_feature)
    
    new_features = select(updated_list, '.feature')
    print(f"📈 Features after adding new one: {len(new_features)}")
    
    # Example 4: Data Extraction
    print("\n4. Data Extraction")
    
    # Extract all text
    page_text = extract_text(doc)
    print(f"📄 Total text length: {len(page_text)} characters")
    print(f"🔤 First 100 chars: {page_text[:100]}...")
    
    # Extract links
    links = extract_links(doc)
    print(f"🔗 Found {len(links)} links:")
    for link in links:
        print(f"   • {link['text']} → {link['url']}")
    
    # Extract table data
    tables = extract_tables(doc)
    if tables:
        print(f"📊 Found {len(tables)} table(s):")
        for i, table in enumerate(tables):
            print(f"   Table {i+1}: {len(table)} rows × {len(table[0]) if table else 0} columns")
            for row in table[:3]:  # Show first 3 rows
                print(f"     {row}")
    
    # Example 5: HTML Output
    print("\n5. HTML Output Generation")
    
    # Extract just the features section
    features_section = select_one(doc, '.features')
    
    # Generate clean HTML
    compact_html = to_html(features_section)
    print(f"📦 Compact HTML ({len(compact_html)} chars):")
    print(compact_html[:150] + "..." if len(compact_html) > 150 else compact_html)
    
    # Generate pretty HTML
    pretty = pretty_html(features_section, indent_size=2)
    print(f"\n🎨 Pretty HTML:")
    print(pretty)
    
    # Example 6: Advanced Querying
    print("\n6. Advanced Querying Examples")
    
    # Find elements by text content
    from perfectpizza.utils import find_by_text
    speed_elements = find_by_text(doc, "faster", case_sensitive=False)
    print(f"⚡ Elements mentioning 'faster': {len(speed_elements)}")
    
    # Complex selector combinations
    nested_text = select(doc, 'div.container div.features ul li')
    print(f"🎯 Deeply nested list items: {len(nested_text)}")
    
    # Meta information extraction
    from perfectpizza.utils import get_meta_info
    meta_info = get_meta_info(doc)
    print(f"📋 Meta information:")
    for key, value in meta_info.items():
        print(f"   {key}: {value}")
    
    # Example 7: Quick Parsing with pizza() helper
    print("\n7. Quick Parsing with pizza() Helper")
    
    simple_html = '<div class="box"><p>Quick test</p><p>Another paragraph</p></div>'
    
    # Parse and select in one call
    paragraphs = pizza(simple_html, 'p')
    print(f"🍕 Quick pizza parse found {len(paragraphs)} paragraphs:")
    for p in paragraphs:
        print(f"   • {p.text()}")
    
    # Example 8: Performance Demonstration
    print("\n8. Performance Test")
    
    import time
    
    # Generate a larger HTML document
    large_html_parts = ['<html><body><div class="container">']
    for i in range(1000):
        large_html_parts.append(f'''
        <article class="post" id="post-{i}" data-category="tech">
            <h2 class="post-title">Post {i} Title</h2>
            <p class="post-content">This is the content of post {i} with some <strong>bold</strong> text.</p>
            <div class="post-meta">
                <span class="author">Author {i % 10}</span>
                <span class="date">2025-01-{(i % 28) + 1:02d}</span>
            </div>
        </article>
        ''')
    large_html_parts.append('</div></body></html>')
    large_html = ''.join(large_html_parts)
    
    # Time the parsing
    start_time = time.time()
    large_doc = parse(large_html)
    parse_time = time.time() - start_time
    
    # Time CSS selection
    start_time = time.time()
    all_posts = select(large_doc, '.post')
    selection_time = time.time() - start_time
    
    # Time complex query
    start_time = time.time()
    specific_posts = select(large_doc, 'article.post[data-category="tech"] h2.post-title')
    complex_time = time.time() - start_time
    
    print(f"⚡ Performance Results:")
    print(f"   📄 Parsed 1000 articles in {parse_time:.3f}s")
    print(f"   🎯 Found {len(all_posts)} posts in {selection_time:.3f}s")
    print(f"   🔍 Complex query found {len(specific_posts)} titles in {complex_time:.3f}s")
    print(f"   📊 Total elements in document: {len(list(large_doc.descendants()))}")
    
    print(f"\n🎉 PerfectPizza demonstration complete!")
    print("💡 Try modifying this example to explore more features!")


if __name__ == "__main__":
    main()