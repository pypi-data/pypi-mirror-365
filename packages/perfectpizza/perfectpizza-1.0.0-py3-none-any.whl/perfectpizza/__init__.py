# perfectpizza/__init__.py

"""
🍕 PerfectPizza - A blazing-fast, functional HTML parser for Python

PerfectPizza is a modern alternative to BeautifulSoup, designed for performance,
functional purity, and clean DOM traversal. Built with extensibility in mind.
"""

from .parser import parse, PizzaHTMLParser
from .dom import Node, Document
from .selectors import select, select_one, find_all, find_one
from .mutations import (
    set_attr, remove_attr, add_class, remove_class, 
    replace_text, append_child, remove_child, clone_node
)
from .utils import to_html, pretty_html, extract_text, extract_links

__version__ = "1.0.0"
__author__ = "Harry Graham"
__description__ = "A blazing-fast, functional HTML parser"

# Main API exports
__all__ = [
    # Core parsing
    'parse', 'PizzaHTMLParser',
    
    # DOM classes
    'Node', 'Document',
    
    # Selection and querying
    'select', 'select_one', 'find_all', 'find_one',
    
    # Mutations (functional)
    'set_attr', 'remove_attr', 'add_class', 'remove_class',
    'replace_text', 'append_child', 'remove_child', 'clone_node',
    
    # Utilities
    'to_html', 'pretty_html', 'extract_text', 'extract_links'
]

# Convenience function for quick parsing and selection
def pizza(html: str, selector: str = None):
    """
    Quick parse and select function.
    
    Args:
        html: HTML string to parse
        selector: Optional CSS selector to apply immediately
        
    Returns:
        Document if no selector, list of Nodes if selector provided
    """
    doc = parse(html)
    if selector:
        return select(doc, selector)
    return doc