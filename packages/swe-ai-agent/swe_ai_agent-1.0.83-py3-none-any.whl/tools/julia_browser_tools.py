#!/usr/bin/env python3
"""
Julia Browser Tools for SWE Agent
Comprehensive web browsing capabilities using julia-browser SDK
"""

from langchain_core.tools import tool
from typing import Dict, Any, List, Optional
import json

try:
    from julia_browser import AgentSDK
    JULIA_BROWSER_AVAILABLE = True
    print("✅ julia-browser imported successfully")
except ImportError as e:
    print(f"❌ julia-browser import failed: {e}")
    JULIA_BROWSER_AVAILABLE = False
    AgentSDK = None
except Exception as e:
    print(f"❌ julia-browser initialization error: {e}")
    JULIA_BROWSER_AVAILABLE = False
    AgentSDK = None

# Global browser instance
_browser_instance = None

def get_browser_instance():
    """Get or create browser instance"""
    global _browser_instance
    if _browser_instance is None and JULIA_BROWSER_AVAILABLE:
        try:
            _browser_instance = AgentSDK()
            print("✅ julia-browser AgentSDK instance created")
        except Exception as e:
            print(f"❌ Failed to create AgentSDK: {e}")
            return None
    return _browser_instance

@tool
def open_website(url: str) -> str:
    """
    Open a website in the browser and get page content.
    
    Args:
        url: The website URL to open (e.g., "https://example.com")
        
    Returns:
        JSON string with page title, URL, and content summary
        
    Example:
        open_website("https://python.org")
        
    Note: This is the first step for any web browsing task. Always start with this tool.
    """
    if not JULIA_BROWSER_AVAILABLE:
        return json.dumps({
            "error": "Julia Browser not available. Install with: pip install julia-browser",
            "setup_instructions": "Run 'pip install julia-browser' to enable web browsing capabilities"
        })
    
    try:
        browser = get_browser_instance()
        if browser is None:
            return json.dumps({"error": "Failed to initialize browser instance"})
            
        result = browser.open_website(url)
        
        return json.dumps({
            "success": True,
            "title": result.get('title', 'Unknown'),
            "url": url,
            "content_preview": str(result).replace('\n', ' ')[:200] + "...",
            "message": f"Successfully opened: {result.get('title', url)}",
            "next_steps": "Use list_elements() to see clickable items, or search_page() to find specific content"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to open website: {str(e)}",
            "url": url,
            "suggestion": "Check URL format and internet connection"
        })

@tool 
def list_elements() -> str:
    """
    List all interactive elements on the current page (buttons, links, input fields).
    
    Returns:
        JSON string with numbered list of clickable elements and input fields
        
    Example:
        After opening a website, use this to see what you can interact with:
        list_elements()
        
    Note: Use this after opening a website to see available interactions. Elements are numbered for easy reference.
    """
    if not JULIA_BROWSER_AVAILABLE:
        return json.dumps({"error": "Julia Browser not available"})
    
    try:
        browser = get_browser_instance()
        if browser is None:
            return json.dumps({"error": "No browser instance available. Open a website first."})
            
        elements = browser.list_elements()
        
        return json.dumps({
            "success": True,
            "total_clickable": elements.get('total_clickable', 0),
            "total_inputs": elements.get('total_inputs', 0),
            "elements": elements,
            "usage": "Use click_element(number) for buttons/links, type_text(number, text) for input fields"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to list elements: {str(e)}",
            "suggestion": "Make sure a website is open first using open_website()"
        })

@tool
def click_element(element_number: int) -> str:
    """
    Click on a button, link, or other clickable element by its number.
    
    Args:
        element_number: The number of the element to click (from list_elements())
        
    Returns:
        JSON string with click result and new page information
        
    Example:
        click_element(1)  # Click the first clickable element
        
    Note: Get element numbers from list_elements() first. Use for buttons, links, and clickable items.
    """
    if not JULIA_BROWSER_AVAILABLE:
        return json.dumps({"error": "Julia Browser not available"})
    
    try:
        browser = get_browser_instance()
        if browser is None:
            return json.dumps({"error": "No browser instance available"})
            
        result = browser.click_element(element_number)
        
        return json.dumps({
            "success": True,
            "element_clicked": element_number,
            "result": result,
            "message": f"Successfully clicked element {element_number}",
            "next_steps": "Use get_page_info() to see new page content, or list_elements() for new interactions"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to click element {element_number}: {str(e)}",
            "suggestion": "Check element number exists using list_elements()"
        })

