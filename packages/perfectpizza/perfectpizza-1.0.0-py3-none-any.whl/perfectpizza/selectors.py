# perfectpizza/selectors.py

import re
from typing import List, Optional, Callable, Dict, Any
from .dom import Node

class CSSSelector:
    """
    CSS selector parser and matcher.
    
    Supports:
    - Tag selectors: div, p, h1
    - Class selectors: .class, .class1.class2
    - ID selectors: #id
    - Attribute selectors: [attr], [attr=value], [attr~=value], [attr*=value]
    - Pseudo-selectors: :first-child, :last-child, :nth-child(n)
    - Combinators: descendant, >, +, ~
    - Complex selectors: div.class#id[attr=value]:first-child
    """
    
    def __init__(self, selector: str):
        self.selector = selector.strip()
        self.tokens = self._tokenize(selector)
        
    def _tokenize(self, selector: str) -> List[Dict[str, Any]]:
        """Parse CSS selector into tokens."""
        # Split by combinators while preserving them
        parts = re.split(r'(\s*[>+~]\s*|\s+)', selector)
        tokens = []
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            if part in ['>', '+', '~']:
                tokens.append({'type': 'combinator', 'value': part})
            elif re.match(r'^\s+$', part):
                tokens.append({'type': 'combinator', 'value': ' '})
            else:
                tokens.append(self._parse_simple_selector(part))
                
        return tokens
        
    def _parse_simple_selector(self, selector: str) -> Dict[str, Any]:
        """Parse a simple selector (no combinators)."""
        token = {
            'type': 'selector',
            'tag': '*',
            'id': None,
            'classes': [],
            'attrs': [],
            'pseudo': []
        }
        
        # Extract tag name (everything before first . # [ :)
        tag_match = re.match(r'^([a-zA-Z0-9\-_*]+)', selector)
        if tag_match:
            token['tag'] = tag_match.group(1).lower()
            selector = selector[len(tag_match.group(1)):]
            
        # Extract ID
        id_match = re.search(r'#([a-zA-Z0-9\-_]+)', selector)
        if id_match:
            token['id'] = id_match.group(1)
            
        # Extract classes
        class_matches = re.findall(r'\.([a-zA-Z0-9\-_]+)', selector)
        token['classes'] = class_matches
        
        # Extract attributes
        attr_matches = re.findall(r'\[([^\]]+)\]', selector)
        for attr_str in attr_matches:
            token['attrs'].append(self._parse_attribute(attr_str))
            
        # Extract pseudo-selectors
        pseudo_matches = re.findall(r':([a-zA-Z0-9\-_]+)(?:\(([^)]+)\))?', selector)
        for pseudo_name, pseudo_value in pseudo_matches:
            token['pseudo'].append({'name': pseudo_name, 'value': pseudo_value})
            
        return token
        
    def _parse_attribute(self, attr_str: str) -> Dict[str, str]:
        """Parse attribute selector."""
        # [attr=value], [attr~=value], [attr*=value], etc.
        if '=' in attr_str:
            operators = ['~=', '*=', '^=', '$=', '|=', '=']
            for op in operators:
                if op in attr_str:
                    name, value = attr_str.split(op, 1)
                    value = value.strip('\'"')
                    return {'name': name.strip(), 'operator': op, 'value': value}
        
        # Just [attr]
        return {'name': attr_str.strip(), 'operator': 'exists', 'value': None}
        
    def matches(self, node: Node) -> bool:
        """Check if a node matches this selector."""
        return self._matches_tokens(node, self.tokens)
        
    def _matches_tokens(self, node: Node, tokens: List[Dict]) -> bool:
        """Check if node matches a sequence of tokens."""
        if not tokens:
            return True
            
        # Find the last selector token
        last_selector_idx = -1
        for i in range(len(tokens) - 1, -1, -1):
            if tokens[i]['type'] == 'selector':
                last_selector_idx = i
                break
                
        if last_selector_idx == -1:
            return True
            
        # Check if current node matches the last selector
        if not self._matches_simple_selector(node, tokens[last_selector_idx]):
            return False
            
        # If this is the only token, we're done
        if last_selector_idx == 0:
            return True
            
        # Check the combinator before this selector
        if last_selector_idx > 0:
            combinator = tokens[last_selector_idx - 1]
            remaining_tokens = tokens[:last_selector_idx - 1]
            
            if combinator['type'] == 'combinator':
                return self._matches_combinator(node, combinator['value'], remaining_tokens)
                
        return True
        
    def _matches_combinator(self, node: Node, combinator: str, remaining_tokens: List[Dict]) -> bool:
        """Check if the combinator relationship is satisfied."""
        if combinator == ' ':  # Descendant
            for ancestor in node.ancestors():
                if self._matches_tokens(ancestor, remaining_tokens):
                    return True
        elif combinator == '>':  # Direct child
            if node.parent:
                return self._matches_tokens(node.parent, remaining_tokens)
        elif combinator == '+':  # Adjacent sibling
            prev_sibling = node.prev_sibling()
            if prev_sibling:
                return self._matches_tokens(prev_sibling, remaining_tokens)
        elif combinator == '~':  # General sibling
            current = node.prev_sibling()
            while current:
                if self._matches_tokens(current, remaining_tokens):
                    return True
                current = current.prev_sibling()
                
        return False
        
    def _matches_simple_selector(self, node: Node, token: Dict) -> bool:
        """Check if node matches a simple selector token."""
        # Check tag
        if token['tag'] != '*' and node.tag != token['tag']:
            return False
            
        # Check ID
        if token['id'] and node.get_attr('id') != token['id']:
            return False
            
        # Check classes
        for class_name in token['classes']:
            if not node.has_class(class_name):
                return False
                
        # Check attributes
        for attr in token['attrs']:
            if not self._matches_attribute(node, attr):
                return False
                
        # Check pseudo-selectors
        for pseudo in token['pseudo']:
            if not self._matches_pseudo(node, pseudo):
                return False
                
        return True
        
    def _matches_attribute(self, node: Node, attr: Dict) -> bool:
        """Check if node matches an attribute selector."""
        name = attr['name']
        operator = attr['operator']
        expected_value = attr['value']
        
        if operator == 'exists':
            return node.has_attr(name)
            
        actual_value = node.get_attr(name)
        if actual_value is None:
            return False
            
        if operator == '=':
            return actual_value == expected_value
        elif operator == '~=':  # Word match
            return expected_value in actual_value.split()
        elif operator == '*=':  # Contains
            return expected_value in actual_value
        elif operator == '^=':  # Starts with
            return actual_value.startswith(expected_value)
        elif operator == '$=':  # Ends with
            return actual_value.endswith(expected_value)
        elif operator == '|=':  # Language attribute
            return actual_value == expected_value or actual_value.startswith(expected_value + '-')
            
        return False
        
    def _matches_pseudo(self, node: Node, pseudo: Dict) -> bool:
        """Check if node matches a pseudo-selector."""
        name = pseudo['name']
        value = pseudo['value']
        
        if name == 'first-child':
            return self._is_first_child(node)
        elif name == 'last-child':
            return self._is_last_child(node)
        elif name == 'nth-child':
            return self._is_nth_child(node, value)
        elif name == 'nth-last-child':
            return self._is_nth_last_child(node, value)
        elif name == 'only-child':
            return self._is_only_child(node)
        elif name == 'empty':
            return node.is_empty()
        elif name == 'root':
            return node.parent is None or node.parent.tag == 'document'
            
        return False
        
    def _is_first_child(self, node: Node) -> bool:
        """Check if node is the first child."""
        if not node.parent:
            return False
        siblings = [child for child in node.parent.children if isinstance(child, Node)]
        return siblings and siblings[0] is node
        
    def _is_last_child(self, node: Node) -> bool:
        """Check if node is the last child."""
        if not node.parent:
            return False
        siblings = [child for child in node.parent.children if isinstance(child, Node)]
        return siblings and siblings[-1] is node
        
    def _is_nth_child(self, node: Node, formula: str) -> bool:
        """Check if node matches nth-child formula."""
        if not node.parent:
            return False
            
        siblings = [child for child in node.parent.children if isinstance(child, Node)]
        try:
            index = siblings.index(node) + 1  # 1-based indexing
        except ValueError:
            return False
            
        return self._matches_nth_formula(index, formula)
        
    def _is_nth_last_child(self, node: Node, formula: str) -> bool:
        """Check if node matches nth-last-child formula."""
        if not node.parent:
            return False
            
        siblings = [child for child in node.parent.children if isinstance(child, Node)]
        try:
            index = len(siblings) - siblings.index(node)  # Reverse 1-based indexing
        except ValueError:
            return False
            
        return self._matches_nth_formula(index, formula)
        
    def _is_only_child(self, node: Node) -> bool:
        """Check if node is the only child."""
        if not node.parent:
            return False
        siblings = [child for child in node.parent.children if isinstance(child, Node)]
        return len(siblings) == 1 and siblings[0] is node
        
    def _matches_nth_formula(self, index: int, formula: str) -> bool:
        """Check if index matches nth formula (e.g., '2n+1', 'odd', 'even')."""
        formula = formula.strip().lower()
        
        if formula == 'odd':
            return index % 2 == 1
        elif formula == 'even':
            return index % 2 == 0
        elif formula.isdigit():
            return index == int(formula)
        elif 'n' in formula:
            # Parse an+b formula
            if formula == 'n':
                return True  # Every element
            elif formula.startswith('-n'):
                return False  # No elements
                
            # Extract coefficients
            parts = formula.replace(' ', '').replace('-', '+-')
            if parts.startswith('+'):
                parts = parts[1:]
                
            # Split by n
            if '+' in parts:
                a_part, b_part = parts.split('+', 1)
            elif '-' in parts and parts.count('-') > 0:
                negative_split = parts.split('-')
                a_part = negative_split[0] if negative_split[0] else '1'
                b_part = '-' + negative_split[1] if len(negative_split) > 1 else '0'
            else:
                a_part = parts.replace('n', '') or '1'
                b_part = '0'
                
            a = int(a_part.replace('n', '') or '1')
            b = int(b_part) if b_part.replace('-', '').isdigit() else 0
            
            if a == 0:
                return index == b
            elif a > 0:
                return index >= b and (index - b) % a == 0
            else:
                return index <= b and (b - index) % abs(a) == 0
                
        return False


