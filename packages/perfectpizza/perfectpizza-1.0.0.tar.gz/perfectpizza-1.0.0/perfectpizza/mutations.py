# perfectpizza/mutations.py

"""
Functional mutations for PerfectPizza DOM nodes.

All mutations return new Node instances, preserving immutability.
"""

from typing import Dict, List, Union, Optional
import copy
from .dom import Node, Document

def clone_node(node: Node, deep: bool = True) -> Node:
    """
    Create a deep or shallow copy of a node.
    
    Args:
        node: Node to clone
        deep: If True, clone all descendants
        
    Returns:
        New Node instance
    """
    if isinstance(node, Document):
        new_node = Document()
    else:
        new_node = Node(node.tag, node.attrs.copy(), parent=None)
    
    if deep:
        for child in node.children:
            if isinstance(child, Node):
                cloned_child = clone_node(child, deep=True)
                new_node.add_child(cloned_child)
            else:
                new_node.add_child(child)  # Text content
                
    return new_node


def set_attr(node: Node, name: str, value: str) -> Node:
    """
    Set an attribute on a node.
    
    Returns a new node with the attribute set.
    """
    new_node = clone_node(node, deep=True)
    new_node.attrs[name.lower()] = value
    return new_node


def remove_attr(node: Node, name: str) -> Node:
    """
    Remove an attribute from a node.
    
    Returns a new node with the attribute removed.
    """
    new_node = clone_node(node, deep=True)
    new_node.attrs.pop(name.lower(), None)
    return new_node


def add_class(node: Node, class_name: str) -> Node:
    """
    Add a CSS class to a node.
    
    Returns a new node with the class added.
    """
    new_node = clone_node(node, deep=True)
    classes = new_node.get_classes()
    
    if class_name not in classes:
        classes.append(class_name)
        new_node.attrs['class'] = ' '.join(classes)
    
    return new_node


def remove_class(node: Node, class_name: str) -> Node:
    """
    Remove a CSS class from a node.
    
    Returns a new node with the class removed.
    """
    new_node = clone_node(node, deep=True)
    classes = new_node.get_classes()
    
    if class_name in classes:
        classes.remove(class_name)
        if classes:
            new_node.attrs['class'] = ' '.join(classes)
        else:
            new_node.attrs.pop('class', None)
    
    return new_node


def toggle_class(node: Node, class_name: str) -> Node:
    """
    Toggle a CSS class on a node.
    
    Returns a new node with the class toggled.
    """
    if node.has_class(class_name):
        return remove_class(node, class_name)
    else:
        return add_class(node, class_name)


def replace_text(node: Node, old_text: str, new_text: str) -> Node:
    """
    Replace text content in a node and its descendants.
    
    Returns a new node with text replaced.
    """
    new_node = clone_node(node, deep=False)
    
    for child in node.children:
        if isinstance(child, str):
            new_text_content = child.replace(old_text, new_text)
            new_node.add_child(new_text_content)
        elif isinstance(child, Node):
            new_child = replace_text(child, old_text, new_text)
            new_node.add_child(new_child)
            
    return new_node


def set_text(node: Node, text: str) -> Node:
    """
    Set the text content of a node, removing all children.
    
    Returns a new node with only text content.
    """
    new_node = Node(node.tag, node.attrs.copy(), parent=None)
    new_node.add_child(text)
    return new_node


def append_child(node: Node, child: Union[Node, str]) -> Node:
    """
    Append a child to a node.
    
    Returns a new node with the child appended.
    """
    new_node = clone_node(node, deep=True)
    
    if isinstance(child, Node):
        child_copy = clone_node(child, deep=True)
        new_node.add_child(child_copy)
    else:
        new_node.add_child(child)
        
    return new_node


def prepend_child(node: Node, child: Union[Node, str]) -> Node:
    """
    Prepend a child to a node.
    
    Returns a new node with the child prepended.
    """
    new_node = Node(node.tag, node.attrs.copy(), parent=None)
    
    # Add the new child first
    if isinstance(child, Node):
        child_copy = clone_node(child, deep=True)
        new_node.add_child(child_copy)
    else:
        new_node.add_child(child)
    
    # Then add existing children
    for existing_child in node.children:
        if isinstance(existing_child, Node):
            existing_copy = clone_node(existing_child, deep=True)
            new_node.add_child(existing_copy)
        else:
            new_node.add_child(existing_child)
            
    return new_node


