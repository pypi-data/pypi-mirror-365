# perfectpizza/utils.py

"""
Utility functions for PerfectPizza DOM manipulation and extraction.
"""

import re
from typing import List, Dict, Optional, Any, Generator
from urllib.parse import urljoin, urlparse
from .dom import Node, Document

# Self-closing tags that should be rendered as <tag />
VOID_ELEMENTS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
}

def to_html(node: Node, pretty: bool = False, indent_size: int = 2) -> str:
    """
    Convert a node tree back to HTML string.
    
    Args:
        node: Root node to convert
        pretty: If True, format with indentation
        indent_size: Number of spaces per indent level
        
    Returns:
        HTML string representation
    """
    if isinstance(node, Document):
        # For documents, render all children
        if pretty:
            parts = []
            for child in node.children:
                if isinstance(child, Node):
                    parts.append(to_html(child, pretty=True, indent_size=indent_size))
                else:
                    stripped = child.strip()
                    if stripped:
                        parts.append(stripped)
            return '\n'.join(parts)
        else:
            return ''.join(to_html(child) if isinstance(child, Node) else child 
                          for child in node.children)
    
    return _render_node(node, 0 if pretty else -1, indent_size)


def _render_node(node: Node, indent_level: int, indent_size: int) -> str:
    """Render a single node to HTML."""
    if node.tag.startswith('!'):
        # Handle comments and doctype
        if node.tag == '!--':
            return f"<!--{node.get_attr('comment', '')}-->"
        elif node.tag == '!doctype':
            return f"<!DOCTYPE {node.get_attr('content', 'html')}>"
        return ''
    
    # Build opening tag
    tag_parts = [node.tag]
    if node.attrs:
        for name, value in node.attrs.items():
            if value is None or value == '':
                tag_parts.append(name)
            else:
                escaped_value = _escape_attribute(value)
                tag_parts.append(f'{name}="{escaped_value}"')
    
    opening_tag = f"<{' '.join(tag_parts)}>"
    
    # Handle void elements
    if node.tag in VOID_ELEMENTS:
        if indent_level >= 0:
            return ' ' * (indent_level * indent_size) + opening_tag
        return opening_tag
    
    # Handle elements with content
    closing_tag = f"</{node.tag}>"
    
    if not node.children:
        # Empty element
        if indent_level >= 0:
            return ' ' * (indent_level * indent_size) + opening_tag + closing_tag
        return opening_tag + closing_tag
    
    # Element with children
    if indent_level >= 0:
        # Pretty printing
        result = [' ' * (indent_level * indent_size) + opening_tag]
        
        for child in node.children:
            if isinstance(child, Node):
                result.append(_render_node(child, indent_level + 1, indent_size))
            else:
                stripped = child.strip()
                if stripped:
                    result.append(' ' * ((indent_level + 1) * indent_size) + _escape_text(stripped))
        
        result.append(' ' * (indent_level * indent_size) + closing_tag)
        return '\n'.join(result)
    else:
        # Compact printing
        content_parts = []
        for child in node.children:
            if isinstance(child, Node):
                content_parts.append(_render_node(child, -1, indent_size))
            else:
                content_parts.append(_escape_text(child))
        
        return opening_tag + ''.join(content_parts) + closing_tag


def pretty_html(node: Node, indent_size: int = 2) -> str:
    """
    Convert node to pretty-printed HTML.
    
    Args:
        node: Node to convert
        indent_size: Spaces per indent level
        
    Returns:
        Pretty-formatted HTML string
    """
    return to_html(node, pretty=True, indent_size=indent_size)


def _escape_text(text: str) -> str:
    """Escape text content for HTML."""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))


def _escape_attribute(value: str) -> str:
    """Escape attribute value for HTML."""
    return (str(value).replace('&', '&amp;')
                     .replace('<', '&lt;')
                     .replace('>', '&gt;')
                     .replace('"', '&quot;')
                     .replace("'", '&#x27;'))


def extract_text(node: Node, separator: str = ' ', clean: bool = True) -> str:
    """
    Extract all text content from a node tree.
    
    Args:
        node: Root node
        separator: String to join text segments
        clean: If True, normalize whitespace
        
    Returns:
        Extracted text content
    """
    text = node.text(deep=True, separator=separator)
    
    if clean:
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def extract_links(node: Node, base_url: str = None) -> List[Dict[str, str]]:
    """
    Extract all links from a node tree.
    
    Args:
        node: Root node to search
        base_url: Base URL for resolving relative links
        
    Returns:
        List of dictionaries with link information
    """
    links = []
    
    # Find all <a> tags with href
    for link_node in node.find_all('a'):
        href = link_node.get_attr('href')
        if href:
            url = urljoin(base_url, href) if base_url else href
            links.append({
                'url': url,
                'text': extract_text(link_node).strip(),
                'title': link_node.get_attr('title', ''),
                'target': link_node.get_attr('target', '')
            })
    
    return links