def select(node: Node, selector: str) -> List[Node]:
    """
    Select all nodes matching the CSS selector.
    
    Args:
        node: Root node to search from
        selector: CSS selector string
        
    Returns:
        List of matching nodes
    """
    if not selector or not selector.strip():
        return []
        
    # Handle multiple selectors separated by commas
    if ',' in selector:
        results = []
        for sub_selector in selector.split(','):
            results.extend(select(node, sub_selector.strip()))
        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for result in results:
            if id(result) not in seen:
                seen.add(id(result))
                unique_results.append(result)
        return unique_results
        
    css_selector = CSSSelector(selector)
    results = []
    
    # Check the root node itself
    if css_selector.matches(node):
        results.append(node)
        
    # Check all descendants
    for descendant in node.descendants():
        if css_selector.matches(descendant):
            results.append(descendant)
            
    return results


def select_one(node: Node, selector: str) -> Optional[Node]:
    """
    Select the first node matching the CSS selector.
    
    Args:
        node: Root node to search from
        selector: CSS selector string
        
    Returns:
        First matching node or None
    """
    results = select(node, selector)
    return results[0] if results else None


# Re-export simple query functions for backwards compatibility
def find_all(node: Node, tag: str) -> List[Node]:
    """Find all descendant nodes with the specified tag."""
    return select(node, tag)


def find_one(node: Node, tag: str) -> Optional[Node]:
    """Find the first descendant node with the specified tag."""
    return select_one(node, tag)