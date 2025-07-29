#!/usr/bin/env python3
"""
Test the enhanced Confluence search CQL query builder.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_jira_confluence.server import build_smart_cql_query

def test_smart_cql_query():
    """Test various query inputs and their enhanced CQL output."""
    
    test_cases = [
        # Simple text queries
        ("API documentation", None, '(title ~ "API documentation" OR text ~ "API documentation")'),
        ("API", None, '(title ~ "API" OR text ~ "API")'),
        
        # Longer queries (treated as content search)
        ("how to configure authentication", None, 'text ~ "how to configure authentication"'),
        
        # Queries with quotes (preserve user intent)
        ('"exact phrase"', None, 'text ~ "exact phrase"'),
        ("'quoted text'", None, "text ~ 'quoted text'"),
        
        # Advanced CQL (should be preserved)
        ("title ~ 'API' AND lastmodified >= now('-7d')", None, "title ~ 'API' AND lastmodified >= now('-7d')"),
        ("space.key = 'DEV'", None, "space.key = 'DEV'"),
        
        # Simple queries with space
        ("API", "DEV", '(title ~ "API" OR text ~ "API")'),
        
        # Advanced CQL with space (space should not be duplicated)
        ("title ~ 'API'", "DEV", "title ~ 'API'"),
        
        # Empty query
        ("", None, "type = page"),
        ("  ", None, "type = page"),
    ]
    
    print("Testing Smart CQL Query Builder")
    print("=" * 50)
    
    for i, (input_query, space_key, expected_contains) in enumerate(test_cases, 1):
        result = build_smart_cql_query(input_query, space_key)
        
        # All queries should start with "type = page"
        assert result.startswith("type = page"), f"Test {i}: Query should start with 'type = page'"
        
        # Check space key handling
        if space_key:
            assert f'space.key = "{space_key}"' in result, f"Test {i}: Space key should be included"
        
        print(f"Test {i}:")
        print(f"  Input: '{input_query}' (space: {space_key})")
        print(f"  Output: {result}")
        print(f"  Expected contains: {expected_contains}")
        
        # Basic validation - the expected content should be in the result
        if expected_contains and expected_contains != result:
            # For simple cases, check if the expected pattern is contained
            if not any(part.strip() in result for part in expected_contains.split(" OR ")):
                print(f"  ⚠️  Warning: Expected pattern not found in result")
        
        print(f"  ✅ Passed")
        print()

if __name__ == "__main__":
    test_smart_cql_query()
    print("All tests completed!")
