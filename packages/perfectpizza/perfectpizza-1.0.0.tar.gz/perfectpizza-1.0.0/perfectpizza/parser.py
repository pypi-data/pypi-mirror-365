# perfectpizza/parser.py

import re
from html.parser import HTMLParser
from typing import Optional, List, Dict, Set
from .dom import Node, Document

# Self-closing tags that don't need end tags
VOID_ELEMENTS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
}

# Tags that can auto-close when certain tags are encountered
AUTO_CLOSE_RULES = {
    'p': {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'pre'},
    'li': {'li'},
    'dt': {'dt', 'dd'},
    'dd': {'dt', 'dd'},
    'tr': {'tr'},
    'td': {'td', 'th', 'tr'},
    'th': {'td', 'th', 'tr'},
    'thead': {'tbody', 'tfoot'},
    'tbody': {'thead', 'tfoot'},
    'tfoot': {'thead', 'tbody'},
}

class PizzaHTMLParser(HTMLParser):
    """
    Robust HTML parser that builds a DOM tree.
    
    Features:
    - Handles malformed HTML gracefully
    - Auto-closes tags when appropriate
    - Preserves whitespace intelligently
    - Supports all HTML5 features
    """
    
    def __init__(self, strict: bool = False):
        super().__init__()
        self.strict = strict
        self.reset_parser()
        
    def reset_parser(self):
        """Reset the parser state."""
        self.root = Document()
        self.stack = [self.root]
        self.open_tags: List[str] = []
        
    def handle_starttag(self, tag: str, attrs: List[tuple]):
        """Handle opening tags."""
        tag = tag.lower()
        attrs_dict = {k.lower(): v for k, v in attrs}
        
        # Auto-close tags if needed
        self._auto_close_tags(tag)
        
        # Create new node
        node = Node(tag, attrs_dict, parent=self.stack[-1])
        self.stack[-1].add_child(node)
        
        # Don't push void elements onto the stack
        if tag not in VOID_ELEMENTS:
            self.stack.append(node)
            self.open_tags.append(tag)
            
    def handle_endtag(self, tag: str):
        """Handle closing tags."""
        tag = tag.lower()
        
        # If it's a void element, ignore the end tag
        if tag in VOID_ELEMENTS:
            return
            
        # Find the matching opening tag
        try:
            # Look for the tag in reverse order (most recent first)
            for i in range(len(self.open_tags) - 1, -1, -1):
                if self.open_tags[i] == tag:
                    # Close all tags from this point forward
                    tags_to_close = len(self.open_tags) - i
                    for _ in range(tags_to_close):
                        if len(self.stack) > 1:
                            self.stack.pop()
                        if self.open_tags:
                            self.open_tags.pop()
                    break
        except (IndexError, ValueError):
            # Malformed HTML - ignore unmatched closing tag
            if not self.strict:
                pass
            else:
                raise ValueError(f"Unmatched closing tag: {tag}")
                
    def handle_data(self, data: str):
        """Handle text content."""
        # Preserve significant whitespace but clean up excessive whitespace
        if data.strip():  # Has non-whitespace content
            # Normalize internal whitespace but preserve intentional spacing
            cleaned = re.sub(r'\s+', ' ', data)
            self.stack[-1].add_child(cleaned)
        elif self._should_preserve_whitespace():
            # In pre, code, textarea tags, preserve all whitespace
            self.stack[-1].add_child(data)
        else:
            # Add single space for significant whitespace between elements
            if data and any(c.isspace() for c in data):
                self.stack[-1].add_child(' ')
                
    def handle_comment(self, data: str):
        """Handle HTML comments."""
        # Store comments as special nodes if needed
        comment_node = Node('!--', {'comment': data}, parent=self.stack[-1])
        self.stack[-1].add_child(comment_node)
        
    def handle_decl(self, decl: str):
        """Handle DOCTYPE declarations."""
        doctype_node = Node('!doctype', {'content': decl}, parent=self.stack[-1])
        self.stack[-1].add_child(doctype_node)
        
    def _auto_close_tags(self, new_tag: str):
        """Auto-close tags based on HTML rules."""
        if not self.open_tags:
            return
            
        current_tag = self.open_tags[-1] if self.open_tags else None
        
        if current_tag in AUTO_CLOSE_RULES:
            if new_tag in AUTO_CLOSE_RULES[current_tag]:
                # Auto-close the current tag
                if len(self.stack) > 1:
                    self.stack.pop()
                if self.open_tags:
                    self.open_tags.pop()
                    
    def _should_preserve_whitespace(self) -> bool:
        """Check if we're inside a tag that preserves whitespace."""
        preserve_tags = {'pre', 'code', 'textarea', 'script', 'style'}
        return any(tag in preserve_tags for tag in self.open_tags)
        
    def error(self, message: str):
        """Handle parser errors."""
        if self.strict:
            raise ValueError(f"HTML Parse Error: {message}")
        # In non-strict mode, just continue parsing


def parse(html: str, strict: bool = False) -> Document:
    """
    Parse HTML string into a Document tree.
    
    Args:
        html: HTML string to parse
        strict: If True, raise errors on malformed HTML
        
    Returns:
        Document root node containing the parsed tree
    """
    if not html or not html.strip():
        return Document()
        
    parser = PizzaHTMLParser(strict=strict)
    
    try:
        parser.feed(html)
        parser.close()
    except Exception as e:
        if strict:
            raise
        # In non-strict mode, return what we parsed so far
        pass
        
    return parser.root


def parse_fragment(html: str, strict: bool = False) -> List[Node]:
    """
    Parse an HTML fragment (content without html/body wrapper).
    
    Returns a list of root nodes instead of a Document.
    """
    doc = parse(html, strict=strict)
    
    # If we have html > body structure, return body children
    html_node = doc.find_one('html')
    if html_node:
        body_node = html_node.find_one('body')
        if body_node:
            return [child for child in body_node.children if isinstance(child, Node)]
    
    # Otherwise return direct children of document
    return [child for child in doc.children if isinstance(child, Node)]


# Functional query helpers
def find_all(node: Node, tag: str) -> List[Node]:
    """Find all descendant nodes with the specified tag."""
    return node.find_all(tag)


def find_one(node: Node, tag: str) -> Optional[Node]:
    """Find the first descendant node with the specified tag."""
    return node.find_one(tag)


def find_by_class(node: Node, class_name: str) -> List[Node]:
    """Find all descendant nodes with the specified CSS class."""
    return node.find_by_class(class_name)


def find_by_id(node: Node, id_value: str) -> Optional[Node]:
    """Find the first descendant node with the specified ID."""
    return node.find_by_id(id_value)


def find_by_attrs(node: Node, **attrs) -> List[Node]:
    """Find all descendant nodes matching the specified attributes."""
    result = []
    for descendant in node.descendants():
        if all(descendant.get_attr(k) == v for k, v in attrs.items()):
            result.append(descendant)
    return result