def remove_child(node: Node, child_to_remove: Union[Node, str, int]) -> Node:
    """
    Remove a child from a node.
    
    Args:
        node: Parent node
        child_to_remove: Child node, text string, or index to remove
        
    Returns:
        New node with the child removed
    """
    new_node = Node(node.tag, node.attrs.copy(), parent=None)
    
    for i, child in enumerate(node.children):
        # Skip the child we want to remove
        if (isinstance(child_to_remove, int) and i == child_to_remove) or \
           (isinstance(child_to_remove, str) and child == child_to_remove) or \
           (isinstance(child_to_remove, Node) and child is child_to_remove):
            continue
            
        # Add other children
        if isinstance(child, Node):
            child_copy = clone_node(child, deep=True)
            new_node.add_child(child_copy)
        else:
            new_node.add_child(child)
            
    return new_node


def replace_child(node: Node, old_child: Union[Node, str, int], new_child: Union[Node, str]) -> Node:
    """
    Replace a child in a node.
    
    Args:
        node: Parent node
        old_child: Child to replace (node, text, or index)
        new_child: New child to insert
        
    Returns:
        New node with the child replaced
    """
    new_node = Node(node.tag, node.attrs.copy(), parent=None)
    
    for i, child in enumerate(node.children):
        # Replace the target child
        if (isinstance(old_child, int) and i == old_child) or \
           (isinstance(old_child, str) and child == old_child) or \
           (isinstance(old_child, Node) and child is old_child):
            if isinstance(new_child, Node):
                new_child_copy = clone_node(new_child, deep=True)
                new_node.add_child(new_child_copy)
            else:
                new_node.add_child(new_child)
        else:
            # Keep other children
            if isinstance(child, Node):
                child_copy = clone_node(child, deep=True)
                new_node.add_child(child_copy)
            else:
                new_node.add_child(child)
                
    return new_node


def wrap_node(node: Node, wrapper_tag: str, wrapper_attrs: Dict[str, str] = None) -> Node:
    """
    Wrap a node in another element.
    
    Args:
        node: Node to wrap
        wrapper_tag: Tag name for wrapper
        wrapper_attrs: Attributes for wrapper
        
    Returns:
        New wrapper node containing the original node
    """
    wrapper = Node(wrapper_tag, wrapper_attrs or {})
    node_copy = clone_node(node, deep=True)
    wrapper.add_child(node_copy)
    return wrapper


def unwrap_node(node: Node) -> List[Union[Node, str]]:
    """
    Unwrap a node, returning its children.
    
    Args:
        node: Node to unwrap
        
    Returns:
        List of the node's children
    """
    children = []
    for child in node.children:
        if isinstance(child, Node):
            children.append(clone_node(child, deep=True))
        else:
            children.append(child)
    return children


def filter_children(node: Node, predicate: callable) -> Node:
    """
    Filter children of a node based on a predicate function.
    
    Args:
        node: Parent node
        predicate: Function that takes a child and returns bool
        
    Returns:
        New node with filtered children
    """
    new_node = Node(node.tag, node.attrs.copy(), parent=None)
    
    for child in node.children:
        if predicate(child):
            if isinstance(child, Node):
                child_copy = clone_node(child, deep=True)
                new_node.add_child(child_copy)
            else:
                new_node.add_child(child)
                
    return new_node


def map_children(node: Node, mapper: callable) -> Node:
    """
    Transform children of a node using a mapper function.
    
    Args:
        node: Parent node
        mapper: Function that takes a child and returns transformed child
        
    Returns:
        New node with transformed children
    """
    new_node = Node(node.tag, node.attrs.copy(), parent=None)
    
    for child in node.children:
        transformed = mapper(child)
        if transformed is not None:
            if isinstance(transformed, Node):
                new_node.add_child(transformed)
            else:
                new_node.add_child(str(transformed))
                
    return new_node


def transform_tree(node: Node, transformer: callable) -> Node:
    """
    Recursively transform a node tree using a transformer function.
    
    Args:
        node: Root node to transform
        transformer: Function that takes a node and returns transformed node
        
    Returns:
        New transformed node tree
    """
    # Transform current node
    transformed = transformer(node)
    if not isinstance(transformed, Node):
        return transformed
        
    # Recursively transform children
    new_node = Node(transformed.tag, transformed.attrs.copy(), parent=None)
    
    for child in transformed.children:
        if isinstance(child, Node):
            transformed_child = transform_tree(child, transformer)
            if transformed_child is not None:
                new_node.add_child(transformed_child)
        else:
            new_node.add_child(child)
            
    return new_node