# perfectpizza/cli.py

"""
Command-line interface for PerfectPizza HTML parser.
"""

import sys
import argparse
import json
from typing import List, Dict, Any
from . import parse, select, select_one
from .utils import (
    extract_text, extract_links, extract_tables, 
    extract_images, extract_forms, to_html, pretty_html
)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='🍕 PerfectPizza - Fast HTML parsing and extraction',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Parse HTML file and extract all links
  perfectpizza parse page.html --extract links

  # Select elements with CSS selectors
  perfectpizza select "div.content p" page.html

  # Extract table data as JSON
  perfectpizza parse page.html --extract tables --format json

  # Pretty-print cleaned HTML
  perfectpizza parse page.html --output html --pretty

  # Extract text content only
  perfectpizza parse page.html --extract text
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse HTML and extract data')
    parse_parser.add_argument('file', help='HTML file to parse (use "-" for stdin)')
    parse_parser.add_argument('--extract', choices=['text', 'links', 'images', 'tables', 'forms'], 
                             help='Extract specific data type')
    parse_parser.add_argument('--format', choices=['json', 'csv', 'text'], default='text',
                             help='Output format')
    parse_parser.add_argument('--output', choices=['html', 'data'], default='data',
                             help='Output type')
    parse_parser.add_argument('--pretty', action='store_true',
                             help='Pretty-print HTML output')
    parse_parser.add_argument('--base-url', help='Base URL for resolving relative links')
    
    # Select command
    select_parser = subparsers.add_parser('select', help='Select elements with CSS selectors')
    select_parser.add_argument('selector', help='CSS selector')
    select_parser.add_argument('file', help='HTML file to parse (use "-" for stdin)')
    select_parser.add_argument('--text', action='store_true', 
                              help='Extract text content from selected elements')
    select_parser.add_argument('--attrs', nargs='*', 
                              help='Extract specific attributes from selected elements')
    select_parser.add_argument('--format', choices=['json', 'text'], default='text',
                              help='Output format')
    select_parser.add_argument('--first', action='store_true',
                              help='Select only the first matching element')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show document information')
    info_parser.add_argument('file', help='HTML file to analyze')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'parse':
            handle_parse_command(args)
        elif args.command == 'select':
            handle_select_command(args)
        elif args.command == 'info':
            handle_info_command(args)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

def read_input(file_path: str) -> str:
    """Read HTML content from file or stdin."""
    if file_path == '-':
        return sys.stdin.read()
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

def handle_parse_command(args):
    """Handle the parse command."""
    html = read_input(args.file)
    doc = parse(html)
    
    if args.output == 'html':
        # Output HTML
        if args.pretty:
            print(pretty_html(doc))
        else:
            print(to_html(doc))
        return
    
    # Extract data
    if args.extract == 'text':
        result = extract_text(doc)
        print(result)
    
    elif args.extract == 'links':
        links = extract_links(doc, base_url=args.base_url)
        output_data(links, args.format)
    
    elif args.extract == 'images':
        images = extract_images(doc, base_url=args.base_url)
        output_data(images, args.format)
    
    elif args.extract == 'tables':
        tables = extract_tables(doc)
        if args.format == 'json':
            print(json.dumps(tables, indent=2))
        elif args.format == 'csv':
            import csv
            import io
            for i, table in enumerate(tables):
                if len(tables) > 1:
                    print(f"# Table {i+1}")
                output = io.StringIO()
                writer = csv.writer(output)
                for row in table:
                    writer.writerow(row)
                print(output.getvalue().strip())
        else:
            for i, table in enumerate(tables):
                if len(tables) > 1:
                    print(f"Table {i+1}:")
                for row in table:
                    print("\t".join(row))
                print()
    
    elif args.extract == 'forms':
        forms = extract_forms(doc)
        output_data(forms, args.format)
    
    else:
        # Default: show document structure
        print(f"📄 Document parsed successfully!")
        print(f"   Elements: {len(list(doc.descendants()))}")
        print(f"   Title: {doc.title() or 'No title'}")
        
        # Show some basic stats
        elements = list(doc.descendants())
        tag_counts = {}
        for elem in elements:
            tag_counts[elem.tag] = tag_counts.get(elem.tag, 0) + 1
        
        print(f"   Most common tags:")
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"     {tag}: {count}")

def handle_select_command(args):
    """Handle the select command."""
    html = read_input(args.file)
    doc = parse(html)
    
    # Select elements
    if args.first:
        elements = [select_one(doc, args.selector)]
        elements = [e for e in elements if e is not None]
    else:
        elements = select(doc, args.selector)
    
    if not elements:
        print("No elements found matching selector", file=sys.stderr)
        return
    
    # Extract data from selected elements
    results = []
    for elem in elements:
        if args.text:
            results.append(elem.text())
        elif args.attrs:
            result = {}
            for attr in args.attrs:
                result[attr] = elem.get_attr(attr, '')
            results.append(result)
        else:
            # Default: show element info
            result = {
                'tag': elem.tag,
                'text': elem.text()[:100] + ('...' if len(elem.text()) > 100 else ''),
                'attrs': dict(elem.attrs)
            }
            results.append(result)
    
    output_data(results, args.format)

def handle_info_command(args):
    """Handle the info command."""
    html = read_input(args.file)
    doc = parse(html)
    
    print("🍕 PerfectPizza Document Analysis")
    print("=" * 40)
    
    # Basic info
    print(f"Title: {doc.title() or 'No title'}")
    print(f"Total elements: {len(list(doc.descendants()))}")
    
    # Meta information
    from .utils import get_meta_info
    meta = get_meta_info(doc)
    if meta:
        print(f"\nMeta information:")
        for key, value in meta.items():
            print(f"  {key}: {value}")
    
    # Element counts
    elements = list(doc.descendants())
    tag_counts = {}
    for elem in elements:
        tag_counts[elem.tag] = tag_counts.get(elem.tag, 0) + 1
    
    print(f"\nElement counts:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {tag}: {count}")
    
    # Links and images
    links = extract_links(doc)
    images = extract_images(doc)
    tables = extract_tables(doc)
    
    print(f"\nContent summary:")
    print(f"  Links: {len(links)}")
    print(f"  Images: {len(images)}")
    print(f"  Tables: {len(tables)}")
    
    # Text stats
    text = extract_text(doc)
    word_count = len(text.split())
    char_count = len(text)
    
    print(f"  Text: {word_count} words, {char_count} characters")

def output_data(data: Any, format_type: str):
    """Output data in specified format."""
    if format_type == 'json':
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif format_type == 'csv':
        import csv
        import io
        if isinstance(data, list) and data and isinstance(data[0], dict):
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            print(output.getvalue().strip())
        else:
            print("CSV format not supported for this data type", file=sys.stderr)
    else:  # text format
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        print(f"{key}: {value}")
                    print()
                else:
                    print(item)
        else:
            print(data)

if __name__ == '__main__':
    main()