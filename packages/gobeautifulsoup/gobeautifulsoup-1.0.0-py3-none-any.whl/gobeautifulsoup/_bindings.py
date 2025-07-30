"""
Go library bindings using ctypes

This module provides the interface between Python and the Go shared library
that powers GoBeautifulSoup's high-performance HTML/XML parsing.
"""

import ctypes
import os
import platform
import json
from typing import Optional, Dict, Any, List

class GoLibrary:
    """Wrapper for the Go shared library"""
    
    def __init__(self):
        self._lib = None
        self._load_library()
        self._setup_function_signatures()
    
    def _load_library(self):
        """Load the appropriate shared library for the platform"""
        import platform
        
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Determine architecture
        if machine in ('x86_64', 'amd64'):
            arch = 'amd64'
        elif machine in ('arm64', 'aarch64'):
            arch = 'arm64'
        else:
            arch = 'amd64'  # Fallback
        
        # Determine library name
        if system == "windows":
            lib_name = "libgobeautifulsoup.dll"
        elif system == "darwin":
            lib_name = "libgobeautifulsoup.dylib"
        else:
            lib_name = "libgobeautifulsoup.so"
        
        # Look for the library in package data first
        package_lib_path = os.path.join(
            os.path.dirname(__file__), 
            'libs', 
            system, 
            arch, 
            lib_name
        )
        
        # Fallback paths for development
        possible_paths = [
            package_lib_path,
            os.path.join(os.path.dirname(__file__), lib_name),
            os.path.join(os.path.dirname(__file__), "..", "..", "go-core", lib_name),
            lib_name  # System path
        ]
        
        for path in possible_paths:
            try:
                self._lib = ctypes.CDLL(path)
                break
            except (OSError, FileNotFoundError):
                continue
        
        if self._lib is None:
            raise RuntimeError(
                f"Could not load Go library {lib_name} for {system}/{arch}. "
                f"Please ensure the library is built and available. "
                f"Searched paths: {possible_paths}"
            )
    
    def _setup_function_signatures(self):
        """Setup function signatures for better type safety"""
        # ParseHTML
        self._lib.ParseHTML.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self._lib.ParseHTML.restype = ctypes.c_int
        
        # FindElement
        self._lib.FindElement.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
        self._lib.FindElement.restype = ctypes.c_char_p
        
        # FindAllElements
        self._lib.FindAllElements.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
        self._lib.FindAllElements.restype = ctypes.c_char_p
        
        # SelectElements
        self._lib.SelectElements.argtypes = [ctypes.c_int, ctypes.c_char_p]
        self._lib.SelectElements.restype = ctypes.c_char_p
        
        # GetElementText
        self._lib.GetElementText.argtypes = [ctypes.c_int, ctypes.c_int]
        self._lib.GetElementText.restype = ctypes.c_char_p
        
        # GetElementAttribute
        self._lib.GetElementAttribute.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
        self._lib.GetElementAttribute.restype = ctypes.c_char_p
        
        # SetElementAttribute
        self._lib.SetElementAttribute.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
        self._lib.SetElementAttribute.restype = ctypes.c_bool
        
        # GetElementHTML
        self._lib.GetElementHTML.argtypes = [ctypes.c_int, ctypes.c_int]
        self._lib.GetElementHTML.restype = ctypes.c_char_p
        
        # FreeDocument
        self._lib.FreeDocument.argtypes = [ctypes.c_int]
        self._lib.FreeDocument.restype = None
        
        # FreeString
        self._lib.FreeString.argtypes = [ctypes.c_char_p]
        self._lib.FreeString.restype = None
    
    def parse_html(self, html: str, parser: str = "html.parser") -> int:
        """Parse HTML and return document handle"""
        try:
            html_bytes = html.encode('utf-8')
            parser_bytes = parser.encode('utf-8')
            return self._lib.ParseHTML(html_bytes, parser_bytes)
        except Exception as e:
            raise RuntimeError(f"Failed to parse HTML: {e}")
    
    def find_element(self, doc_handle: int, tag: str, attrs: Dict[str, str] = None) -> Optional[Dict]:
        """Find a single element"""
        try:
            tag_bytes = tag.encode('utf-8')
            attrs_json = json.dumps(attrs or {}).encode('utf-8')
            result = self._lib.FindElement(doc_handle, tag_bytes, attrs_json)
            
            if result:
                result_str = result.decode('utf-8')
                self._lib.FreeString(result)
                return json.loads(result_str) if result_str else None
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to find element: {e}")
    
    def find_all_elements(self, doc_handle: int, tag: str, attrs: Dict[str, str] = None) -> List[Dict]:
        """Find all matching elements"""
        try:
            tag_bytes = tag.encode('utf-8')
            attrs_json = json.dumps(attrs or {}).encode('utf-8')
            result = self._lib.FindAllElements(doc_handle, tag_bytes, attrs_json)
            
            if result:
                result_str = result.decode('utf-8')
                self._lib.FreeString(result)
                return json.loads(result_str) if result_str else []
            return []
        except Exception as e:
            raise RuntimeError(f"Failed to find all elements: {e}")
    
    def select_elements(self, doc_handle: int, selector: str) -> List[Dict]:
        """Select elements using CSS selector"""
        try:
            selector_bytes = selector.encode('utf-8')
            result = self._lib.SelectElements(doc_handle, selector_bytes)
            
            if result:
                result_str = result.decode('utf-8')
                self._lib.FreeString(result)
                return json.loads(result_str) if result_str else []
            return []
        except Exception as e:
            raise RuntimeError(f"Failed to select elements: {e}")
    
    def get_element_text(self, doc_handle: int, element_id: int) -> str:
        """Get text content of an element"""
        try:
            result = self._lib.GetElementText(doc_handle, element_id)
            if result:
                text = result.decode('utf-8')
                self._lib.FreeString(result)
                return text
            return ""
        except Exception as e:
            raise RuntimeError(f"Failed to get element text: {e}")
    
    def get_element_attribute(self, doc_handle: int, element_id: int, attr_name: str) -> Optional[str]:
        """Get attribute value of an element"""
        try:
            attr_bytes = attr_name.encode('utf-8')
            result = self._lib.GetElementAttribute(doc_handle, element_id, attr_bytes)
            
            if result:
                value = result.decode('utf-8')
                self._lib.FreeString(result)
                return value
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to get element attribute: {e}")
    
    def set_element_attribute(self, doc_handle: int, element_id: int, attr_name: str, attr_value: str) -> bool:
        """Set attribute value of an element"""
        try:
            attr_name_bytes = attr_name.encode('utf-8')
            attr_value_bytes = attr_value.encode('utf-8')
            return self._lib.SetElementAttribute(doc_handle, element_id, attr_name_bytes, attr_value_bytes)
        except Exception as e:
            raise RuntimeError(f"Failed to set element attribute: {e}")
    
    def get_element_html(self, doc_handle: int, element_id: int) -> str:
        """Get HTML representation of an element"""
        try:
            result = self._lib.GetElementHTML(doc_handle, element_id)
            if result:
                html = result.decode('utf-8')
                self._lib.FreeString(result)
                return html
            return ""
        except Exception as e:
            raise RuntimeError(f"Failed to get element HTML: {e}")
    
    def free_document(self, doc_handle: int):
        """Free document resources"""
        try:
            if doc_handle and doc_handle != -1:
                self._lib.FreeDocument(doc_handle)
        except Exception:
            # Ignore errors during cleanup
            pass

# Global library instance
_go_library = None

def get_go_library() -> GoLibrary:
    """Get the global Go library instance"""
    global _go_library
    if _go_library is None:
        _go_library = GoLibrary()
    return _go_library
