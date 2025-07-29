"""Formatting utilities for converting between Markdown and Jira/Confluence markup."""

import re
from typing import Optional


class JiraFormatter:
    """Convert between Markdown and Jira markup."""
    
    @staticmethod
    def markdown_to_jira(input_text: str) -> str:
        """Convert Markdown text to Jira markup."""
        output = input_text
        
        # Headers
        output = re.sub(r"^# (.*?)$", r"h1. \1", output, flags=re.MULTILINE)
        output = re.sub(r"^## (.*?)$", r"h2. \1", output, flags=re.MULTILINE)
        output = re.sub(r"^### (.*?)$", r"h3. \1", output, flags=re.MULTILINE)
        output = re.sub(r"^#### (.*?)$", r"h4. \1", output, flags=re.MULTILINE)
        output = re.sub(r"^##### (.*?)$", r"h5. \1", output, flags=re.MULTILINE)
        output = re.sub(r"^###### (.*?)$", r"h6. \1", output, flags=re.MULTILINE)
        
        # Bold and Italic
        output = re.sub(r"\*\*(.*?)\*\*", r"*\1*", output)  # Bold
        output = re.sub(r"__(.*?)__", r"*\1*", output)      # Bold
        output = re.sub(r"\*(.*?)\*", r"_\1_", output)      # Italic
        output = re.sub(r"_(.*?)_", r"_\1_", output)        # Italic
        
        # Lists
        # Bulleted lists
        output = re.sub(r"^- (.*?)$", r"* \1", output, flags=re.MULTILINE)
        output = re.sub(r"^\* (.*?)$", r"* \1", output, flags=re.MULTILINE)
        
        # Numbered lists
        output = re.sub(r"^(\d+)\. (.*?)$", r"# \2", output, flags=re.MULTILINE)
        
        # Code blocks
        output = re.sub(r"```(\w+)?\n(.*?)\n```", r"{code:\1}\2{code}", output, flags=re.DOTALL)
        output = re.sub(r"`([^`]+)`", r"{{{\1}}}", output)  # Inline code
        
        # Links
        output = re.sub(r"\[(.*?)\]\((.*?)\)", r"[\1|\2]", output)
        
        # Images
        output = re.sub(r"!\[(.*?)\]\((.*?)\)", r"!\2!", output)
        
        return output
    
    @staticmethod
    def jira_to_markdown(input_text: str) -> str:
        """Convert Jira markup to Markdown text."""
        output = input_text
        
        # Headers
        output = re.sub(r"^h1\. (.*?)$", r"# \1", output, flags=re.MULTILINE)
        output = re.sub(r"^h2\. (.*?)$", r"## \1", output, flags=re.MULTILINE)
        output = re.sub(r"^h3\. (.*?)$", r"### \1", output, flags=re.MULTILINE)
        output = re.sub(r"^h4\. (.*?)$", r"#### \1", output, flags=re.MULTILINE)
        output = re.sub(r"^h5\. (.*?)$", r"##### \1", output, flags=re.MULTILINE)
        output = re.sub(r"^h6\. (.*?)$", r"###### \1", output, flags=re.MULTILINE)
        
        # Bold and Italic
        output = re.sub(r"\*(.*?)\*", r"**\1**", output)  # Bold
        output = re.sub(r"_(.*?)_", r"*\1*", output)      # Italic
        
        # Lists
        # Bulleted lists
        output = re.sub(r"^\* (.*?)$", r"- \1", output, flags=re.MULTILINE)
        
        # Numbered lists
        output = re.sub(r"^# (.*?)$", r"1. \1", output, flags=re.MULTILINE)
        
        # Code blocks
        output = re.sub(r"\{code(?::\w+)?\}(.*?)\{code\}", r"```\n\1\n```", output, flags=re.DOTALL)
        output = re.sub(r"\{\{\{(.*?)\}\}\}", r"`\1`", output)  # Inline code
        
        # Links
        output = re.sub(r"\[(.*?)\|(.*?)\]", r"[\1](\2)", output)
        
        # Images
        output = re.sub(r"!(.*?)!", r"![](\1)", output)
        
        return output


