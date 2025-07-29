#!/usr/bin/env python3
"""
Script to update the existing Document entity type to include the content field.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add server directory to path
sys.path.append('server')

# Load environment variables
load_dotenv()

async def update_document_entity_type():
    """Update the Document entity type to include content field."""
    from graph_service.entity_type_manager import entity_type_manager
    from graph_service.dto.entity_types import EntityTypeField, UpdateEntityTypeRequest
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
        # Get current Document entity type
        current_doc_type = await entity_type_manager.get_entity_type("Document")
        
        if not current_doc_type:
            print("❌ Document entity type not found!")
            return False
        
        print("📋 Current Document entity type fields:")
        for field in current_doc_type.fields:
            print(f"  - {field.name} ({field.type}): {field.description}")
        
        # Check if content field already exists
        has_content = any(field.name == "content" for field in current_doc_type.fields)
        
        if has_content:
            print("✅ Document entity type already has content field!")
            return True
        
        # Create updated fields list with content field added
        updated_fields = [
            EntityTypeField(name="title", type="str", description="Document title", required=True),
            EntityTypeField(name="content", type="str", description="Full text content of the document", required=False),
            EntityTypeField(name="description", type="str", description="Document description or summary", required=False),
            EntityTypeField(name="document_type", type="str", description="Type: contract, proposal, report, manual, policy, specification, guide", required=False),
            EntityTypeField(name="author", type="str", description="Document author", required=False),
            EntityTypeField(name="created_date", type="str", description="Creation date", required=False),
            EntityTypeField(name="last_modified", type="str", description="Last modification date", required=False),
            EntityTypeField(name="version", type="str", description="Document version", required=False),
            EntityTypeField(name="status", type="str", description="Status: draft, review, approved, archived", required=False),
            EntityTypeField(name="file_url", type="str", description="URL to the document file", required=False),
            EntityTypeField(name="preview_url", type="str", description="URL to document preview or thumbnail", required=False),
            EntityTypeField(name="edit_url", type="str", description="URL for editing the document", required=False),
            EntityTypeField(name="tags", type="str", description="Document tags or categories", required=False),
            EntityTypeField(name="access_level", type="str", description="Access level: public, internal, confidential", required=False),
            EntityTypeField(name="related_project", type="str", description="Associated project", required=False),
            EntityTypeField(name="word_count", type="str", description="Approximate word count", required=False),
            EntityTypeField(name="language", type="str", description="Document language", required=False)
        ]
        
        # Create update request
        update_request = UpdateEntityTypeRequest(
            description="A business document or file",
            fields=updated_fields,
            visible_by_default=True
        )
        
        print("\n🔄 Updating Document entity type to include content field...")
        
        # Update the entity type
        updated_type = await entity_type_manager.update_entity_type("Document", update_request)
        
        if updated_type:
            print("✅ Document entity type updated successfully!")
            print(f"\n📋 Updated Document entity type now has {len(updated_type.fields)} fields:")
            for field in updated_type.fields:
                if field.name == "content":
                    print(f"  - {field.name} ({field.type}): {field.description} ✅ NEW!")
                else:
                    print(f"  - {field.name} ({field.type}): {field.description}")
            
            # Test creating a Pydantic model with content
            models = await entity_type_manager.get_pydantic_models(["Document"])
            document_model = models.get("Document")
            
            if document_model:
                print("\n✅ Testing Pydantic model with content field...")
                
                test_doc = document_model(
                    title="Test Document with Content",
                    content="This is the full text content of the document. Now it can be properly searched and analyzed for knowledge management!",
                    document_type="manual",
                    author="System Update",
                    status="approved"
                )
                
                print("✅ Document instance created successfully with content:")
                print(f"  Title: {test_doc.title}")
                print(f"  Content: {test_doc.content}")
                print(f"  Type: {test_doc.document_type}")
                print(f"  Author: {test_doc.author}")
                print(f"  Status: {test_doc.status}")
                
                return True
            else:
                print("❌ Failed to create Pydantic model for updated Document")
                return False
        else:
            print("❌ Failed to update Document entity type!")
            return False
            
    except Exception as e:
        print(f"❌ Error updating Document entity type: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await driver.close()

if __name__ == "__main__":
    success = asyncio.run(update_document_entity_type())
    if success:
        print("\n🎉 Document entity type now properly includes content field for knowledge management!")
    else:
        print("\n💥 Failed to update Document entity type!")
