#!/usr/bin/env python3
import re
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_jira_confluence.formatter import ConfluenceFormatter

def test_markdown_detection(content):
    markdown_patterns = [
        r'^#{1,6}\s+',           # Headers
        r'\*\*(.*?)\*\*',        # Bold
        r'\*(.*?)\*',            # Italic/emphasis  
        r'`([^`]+)`',            # Inline code
        r'```',                  # Code blocks
        r'^[\s]*[-*]\s+',        # Unordered lists
        r'^[\s]*\d+\.\s+',       # Ordered lists
        r'\[.*?\]\(.*?\)',       # Links
        r'!\[.*?\]\(.*?\)',      # Images
    ]
    
    is_markdown = any(re.search(pattern, content, re.MULTILINE) for pattern in markdown_patterns)
    return is_markdown

def main():
    print("Testing Confluence Formatter Improvements")
    print("=" * 50)
    
    # Test markdown detection
    print("\n1. Testing Markdown Detection:")
    tests = [
        ('# This is markdown', True),
        ('**Bold text**', True), 
        ('- List item', True),
        ('1. Numbered item', True),
        ('`code`', True),
        ('<p>HTML content</p>', False),
        ('Plain text only', False),
        ('[link](http://example.com)', True),
    ]
    
    for content, expected in tests:
        result = test_markdown_detection(content)
        status = '✓' if result == expected else '✗'
        print(f'{status} "{content}" -> {result} (expected {expected})')
    
    # Test formatting
    print("\n2. Testing Confluence Formatting:")
    
    test_markdown = """# Test Document

This is a **test document** with various *formatting*.

## Lists
Here are some items:
- First item
- Second item with `inline code`
- Third item

And numbered:
1. Step one
2. Step two
3. Step three

## Code Block
```python
def hello():
    print("Hello, World!")
```

## Links
Visit [Confluence](https://www.atlassian.com/software/confluence) for more info.
"""
    
    result = ConfluenceFormatter.markdown_to_confluence(test_markdown)
    print("Input markdown:")
    print(test_markdown)
    print("\nConverted to Confluence format:")
    print(result)
    
    # Validate key elements are present
    print("\n3. Validation:")
    validations = [
        ('<h1>Test Document</h1>', 'Header conversion'),
        ('<strong>test document</strong>', 'Bold formatting'),
        ('<em>formatting</em>', 'Italic formatting'),
        ('<ul>', 'Unordered list start'),
        ('<li>First item</li>', 'List item'),
        ('</ul>', 'Unordered list end'),
        ('<ol>', 'Ordered list start'),
        ('</ol>', 'Ordered list end'),
        ('<code>inline code</code>', 'Inline code'),
        ('ac:structured-macro ac:name="code"', 'Code block macro'),
        ('<a href="https://www.atlassian.com/software/confluence">Confluence</a>', 'Link formatting'),
    ]
    
    for expected, description in validations:
        if expected in result:
            print(f'✓ {description}')
        else:
            print(f'✗ {description} - Expected: {expected}')

if __name__ == "__main__":
    main()
