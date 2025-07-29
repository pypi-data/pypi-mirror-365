#!/usr/bin/env python3
"""Test script to verify markdown to Confluence formatting improvements."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_jira_confluence.formatter import ConfluenceFormatter

def test_markdown_formatting():
    """Test various markdown formatting scenarios."""
    
    test_cases = [
        {
            "name": "Headers",
            "input": """# Main Title
## Subtitle
### Section
#### Subsection""",
            "expected_tags": ["<h1>", "<h2>", "<h3>", "<h4>"]
        },
        {
            "name": "Lists",
            "input": """Here are some items:
- First item
- Second item
- Third item

And numbered:
1. First step
2. Second step
3. Third step""",
            "expected_tags": ["<ul>", "<li>", "</ul>", "<ol>", "</ol>"]
        },
        {
            "name": "Mixed formatting",
            "input": """# API Documentation

This document describes the **important** API endpoints.

## Authentication
You need an *API key* to access the endpoints.

### Code Example
```python
import requests
response = requests.get('https://api.example.com')
```

### Links and Images
Visit [our website](https://example.com) for more info.
![Logo](https://example.com/logo.png)""",
            "expected_tags": ["<h1>", "<h2>", "<h3>", "<strong>", "<em>", "<code>", "<a href=", "<ac:structured-macro"]
        }
    ]
    
    print("Testing Confluence Markdown Formatter")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print("-" * 30)
        print("Input:")
        print(test_case['input'])
        print("\nOutput:")
        result = ConfluenceFormatter.markdown_to_confluence(test_case['input'])
        print(result)
        
        print("\nValidation:")
        for tag in test_case['expected_tags']:
            if tag in result:
                print(f"✓ Found expected tag: {tag}")
            else:
                print(f"✗ Missing expected tag: {tag}")
        print()

if __name__ == "__main__":
    test_markdown_formatting()