@tool
def type_text(field_number: int, text: str) -> str:
    """
    Type text into an input field by its number.
    
    Args:
        field_number: The number of the input field (from list_elements())
        text: The text to type into the field
        
    Returns:
        JSON string with typing result
        
    Example:
        type_text(1, "search query")  # Type into the first input field
        
    Note: Get field numbers from list_elements() first. Use for text inputs, search boxes, forms.
    """
    if not JULIA_BROWSER_AVAILABLE:
        return json.dumps({"error": "Julia Browser not available"})
    
    try:
        browser = get_browser_instance()
        if browser is None:
            return json.dumps({"error": "No browser instance available"})
            
        browser.type_text(field_number, text)
        
        return json.dumps({
            "success": True,
            "field_number": field_number,
            "text_typed": text,
            "message": f"Successfully typed '{text}' into field {field_number}",
            "next_steps": "Use submit_form() to submit, or click_element() to click submit button"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to type into field {field_number}: {str(e)}",
            "suggestion": "Check field number exists and is an input field using list_elements()"
        })

@tool
def submit_form() -> str:
    """
    Submit the current form with any typed data.
    
    Returns:
        JSON string with form submission result and new page information
        
    Example:
        After typing into fields, submit the form:
        submit_form()
        
    Note: Use after typing text into form fields. Submits the entire form.
    """
    if not JULIA_BROWSER_AVAILABLE:
        return json.dumps({"error": "Julia Browser not available"})
    
    try:
        browser = get_browser_instance()
        if browser is None:
            return json.dumps({"error": "No browser instance available"})
            
        result = browser.submit_form()
        
        return json.dumps({
            "success": True,
            "result": result,
            "title": result.get('title', 'Unknown') if isinstance(result, dict) else str(result),
            "message": "Form submitted successfully",
            "next_steps": "Use get_page_info() to see results, or list_elements() for new interactions"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to submit form: {str(e)}",
            "suggestion": "Make sure form fields are filled and form is present on page"
        })

@tool
def follow_link(link_number: int) -> str:
    """
    Navigate to a link by its number.
    
    Args:
        link_number: The number of the link to follow (from list_elements())
        
    Returns:
        JSON string with navigation result and new page information
        
    Example:
        follow_link(2)  # Follow the second link on the page
        
    Note: Alternative to click_element() specifically for links. Get numbers from list_elements().
    """
    if not JULIA_BROWSER_AVAILABLE:
        return json.dumps({"error": "Julia Browser not available"})
    
    try:
        browser = get_browser_instance()
        if browser is None:
            return json.dumps({"error": "No browser instance available"})
            
        result = browser.follow_link(link_number)
        
        return json.dumps({
            "success": True,
            "link_followed": link_number,
            "result": result,
            "message": f"Successfully followed link {link_number}",
            "next_steps": "Use get_page_info() to see new page, or list_elements() for interactions"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to follow link {link_number}: {str(e)}",
            "suggestion": "Check link number exists using list_elements()"
        })

@tool
def get_page_info() -> str:
    """
    Get current page title, URL, and full content.
    
    Returns:
        JSON string with comprehensive page information
        
    Example:
        get_page_info()  # Get current page details
        
    Note: Use to understand current page content and context. Helpful after navigation or form submission.
    """
    if not JULIA_BROWSER_AVAILABLE:
        return json.dumps({"error": "Julia Browser not available"})
    
    try:
        browser = get_browser_instance()
        if browser is None:
            return json.dumps({"error": "No browser instance available"})
            
        info = browser.get_page_info()
        
        return json.dumps({
            "success": True,
            "title": info.get('title', 'Unknown'),
            "url": info.get('url', 'Unknown'),
            "content": str(info.get('content', ''))[:1000] + "..." if len(str(info.get('content', ''))) > 1000 else str(info.get('content', '')),
            "full_info": info,
            "next_steps": "Use search_page() to find specific content, or list_elements() for interactions"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to get page info: {str(e)}",
            "suggestion": "Make sure a website is open first"
        })

@tool
def search_page(term: str) -> str:
    """
    Search for specific text within the current page.
    
    Args:
        term: The text to search for on the page
        
    Returns:
        JSON string with search results and matches found
        
    Example:
        search_page("Python tutorial")  # Find Python tutorial content
        
    Note: Searches current page content for specific terms. Useful for finding relevant information quickly.
    """
    if not JULIA_BROWSER_AVAILABLE:
        return json.dumps({"error": "Julia Browser not available"})
    
    try:
        browser = get_browser_instance()
        if browser is None:
            return json.dumps({"error": "No browser instance available"})
            
        results = browser.search_page(term)
        
        return json.dumps({
            "success": True,
            "search_term": term,
            "results": results,
            "matches_found": len(results) if isinstance(results, list) else 1 if results else 0,
            "message": f"Search completed for '{term}'",
            "next_steps": "Use scroll tools to navigate to specific content areas"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to search page for '{term}': {str(e)}",
            "suggestion": "Make sure a website is open and has content"
        })

