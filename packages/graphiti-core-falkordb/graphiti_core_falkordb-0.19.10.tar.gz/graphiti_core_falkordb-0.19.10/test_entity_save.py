#!/usr/bin/env python3
"""
Simple test script to verify that entity save works with FalkorDB.
"""

import asyncio
import os
from datetime import datetime, timezone

from graphiti_core_falkordb import Graphiti
from graphiti_core_falkordb.nodes import EntityNode


async def test_entity_save():
    """Test that entity save works with FalkorDB."""
    
    # Use environment variables or defaults
    falkor_host = os.getenv('FALKOR_HOST', 'localhost')
    falkor_port = int(os.getenv('FALKOR_PORT', '6379'))
    falkor_password = os.getenv('FALKOR_PASSWORD', None)
    
    print(f"Connecting to FalkorDB at {falkor_host}:{falkor_port}")
    
    try:
        # Initialize Graphiti with FalkorDB
        graphiti = Graphiti(
            uri=f"falkor://{falkor_host}:{falkor_port}",
            user="",
            password=falkor_password or "",
        )
        
        print("Connected to FalkorDB successfully")
        
        # Create a test entity
        entity = EntityNode(
            name="Test Entity",
            group_id="test_group",
            summary="This is a test entity",
            labels=["Person", "TestLabel"],
            attributes={"test_attr": "test_value"}
        )
        
        print(f"Created entity: {entity.name} with UUID: {entity.uuid}")
        
        # Try to save the entity
        print("Attempting to save entity...")
        result = await entity.save(graphiti.driver)
        
        print(f"Entity saved successfully! Result: {result}")
        
        # Try to retrieve the entity
        print("Attempting to retrieve entity...")
        retrieved_entity = await EntityNode.get_by_uuid(graphiti.driver, entity.uuid)
        
        print(f"Entity retrieved successfully: {retrieved_entity.name}")
        print(f"Labels: {retrieved_entity.labels}")
        print(f"Attributes: {retrieved_entity.attributes}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_entity_save())
    if success:
        print("✅ Entity save test passed!")
    else:
        print("❌ Entity save test failed!")
