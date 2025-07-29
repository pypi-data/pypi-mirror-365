#!/usr/bin/env python3
"""
Test script to verify that the Document entity type now includes a content field.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add server directory to path
sys.path.append('server')

# Load environment variables
load_dotenv()

async def test_document_entity_type():
    """Test that Document entity type has content field."""
    from graph_service.entity_type_manager import entity_type_manager
    from graphiti_core_falkordb.driver.neo4j_driver import Neo4jDriver
    
    # Initialize driver
    driver = Neo4jDriver(
        uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        user=os.getenv('NEO4J_USER', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'password')
    )
    
    # Set driver for entity type manager
    entity_type_manager.set_driver(driver)
    
    try:
        # Get Document entity type
        document_type = await entity_type_manager.get_entity_type("Document")
        
        if document_type:
            print("✅ Document entity type found!")
            print(f"Description: {document_type.description}")
            print("\nFields:")
            
            has_content = False
            for field in document_type.fields:
                print(f"  - {field.name} ({field.type}): {field.description}")
                if field.name == "content":
                    has_content = True
                    print("    ✅ CONTENT FIELD FOUND!")
            
            if not has_content:
                print("❌ Content field is missing from Document entity type!")
                return False
            
            print(f"\n✅ Document entity type has {len(document_type.fields)} fields including content!")
            
            # Test creating a Pydantic model
            models = await entity_type_manager.get_pydantic_models(["Document"])
            document_model = models.get("Document")
            
            if document_model:
                print("✅ Pydantic model created successfully!")
                
                # Test creating an instance with content
                test_doc = document_model(
                    title="Test Document",
                    content="This is the full text content of the document. It can be searched and analyzed.",
                    document_type="manual",
                    author="Test Author",
                    status="draft"
                )
                
                print("✅ Document instance created with content:")
                print(f"  Title: {test_doc.title}")
                print(f"  Content: {test_doc.content[:50]}...")
                print(f"  Type: {test_doc.document_type}")
                print(f"  Author: {test_doc.author}")
                print(f"  Status: {test_doc.status}")
                
                return True
            else:
                print("❌ Failed to create Pydantic model for Document")
                return False
        else:
            print("❌ Document entity type not found!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Document entity type: {e}")
        return False
    finally:
        await driver.close()

if __name__ == "__main__":
    success = asyncio.run(test_document_entity_type())
    if success:
        print("\n🎉 Document entity type now properly includes content field!")
    else:
        print("\n💥 Document entity type test failed!")