def extract_images(node: Node, base_url: str = None) -> List[Dict[str, str]]:
    """
    Extract all images from a node tree.
    
    Args:
        node: Root node to search
        base_url: Base URL for resolving relative URLs
        
    Returns:
        List of dictionaries with image information
    """
    images = []
    
    for img_node in node.find_all('img'):
        src = img_node.get_attr('src')
        if src:
            url = urljoin(base_url, src) if base_url else src
            images.append({
                'url': url,
                'alt': img_node.get_attr('alt', ''),
                'title': img_node.get_attr('title', ''),
                'width': img_node.get_attr('width', ''),
                'height': img_node.get_attr('height', '')
            })
    
    return images


def extract_forms(node: Node) -> List[Dict[str, Any]]:
    """
    Extract form information from a node tree.
    
    Args:
        node: Root node to search
        
    Returns:
        List of dictionaries with form information
    """
    forms = []
    
    for form_node in node.find_all('form'):
        form_data = {
            'action': form_node.get_attr('action', ''),
            'method': form_node.get_attr('method', 'get').lower(),
            'enctype': form_node.get_attr('enctype', 'application/x-www-form-urlencoded'),
            'fields': []
        }
        
        # Extract form fields
        for field in form_node.find_all('input') + form_node.find_all('textarea') + form_node.find_all('select'):
            field_info = {
                'type': field.get_attr('type', 'text'),
                'name': field.get_attr('name', ''),
                'value': field.get_attr('value', ''),
                'required': field.has_attr('required'),
                'placeholder': field.get_attr('placeholder', '')
            }
            
            if field.tag == 'select':
                field_info['options'] = []
                for option in field.find_all('option'):
                    field_info['options'].append({
                        'value': option.get_attr('value', ''),
                        'text': extract_text(option).strip(),
                        'selected': option.has_attr('selected')
                    })
            
            form_data['fields'].append(field_info)
        
        forms.append(form_data)
    
    return forms


def extract_tables(node: Node) -> List[List[List[str]]]:
    """
    Extract table data as lists of rows and cells.
    
    Args:
        node: Root node to search
        
    Returns:
        List of tables, each table is a list of rows, each row is a list of cells
    """
    tables = []
    
    for table_node in node.find_all('table'):
        table_data = []
        
        # Process all rows (in thead, tbody, tfoot, or direct children)
        for row_node in table_node.find_all('tr'):
            row_data = []
            
            # Process all cells (th or td)
            for cell_node in row_node.find_all('th') + row_node.find_all('td'):
                cell_text = extract_text(cell_node).strip()
                row_data.append(cell_text)
            
            if row_data:  # Only add non-empty rows
                table_data.append(row_data)
        
        if table_data:  # Only add non-empty tables
            tables.append(table_data)
    
    return tables


def get_meta_info(node: Node) -> Dict[str, str]:
    """
    Extract meta information from the document.
    
    Args:
        node: Document or node to search
        
    Returns:
        Dictionary of meta information
    """
    meta_info = {}
    
    # Extract title
    title_node = node.find_one('title')
    if title_node:
        meta_info['title'] = extract_text(title_node).strip()
    
    # Extract meta tags
    for meta_node in node.find_all('meta'):
        name = meta_node.get_attr('name') or meta_node.get_attr('property')
        content = meta_node.get_attr('content')
        
        if name and content:
            meta_info[name] = content
    
    return meta_info


def find_by_text(node: Node, text: str, exact: bool = False, case_sensitive: bool = False) -> List[Node]:
    """
    Find nodes containing specific text.
    
    Args:
        node: Root node to search
        text: Text to search for
        exact: If True, match exact text content
        case_sensitive: If True, case-sensitive matching
        
    Returns:
        List of nodes containing the text
    """
    if not case_sensitive:
        text = text.lower()
    
    results = []
    
    def check_node(n):
        node_text = extract_text(n)
        if not case_sensitive:
            node_text = node_text.lower()
        
        if exact:
            if node_text.strip() == text.strip():
                results.append(n)
        else:
            if text in node_text:
                results.append(n)
    
    # Check the root node
    check_node(node)
    
    # Check all descendants
    for descendant in node.descendants():
        check_node(descendant)
    
    return results


def get_path(node: Node) -> str:
    """
    Get the CSS selector path to a node.
    
    Args:
        node: Node to get path for
        
    Returns:
        CSS selector string that uniquely identifies the node
    """
    if not node.parent or node.parent.tag == 'document':
        return node.tag
    
    path_parts = []
    current = node
    
    while current and current.parent and current.parent.tag != 'document':
        # Build selector for current node
        selector = current.tag
        
        # Add ID if present
        node_id = current.get_attr('id')
        if node_id:
            selector += f'#{node_id}'
        else:
            # Add classes if present
            classes = current.get_classes()
            if classes:
                selector += '.' + '.'.join(classes)
            
            # Add nth-child if no unique identifier
            if not classes:
                siblings = [child for child in current.parent.children 
                          if isinstance(child, Node) and child.tag == current.tag]
                if len(siblings) > 1:
                    try:
                        index = siblings.index(current) + 1
                        selector += f':nth-child({index})'
                    except ValueError:
                        pass
        
        path_parts.insert(0, selector)
        current = current.parent
    
    return ' > '.join(path_parts)