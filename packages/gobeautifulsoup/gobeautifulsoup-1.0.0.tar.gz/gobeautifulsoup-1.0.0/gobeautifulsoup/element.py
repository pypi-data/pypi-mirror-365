"""
Element classes that mimic BeautifulSoup's Tag and NavigableString

This module provides the Tag and NavigableString classes that offer the same
interface as BeautifulSoup4's element classes but backed by the Go implementation.
"""

from typing import Optional, Dict, List, Union, Any, Iterator
import re
from ._bindings import get_go_library

class NavigableString(str):
    """
    String that can navigate the parse tree
    
    This class extends str to provide navigation capabilities similar to
    BeautifulSoup4's NavigableString.
    """
    
    def __new__(cls, value):
        return str.__new__(cls, value)
    
    def __init__(self, value):
        super().__init__()
        self.parent = None
        self.next_sibling = None
        self.previous_sibling = None
    
    def __repr__(self):
        return f"'{str(self)}'"
    
    @property
    def string(self):
        """Return self for compatibility"""
        return self
    
    def get_text(self, separator: str = "", strip: bool = False) -> str:
        """Get text content"""
        text = str(self)
        if strip:
            text = text.strip()
        return text
    
    # Navigation properties for compatibility
    @property
    def next(self):
        """Next sibling (alias for next_sibling)"""
        return self.next_sibling
    
    @property
    def previous(self):
        """Previous sibling (alias for previous_sibling)"""
        return self.previous_sibling

