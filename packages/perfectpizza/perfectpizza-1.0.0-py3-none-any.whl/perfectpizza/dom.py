# perfectpizza/dom.py

from typing import Optional, List, Dict, Union, Iterator, Any
import re
from html import escape, unescape

class Node:
    """
    Represents an HTML element node in the DOM tree.
    
    Immutable by design - all mutations return new Node instances.
    """
    
    def __init__(self, tag: str, attrs: Dict[str, str] = None, parent: Optional['Node'] = None):
        self.tag = tag.lower()
        self.attrs = attrs or {}
        self.parent = parent
        self.children: List[Union['Node', str]] = []
        self._text_cache = None
        
    def add_child(self, child: Union['Node', str]):
        """Add a child node or text content."""
        if isinstance(child, Node):
            child.parent = self
        self.children.append(child)
        self._text_cache = None  # Invalidate cache
        
    def get_attr(self, name: str, default: str = None) -> str:
        """Get an attribute value."""
        return self.attrs.get(name.lower(), default)
        
    def has_attr(self, name: str) -> bool:
        """Check if an attribute exists."""
        return name.lower() in self.attrs
        
    def has_class(self, class_name: str) -> bool:
        """Check if node has a specific CSS class."""
        classes = self.get_attr('class', '').split()
        return class_name in classes
        
    def get_classes(self) -> List[str]:
        """Get all CSS classes as a list."""
        return self.get_attr('class', '').split()
        
    def text(self, deep: bool = True, separator: str = '') -> str:
        """
        Extract text content from this node.
        
        Args:
            deep: If True, extract text from all descendants
            separator: String to join text segments
        """
        if not deep and self._text_cache is not None:
            return self._text_cache
            
        text_parts = []
        for child in self.children:
            if isinstance(child, str):
                text_parts.append(child.strip())
            elif isinstance(child, Node) and deep:
                child_text = child.text(deep=True, separator=separator)
                if child_text:
                    text_parts.append(child_text)
                    
        result = separator.join(text_parts)
        
        if not deep:
            self._text_cache = result
            
        return result
        
    def inner_text(self) -> str:
        """Get the inner text content (no descendants)."""
        return self.text(deep=False)
        
    def find_all(self, tag: str) -> List['Node']:
        """Find all descendant nodes with the specified tag."""
        result = []
        if self.tag == tag.lower():
            result.append(self)
        for child in self.children:
            if isinstance(child, Node):
                result.extend(child.find_all(tag))
        return result
        
    def find_one(self, tag: str) -> Optional['Node']:
        """Find the first descendant node with the specified tag."""
        if self.tag == tag.lower():
            return self
        for child in self.children:
            if isinstance(child, Node):
                found = child.find_one(tag)
                if found:
                    return found
        return None
        
    def find_by_class(self, class_name: str) -> List['Node']:
        """Find all descendant nodes with the specified CSS class."""
        result = []
        if self.has_class(class_name):
            result.append(self)
        for child in self.children:
            if isinstance(child, Node):
                result.extend(child.find_by_class(class_name))
        return result
        
    def find_by_id(self, id_value: str) -> Optional['Node']:
        """Find the first descendant node with the specified ID."""
        if self.get_attr('id') == id_value:
            return self
        for child in self.children:
            if isinstance(child, Node):
                found = child.find_by_id(id_value)
                if found:
                    return found
        return None
        
    def descendants(self) -> Iterator['Node']:
        """Iterate over all descendant nodes."""
        for child in self.children:
            if isinstance(child, Node):
                yield child
                yield from child.descendants()
                
    def ancestors(self) -> Iterator['Node']:
        """Iterate over all ancestor nodes."""
        current = self.parent
        while current:
            yield current
            current = current.parent
            
    def siblings(self) -> List['Node']:
        """Get all sibling nodes."""
        if not self.parent:
            return []
        return [child for child in self.parent.children 
                if isinstance(child, Node) and child is not self]
                
    def next_sibling(self) -> Optional['Node']:
        """Get the next sibling node."""
        if not self.parent:
            return None
        siblings = [child for child in self.parent.children if isinstance(child, Node)]
        try:
            index = siblings.index(self)
            return siblings[index + 1] if index + 1 < len(siblings) else None
        except (ValueError, IndexError):
            return None
            
    def prev_sibling(self) -> Optional['Node']:
        """Get the previous sibling node."""
        if not self.parent:
            return None
        siblings = [child for child in self.parent.children if isinstance(child, Node)]
        try:
            index = siblings.index(self)
            return siblings[index - 1] if index > 0 else None
        except (ValueError, IndexError):
            return None
            
    def matches(self, **criteria) -> bool:
        """
        Check if this node matches the given criteria.
        
        Args:
            tag: Tag name to match
            class_: CSS class to match (note underscore)
            id: ID attribute to match
            attrs: Dictionary of attributes to match
            **kwargs: Additional attribute matches
        """
        # Check tag
        if 'tag' in criteria and self.tag != criteria['tag'].lower():
            return False
            
        # Check class (using underscore to avoid Python keyword)
        if 'class_' in criteria and not self.has_class(criteria['class_']):
            return False
            
        # Check ID
        if 'id' in criteria and self.get_attr('id') != criteria['id']:
            return False
            
        # Check attributes dictionary
        if 'attrs' in criteria:
            for attr, value in criteria['attrs'].items():
                if self.get_attr(attr) != value:
                    return False
                    
        # Check individual attribute kwargs
        for attr, value in criteria.items():
            if attr in ('tag', 'class_', 'id', 'attrs'):
                continue
            if self.get_attr(attr) != value:
                return False
                
        return True
        
    def is_empty(self) -> bool:
        """Check if the node has no content (no children or only whitespace)."""
        return not self.children or all(
            isinstance(child, str) and not child.strip() 
            for child in self.children
        )
        
    def depth(self) -> int:
        """Get the depth of this node in the tree."""
        depth = 0
        current = self.parent
        while current:
            depth += 1
            current = current.parent
        return depth
        
    def __repr__(self):
        attrs_str = ' '.join(f'{k}="{v}"' for k, v in self.attrs.items())
        attrs_part = f' {attrs_str}' if attrs_str else ''
        return f"<{self.tag}{attrs_part}>"
        
    def __str__(self):
        return self.__repr__()
        
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return (self.tag == other.tag and 
                self.attrs == other.attrs and 
                self.children == other.children)
                
    def __hash__(self):
        return hash((self.tag, tuple(sorted(self.attrs.items()))))