@tool
def scroll_down(chunks: int = 1) -> str:
    """
    Scroll down to see more content on the page.
    
    Args:
        chunks: Number of scroll chunks to move down (default: 1)
        
    Returns:
        JSON string with scroll result and new visible content
        
    Example:
        scroll_down(2)  # Scroll down 2 chunks
        
    Note: Use when page content extends below visible area. Each chunk is a reasonable scroll amount.
    """
    if not JULIA_BROWSER_AVAILABLE:
        return json.dumps({"error": "Julia Browser not available"})
    
    try:
        browser = get_browser_instance()
        if browser is None:
            return json.dumps({"error": "No browser instance available"})
            
        result = browser.scroll_down(chunks)
        
        return json.dumps({
            "success": True,
            "scrolled_chunks": chunks,
            "direction": "down",
            "result": result,
            "message": f"Scrolled down {chunks} chunk(s)",
            "next_steps": "Use list_elements() to see new interactive elements, or continue scrolling"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to scroll down: {str(e)}",
            "suggestion": "Make sure page is loaded and has scrollable content"
        })

@tool
def scroll_up(chunks: int = 1) -> str:
    """
    Scroll up to see previous content on the page.
    
    Args:
        chunks: Number of scroll chunks to move up (default: 1)
        
    Returns:
        JSON string with scroll result and new visible content
        
    Example:
        scroll_up(1)  # Scroll up 1 chunk
        
    Note: Use to go back to previous content areas. Each chunk is a reasonable scroll amount.
    """
    if not JULIA_BROWSER_AVAILABLE:
        return json.dumps({"error": "Julia Browser not available"})
    
    try:
        browser = get_browser_instance()
        if browser is None:
            return json.dumps({"error": "No browser instance available"})
            
        result = browser.scroll_up(chunks)
        
        return json.dumps({
            "success": True,
            "scrolled_chunks": chunks,
            "direction": "up", 
            "result": result,
            "message": f"Scrolled up {chunks} chunk(s)",
            "next_steps": "Use list_elements() to see interactive elements, or continue scrolling"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to scroll up: {str(e)}",
            "suggestion": "Make sure page is loaded and has scrollable content"
        })

@tool
def scroll_to_top() -> str:
    """
    Jump to the top of the page.
    
    Returns:
        JSON string with scroll result
        
    Example:
        scroll_to_top()  # Go to page top
        
    Note: Quick way to return to the beginning of the page content.
    """
    if not JULIA_BROWSER_AVAILABLE:
        return json.dumps({"error": "Julia Browser not available"})
    
    try:
        browser = get_browser_instance()
        if browser is None:
            return json.dumps({"error": "No browser instance available"})
            
        result = browser.scroll_to_top()
        
        return json.dumps({
            "success": True,
            "position": "top",
            "result": result,
            "message": "Scrolled to top of page",
            "next_steps": "Use list_elements() to see page header elements"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to scroll to top: {str(e)}",
            "suggestion": "Make sure page is loaded"
        })

@tool
def scroll_to_bottom() -> str:
    """
    Jump to the bottom of the page.
    
    Returns:
        JSON string with scroll result
        
    Example:
        scroll_to_bottom()  # Go to page bottom
        
    Note: Quick way to see page footer content and bottom elements.
    """
    if not JULIA_BROWSER_AVAILABLE:
        return json.dumps({"error": "Julia Browser not available"})
    
    try:
        browser = get_browser_instance()
        if browser is None:
            return json.dumps({"error": "No browser instance available"})
            
        result = browser.scroll_to_bottom()
        
        return json.dumps({
            "success": True,
            "position": "bottom",
            "result": result,
            "message": "Scrolled to bottom of page",
            "next_steps": "Use list_elements() to see page footer elements"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to scroll to bottom: {str(e)}",
            "suggestion": "Make sure page is loaded"
        })

@tool 
def get_scroll_info() -> str:
    """
    Get current scroll position and page progress information.
    
    Returns:
        JSON string with scroll position and page navigation info
        
    Example:
        get_scroll_info()  # Check current position
        
    Note: Helpful to understand current position on long pages and navigation progress.
    """
    if not JULIA_BROWSER_AVAILABLE:
        return json.dumps({"error": "Julia Browser not available"})
    
    try:
        browser = get_browser_instance()
        if browser is None:
            return json.dumps({"error": "No browser instance available"})
            
        info = browser.get_scroll_info()
        
        return json.dumps({
            "success": True,
            "scroll_info": info,
            "position": info.get('position', 'unknown'),
            "progress": info.get('progress', 'unknown'),
            "message": "Current scroll position retrieved",
            "next_steps": "Use scroll tools to navigate or list_elements() for interactions"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to get scroll info: {str(e)}",
            "suggestion": "Make sure page is loaded"
        })