class Tag:
    """
    Represents an HTML/XML tag element
    
    This class provides the same interface as BeautifulSoup4's Tag class but
    with Go backend performance improvements.
    """
    
    def __init__(self, element_data: Dict[str, Any], soup_instance=None):
        """
        Initialize Tag from Go element data
        
        Args:
            element_data: Dictionary containing element information from Go
            soup_instance: Reference to the parent BeautifulSoup instance
        """
        self._element_id = element_data.get('id', 0)
        self._doc_handle = element_data.get('doc_handle', 0) 
        self._tag_name = element_data.get('name', '')
        self._attrs = element_data.get('attrs', {})
        self._text = element_data.get('text', '')
        self._soup = soup_instance
        self._go_lib = get_go_library()
        
        # Cache for navigation (lazy loading)
        self._parent = None
        self._children = None
        self._next_sibling = None
        self._previous_sibling = None
        self._descendants = None
    
    @property
    def name(self) -> str:
        """Tag name"""
        return self._tag_name
    
    @name.setter
    def name(self, value: str):
        """Set tag name (not implemented in current Go backend)"""
        raise NotImplementedError("Tag name modification not yet implemented")
    
    @property
    def attrs(self) -> Dict[str, str]:
        """Tag attributes dictionary"""
        if self._doc_handle and self._element_id:
            # For now, return cached attrs. In full implementation, 
            # we'd fetch fresh from Go backend
            pass
        return self._attrs.copy()
    
    @attrs.setter
    def attrs(self, value: Dict[str, str]):
        """Set tag attributes"""
        if not isinstance(value, dict):
            raise ValueError("Attributes must be a dictionary")
        
        # Update cached attributes
        self._attrs = value.copy()
        
        # In full implementation, we'd update in Go backend
        # For now, just cache locally
    
    def get(self, key: str, default=None):
        """
        Get attribute value
        
        Args:
            key: Attribute name
            default: Default value if attribute doesn't exist
            
        Returns:
            Attribute value or default
        """
        return self.attrs.get(key, default)
    
    def __getitem__(self, key: str):
        """Get attribute value using [] syntax"""
        try:
            return self.attrs[key]
        except KeyError:
            raise KeyError(f"'{key}'")
    
    def __setitem__(self, key: str, value: str):
        """Set attribute value using [] syntax"""
        if self._doc_handle and self._element_id:
            try:
                success = self._go_lib.set_element_attribute(
                    self._doc_handle, self._element_id, key, value
                )
                if success:
                    self._attrs[key] = value
            except Exception:
                # Fallback to local cache
                self._attrs[key] = value
        else:
            self._attrs[key] = value
    
    def __delitem__(self, key: str):
        """Delete attribute using del syntax"""
        if key in self._attrs:
            del self._attrs[key]
        # In full implementation, we'd also delete from Go backend
    
    def __contains__(self, key: str) -> bool:
        """Check if attribute exists"""
        return key in self.attrs
    
    def has_attr(self, key: str) -> bool:
        """Check if attribute exists (BeautifulSoup4 compatibility)"""
        return key in self.attrs
    
    @property
    def string(self) -> Optional[NavigableString]:
        """Get the string content if this tag contains only a string"""
        text = self.get_text()
        if text and not self.find_all():  # No child tags
            return NavigableString(text)
        return None
    
    @property
    def text(self) -> str:
        """Get all text content"""
        return self.get_text()
    
    def get_text(self, separator: str = "", strip: bool = False) -> str:
        """
        Get text content with options
        
        Args:
            separator: String to join text segments
            strip: Whether to strip whitespace
            
        Returns:
            Text content of the element
        """
        if self._doc_handle and self._element_id:
            try:
                text = self._go_lib.get_element_text(self._doc_handle, self._element_id)
            except Exception:
                text = self._text
        else:
            text = self._text
        
        if strip:
            text = text.strip()
        return text
    
    def __str__(self) -> str:
        """String representation (HTML)"""
        if self._doc_handle and self._element_id:
            try:
                return self._go_lib.get_element_html(self._doc_handle, self._element_id)
            except Exception:
                pass
        
        # Fallback: construct basic HTML
        attrs_str = ""
        if self._attrs:
            attrs_list = [f'{k}=\"{v}\"' for k, v in self._attrs.items()]
            attrs_str = " " + " ".join(attrs_list)
        
        if self._text:
            return f"<{self._tag_name}{attrs_str}>{self._text}</{self._tag_name}>"
        else:
            return f"<{self._tag_name}{attrs_str}></{self._tag_name}>"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return str(self)
    
    def prettify(self, encoding: Optional[str] = None, formatter: str = "minimal") -> str:
        """
        Pretty-print this element
        
        Args:
            encoding: Output encoding (ignored, always returns str)
            formatter: Formatting style (ignored in current implementation)
            
        Returns:
            Pretty-formatted HTML string
        """
        return str(self)
    
    # Navigation properties
    @property
    def parent(self) -> Optional['Tag']:
        """Get parent element"""
        # Navigation not fully implemented in current Go backend
        return self._parent
    
    @property
    def children(self) -> List[Union['Tag', NavigableString]]:
        """Get direct child elements"""
        # For now, return empty list. In full implementation,
        # we'd fetch from Go backend
        if self._children is None:
            self._children = []
        return self._children
    
    @property
    def descendants(self) -> Iterator[Union['Tag', NavigableString]]:
        """Iterate over all descendant elements"""
        return iter([])  # Placeholder
    
    @property
    def next_sibling(self) -> Optional[Union['Tag', NavigableString]]:
        """Get next sibling element"""
        return self._next_sibling
    
    @property
    def previous_sibling(self) -> Optional[Union['Tag', NavigableString]]:
        """Get previous sibling element"""
        return self._previous_sibling
    
    # Aliases for backwards compatibility
    @property
    def next(self):
        """Next sibling (alias for next_sibling)"""
        return self.next_sibling
    
    @property
    def previous(self):
        """Previous sibling (alias for previous_sibling)"""
        return self.previous_sibling
    
    # Search methods that delegate to soup
    def find(self, name=None, attrs=None, recursive=True, string=None, **kwargs) -> Optional['Tag']:
        """Find first matching descendant"""
        if not self._soup:
            return None
        
        # In full implementation, we'd search within this element only
        # For now, delegate to soup with a warning that scope is global
        return self._soup.find(name, attrs, recursive, string, **kwargs)
    
    def find_all(self, name=None, attrs=None, recursive=True, string=None, 
                 limit=None, **kwargs) -> List['Tag']:
        """Find all matching descendants"""
        if not self._soup:
            return []
        
        # In full implementation, we'd search within this element only
        # For now, delegate to soup with a warning that scope is global
        return self._soup.find_all(name, attrs, recursive, string, limit, **kwargs)
    
    def select(self, selector: str) -> List['Tag']:
        """Find elements using CSS selector within this element"""
        if not self._soup:
            return []
        
        # In full implementation, we'd scope the selector to this element
        return self._soup.select(selector)
    
    def select_one(self, selector: str) -> Optional['Tag']:
        """Find first element using CSS selector within this element"""
        results = self.select(selector)
        return results[0] if results else None
    
    # Backwards compatibility
    findAll = find_all
    
    # Iteration support
    def __iter__(self) -> Iterator[Union['Tag', NavigableString]]:
        """Iterate over direct children"""
        return iter(self.children)
    
    def __len__(self) -> int:
        """Number of direct children"""
        return len(self.children)
    
    def __bool__(self) -> bool:
        """Tag is always truthy"""
        return True
    
    # Utility methods
    def decompose(self):
        """Remove this element from the tree (not implemented)"""
        raise NotImplementedError("Element decomposition not yet implemented")
    
    def extract(self) -> 'Tag':
        """Remove and return this element (not implemented)"""
        raise NotImplementedError("Element extraction not yet implemented")
    
    def insert(self, position: int, new_child):
        """Insert a child at the specified position (not implemented)"""
        raise NotImplementedError("Element insertion not yet implemented")
    
    def append(self, new_child):
        """Append a child (not implemented)"""
        raise NotImplementedError("Element appending not yet implemented")
    
    def clear(self):
        """Remove all children (not implemented)"""
        raise NotImplementedError("Element clearing not yet implemented")
    
    # Convenience methods for common attributes
    def get_class(self) -> List[str]:
        """Get CSS classes as a list"""
        class_attr = self.get('class', '')
        if isinstance(class_attr, list):
            return class_attr
        return class_attr.split() if class_attr else []
    
    def get_id(self) -> Optional[str]:
        """Get the id attribute"""
        return self.get('id')
    
    def has_class(self, class_name: str) -> bool:
        """Check if element has a specific CSS class"""
        return class_name in self.get_class()
    
    # HTML5 data attributes
    def get_data_attrs(self) -> Dict[str, str]:
        """Get all data-* attributes"""
        return {k: v for k, v in self.attrs.items() if k.startswith('data-')}