class ConfluenceFormatter:
    """Convert between Markdown and Confluence markup."""
    
    @staticmethod
    def markdown_to_confluence(input_text: str) -> str:
        """Convert Markdown text to Confluence storage format (XHTML)."""
        import re
        
        lines = input_text.split('\n')
        output_lines = []
        in_code_block = False
        code_language = ""
        code_content = []
        in_ul_list = False
        in_ol_list = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Handle code blocks
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Start of code block
                    in_code_block = True
                    code_language = line.strip()[3:].strip()
                    code_content = []
                else:
                    # End of code block
                    in_code_block = False
                    code_text = '\n'.join(code_content)
                    if code_language:
                        output_lines.append(f'<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">{code_language}</ac:parameter><ac:plain-text-body><![CDATA[{code_text}]]></ac:plain-text-body></ac:structured-macro>')
                    else:
                        output_lines.append(f'<ac:structured-macro ac:name="code"><ac:plain-text-body><![CDATA[{code_text}]]></ac:plain-text-body></ac:structured-macro>')
                i += 1
                continue
            
            if in_code_block:
                code_content.append(line)
                i += 1
                continue
            
            # Handle headers
            if line.strip().startswith('#'):
                # Close any open lists
                if in_ul_list:
                    output_lines.append('</ul>')
                    in_ul_list = False
                if in_ol_list:
                    output_lines.append('</ol>')
                    in_ol_list = False
                    
                header_match = re.match(r'^(#{1,6})\s+(.*)', line.strip())
                if header_match:
                    level = len(header_match.group(1))
                    text = header_match.group(2)
                    output_lines.append(f'<h{level}>{text}</h{level}>')
                i += 1
                continue
            
            # Handle unordered lists
            if re.match(r'^[\s]*[-*]\s+', line):
                if not in_ul_list:
                    if in_ol_list:
                        output_lines.append('</ol>')
                        in_ol_list = False
                    output_lines.append('<ul>')
                    in_ul_list = True
                
                # Extract list item content
                list_item = re.sub(r'^[\s]*[-*]\s+', '', line)
                list_item = ConfluenceFormatter._process_inline_formatting(list_item)
                output_lines.append(f'<li>{list_item}</li>')
                i += 1
                continue
            
            # Handle ordered lists
            if re.match(r'^[\s]*\d+\.\s+', line):
                if not in_ol_list:
                    if in_ul_list:
                        output_lines.append('</ul>')
                        in_ul_list = False
                    output_lines.append('<ol>')
                    in_ol_list = True
                
                # Extract list item content
                list_item = re.sub(r'^[\s]*\d+\.\s+', '', line)
                list_item = ConfluenceFormatter._process_inline_formatting(list_item)
                output_lines.append(f'<li>{list_item}</li>')
                i += 1
                continue
            
            # If we're here and in a list, close it
            if in_ul_list:
                output_lines.append('</ul>')
                in_ul_list = False
            if in_ol_list:
                output_lines.append('</ol>')
                in_ol_list = False
            
            # Handle empty lines
            if not line.strip():
                output_lines.append('')
                i += 1
                continue
            
            # Handle regular paragraphs
            processed_line = ConfluenceFormatter._process_inline_formatting(line)
            output_lines.append(f'<p>{processed_line}</p>')
            i += 1
        
        # Close any remaining open lists
        if in_ul_list:
            output_lines.append('</ul>')
        if in_ol_list:
            output_lines.append('</ol>')
        
        # Join lines and clean up
        output = '\n'.join(output_lines)
        
        # Clean up multiple empty lines
        output = re.sub(r'\n{3,}', '\n\n', output)
        
        return output.strip()
    
    @staticmethod
    def _process_inline_formatting(text: str) -> str:
        """Process inline formatting like bold, italic, code, links, images."""
        output = text
        
        # Bold and Italic (order matters - do bold first to avoid conflicts)
        output = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', output)  # Bold
        output = re.sub(r'__(.*?)__', r'<strong>\1</strong>', output)      # Bold
        output = re.sub(r'\*(.*?)\*', r'<em>\1</em>', output)             # Italic
        output = re.sub(r'(?<!\*)\b_(.*?)_\b(?!\*)', r'<em>\1</em>', output)  # Italic (avoiding conflicts with bold)
        
        # Inline code
        output = re.sub(r'`([^`]+)`', r'<code>\1</code>', output)
        
        # Links
        output = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', output)
        
        # Images
        output = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<ac:image><ri:url ri:value="\2"/></ac:image>', output)
        
        return output
    
    @staticmethod
    def confluence_to_markdown(input_text: str) -> str:
        """Convert Confluence storage format to Markdown text."""
        # This is a simplified implementation
        output = input_text
        
        # Remove CDATA and macro wrapper if present
        output = re.sub(r'<ac:structured-macro[^>]*>.*?<!\[CDATA\[(.*?)\]\]>.*?</ac:structured-macro>', r'\1', output, flags=re.DOTALL)
        
        # Headers
        output = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', output)
        output = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', output)
        output = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', output)
        output = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', output)
        output = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1', output)
        output = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1', output)
        
        # Bold and Italic
        output = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', output)
        output = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', output)
        output = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', output)
        output = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', output)
        
        # Lists
        # This is simplified and might not handle nested lists properly
        output = re.sub(r'<ul[^>]*>.*?<li[^>]*>(.*?)</li>.*?</ul>', r'- \1', output)
        output = re.sub(r'<ol[^>]*>.*?<li[^>]*>(.*?)</li>.*?</ol>', r'1. \1', output)
        
        # Code blocks - simplified
        output = re.sub(r'<ac:structured-macro ac:name="code"[^>]*>.*?<ac:plain-text-body><!\[CDATA\[(.*?)\]\]></ac:plain-text-body></ac:structured-macro>', r'```\n\1\n```', output, flags=re.DOTALL)
        
        output = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', output)  # Inline code
        
        # Links
        output = re.sub(r'<a href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', output)
        
        # Images
        output = re.sub(r'<ac:image[^>]*><ri:url ri:value="([^"]+)"[^>]*></ac:image>', r'![](\1)', output)
        output = re.sub(r'<img src="([^"]+)"[^>]*>', r'![](\1)', output)
        
        # Paragraphs
        output = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', output)
        
        # Clean up any remaining HTML tags (simplified)
        output = re.sub(r'<[^>]+>', '', output)
        
        # Fix multiple newlines
        output = re.sub(r'\n{3,}', '\n\n', output)
        
        return output.strip()
