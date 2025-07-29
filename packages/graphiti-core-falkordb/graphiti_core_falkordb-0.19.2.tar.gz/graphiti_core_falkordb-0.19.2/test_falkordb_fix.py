#!/usr/bin/env python3
"""
Test script to verify FalkorDB parameter handling fix.
This script tests the specific issue that was causing the malformed Cypher query error.
"""

import asyncio
import os
from datetime import datetime, timezone

from graphiti_core_falkordb.driver.falkordb_driver import FalkorDriver


async def test_falkordb_parameter_handling():
    """Test that FalkorDB driver correctly handles parameters."""
    
    # Use environment variables or defaults for FalkorDB connection
    falkor_host = os.environ.get('FALKORDB_HOST', 'localhost')
    falkor_port = int(os.environ.get('FALKORDB_PORT', '6379'))
    falkor_username = os.environ.get('FALKORDB_USERNAME', None)
    falkor_password = os.environ.get('FALKORDB_PASSWORD', None)
    
    print(f"Connecting to FalkorDB at {falkor_host}:{falkor_port}")
    
    try:
        # Create FalkorDB driver
        driver = FalkorDriver(
            host=falkor_host,
            port=falkor_port,
            username=falkor_username,
            password=falkor_password
        )
        
        print("✓ FalkorDB driver created successfully")
        
        # Test basic query execution
        print("Testing basic query execution...")
        result = await driver.execute_query('RETURN 1 as test')
        if result:
            result_set, header, _ = result
            print(f"✓ Basic query successful. Header: {header}, Result: {result_set}")
        
        # Test the specific parameter handling that was causing the issue
        print("Testing parameter handling (the original issue)...")
        
        # This simulates the call that was failing in node_similarity_search
        test_query = """
        MATCH (n:Entity)
        WHERE n.group_id IS NOT NULL
        WITH n, 0.5 AS score
        WHERE score > $min_score
        RETURN n.uuid AS uuid
        LIMIT $limit
        """
        
        # This is the problematic call pattern that was causing the issue
        result = await driver.execute_query(
            test_query,
            params={'group_ids': ['test_group']},  # This was causing conflicts
            search_vector=[0.1] * 1024,           # Individual parameters
            group_ids=['test_group'],             # Duplicate parameter
            limit=10,
            min_score=0.5,
            database_='default_db',
            routing_='r',
        )
        
        print("✓ Parameter handling test successful - no malformed query error!")
        
        # Test datetime conversion
        print("Testing datetime parameter conversion...")
        test_datetime = datetime.now(timezone.utc)
        result = await driver.execute_query(
            'RETURN $test_date as date_value',
            test_date=test_datetime
        )
        if result:
            result_set, header, _ = result
            print(f"✓ Datetime conversion successful. Result: {result_set}")
        
        await driver.close()
        print("✓ All tests passed!")
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    print("Testing FalkorDB parameter handling fix...")
    print("=" * 50)
    
    success = asyncio.run(test_falkordb_parameter_handling())
    
    if success:
        print("\n🎉 All tests passed! The FalkorDB parameter handling fix is working.")
    else:
        print("\n❌ Tests failed. There may still be issues with the fix.")