class Document(Node):
    """
    Special node type representing the root document.
    Provides additional document-level methods.
    """
    
    def __init__(self):
        super().__init__("document", {})
        self._title_cache = None
        
    def title(self) -> str:
        """Get the document title."""
        if self._title_cache is not None:
            return self._title_cache
            
        title_node = self.find_one('title')
        self._title_cache = title_node.text() if title_node else ''
        return self._title_cache
        
    def head(self) -> Optional[Node]:
        """Get the head element."""
        return self.find_one('head')
        
    def body(self) -> Optional[Node]:
        """Get the body element."""
        return self.find_one('body')
        
    def html(self) -> Optional[Node]:
        """Get the html root element."""
        return self.find_one('html')
        
    def meta_tags(self) -> List[Node]:
        """Get all meta tags."""
        return self.find_all('meta')
        
    def get_meta(self, name: str) -> Optional[str]:
        """Get content of a specific meta tag by name."""
        for meta in self.meta_tags():
            if meta.get_attr('name') == name:
                return meta.get_attr('content')
        return None
        
    def links(self) -> List[Node]:
        """Get all link elements."""
        return self.find_all('link')
        
    def scripts(self) -> List[Node]:
        """Get all script elements."""
        return self.find_all('script')
        
    def images(self) -> List[Node]:
        """Get all img elements."""
        return self.find_all('img')
        
    def forms(self) -> List[Node]:
        """Get all form elements."""
        return self.find_all('form')
        
    def tables(self) -> List[Node]:
        """Get all table elements."""
        return self.find_all('table')
        
    def __repr__(self):
        return "<Document>"