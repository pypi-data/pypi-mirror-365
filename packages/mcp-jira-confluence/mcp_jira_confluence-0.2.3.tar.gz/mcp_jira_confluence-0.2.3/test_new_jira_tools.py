#!/usr/bin/env python3
"""
Test script for the new Jira tools:
- get-my-assigned-issues
- summarize-jira-issue  
- extract-confluence-links
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_jira_confluence.jira import JiraClient

async def test_new_jira_tools():
    """Test the new Jira tools"""
    
    print("Testing New Jira Tools")
    print("=" * 40)
    
    try:
        # Initialize client
        jira_client = JiraClient()
        
        print("\n1. Testing get_current_user()")
        print("-" * 30)
        try:
            user = await jira_client.get_current_user()
            print(f"✅ Current user: {user.get('displayName', 'Unknown')}")
            print(f"   Email: {user.get('emailAddress', 'Unknown')}")
        except Exception as e:
            print(f"❌ get_current_user failed: {e}")
        
        print("\n2. Testing get_my_assigned_issues()")
        print("-" * 30)
        try:
            result = await jira_client.get_my_assigned_issues(max_results=5)
            issues = result.get('issues', [])
            total = result.get('total', 0)
            print(f"✅ Found {len(issues)} out of {total} assigned issues")
            
            for i, issue in enumerate(issues[:3], 1):  # Show first 3
                key = issue.get('key', 'Unknown')
                summary = issue['fields'].get('summary', 'No summary')[:50]
                priority = issue['fields'].get('priority', {}).get('name', 'Unknown')
                status = issue['fields'].get('status', {}).get('name', 'Unknown')
                print(f"   {i}. {key}: {summary}... (Priority: {priority}, Status: {status})")
            
        except Exception as e:
            print(f"❌ get_my_assigned_issues failed: {e}")
        
        print("\n3. Testing summarize_issue() and extract_confluence_links()")
        print("-" * 30)
        
        # Try to get a real issue key from the results above
        test_issue_key = None
        try:
            if 'issues' in locals() and issues:
                test_issue_key = issues[0].get('key')
        except:
            pass
        
        if test_issue_key:
            print(f"Using test issue: {test_issue_key}")
            
            try:
                # Test summarize_issue
                issue_data = await jira_client.summarize_issue(test_issue_key)
                print(f"✅ summarize_issue returned data for {test_issue_key}")
                print(f"   Has comments: {'comment' in issue_data.get('fields', {})}")
                print(f"   Has remote links: {len(issue_data.get('remoteLinks', []))} links")
                
                # Test extract_confluence_links
                confluence_links = await jira_client.extract_confluence_links(test_issue_key)
                print(f"✅ Found {len(confluence_links)} Confluence links")
                
                for i, link in enumerate(confluence_links[:2], 1):
                    print(f"   {i}. {link['title']} ({link['type']})")
                    
            except Exception as e:
                print(f"❌ Issue analysis failed: {e}")
        else:
            print("ℹ️  No test issue available - testing with mock key")
            try:
                # This will likely fail but we can test the error handling
                await jira_client.extract_confluence_links("TEST-999")
                print("✅ extract_confluence_links executed")
            except Exception as e:
                print(f"ℹ️  Expected error for mock issue: {type(e).__name__}")
        
        print("\n4. Testing _extract_confluence_urls_from_text()")
        print("-" * 30)
        test_text = """
        Check out the documentation at https://mycompany.atlassian.net/wiki/spaces/DOCS/pages/123456/API+Guide
        Also see https://confluence.example.com/display/PROJ/Requirements
        And this link: https://wiki.internal.com/confluence/spaces/DEV/pages/789/Setup
        """
        
        urls = jira_client._extract_confluence_urls_from_text(test_text)
        print(f"✅ Extracted {len(urls)} Confluence URLs from test text:")
        for url in urls:
            print(f"   - {url}")
        
        await jira_client.close()
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_new_jira_tools())
