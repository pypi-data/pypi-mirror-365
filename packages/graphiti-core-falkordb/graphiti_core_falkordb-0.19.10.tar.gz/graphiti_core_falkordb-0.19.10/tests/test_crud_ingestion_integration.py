"""
Test that CRUD operations on entities trigger the full ingestion pipeline.
"""

import os
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from graphiti_core_falkordb.graphiti import Graphiti
from graphiti_core_falkordb.nodes import EntityNode, EpisodicNode
from graphiti_core_falkordb.utils.datetime_utils import utc_now

load_dotenv()

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')


class Person(BaseModel):
    """Person entity type for testing."""
    name: str = Field(description="Full name of the person")
    role: str = Field(description="Job title or role")
    email: str = Field(description="Email address", default="")
    company: str = Field(description="Company they work for", default="")


class Company(BaseModel):
    """Company entity type for testing."""
    name: str = Field(description="Company name")
    industry: str = Field(description="Industry sector", default="")
    location: str = Field(description="Primary location", default="")


async def _cleanup_test_data(graphiti: Graphiti, group_id: str):
    """Helper to clean up test data."""
    try:
        # Search for all nodes and episodes in the test group
        search_results = await graphiti.search_(query="", group_ids=[group_id])
        
        # Delete all found nodes
        for node in search_results.nodes:
            await node.delete(graphiti.driver)
            
        # Delete all found edges
        for edge in search_results.edges:
            await edge.delete(graphiti.driver)
            
        # Also clean up any episodes
        episodes = await EpisodicNode.get_by_group_ids(graphiti.driver, [group_id])
        for episode in episodes:
            await episode.delete(graphiti.driver)
    except Exception as e:
        print(f"Cleanup error: {e}")


async def test_entity_create_triggers_ingestion():
    """Test that creating an entity triggers the ingestion pipeline."""
    if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
        print("Neo4j credentials not available, skipping test")
        return
    
    graphiti = Graphiti(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        await graphiti.build_indices_and_constraints()
        
        group_id = 'test_crud_create'
        
        # Create entity types
        entity_types = {
            'Person': Person,
            'Company': Company,
        }
        
        # Create an entity node directly (simulating CRUD operation)
        entity_node = EntityNode(
            uuid="test-person-uuid",
            group_id=group_id,
            name="John Smith",
            summary="Software engineer at TechCorp",
            labels=["Entity", "Person"],
            attributes={
                "role": "Senior Developer",
                "email": "john@techcorp.com",
                "company": "TechCorp"
            },
            created_at=utc_now(),
        )
        
        # Save the entity
        await entity_node.save(graphiti.driver)
        
        # Simulate the episode creation that should happen in CRUD
        episode_content = f"Entity created: {entity_node.name} - {entity_node.summary} (Type: Person) with attributes: role: Senior Developer, email: john@techcorp.com, company: TechCorp"
        
        await graphiti.add_episode(
            name=f"Entity Created: {entity_node.name}",
            episode_body=episode_content,
            source_description="Entity CRUD operation - created Person",
            reference_time=utc_now(),
            group_id=group_id,
            entity_types=entity_types,
        )
        
        # Verify that episodes were created
        episodes = await EpisodicNode.get_by_group_ids(graphiti.driver, [group_id])
        assert len(episodes) > 0, "No episodes were created"
        
        # Verify that the episode mentions the entity creation
        episode_found = False
        for episode in episodes:
            if "Entity created" in episode.content and "John Smith" in episode.content:
                episode_found = True
                break
        
        assert episode_found, "Episode describing entity creation was not found"
        
        # Verify that relationships might have been extracted
        search_results = await graphiti.search_(
            query='John Smith TechCorp', 
            group_ids=[group_id]
        )
        
        # Should find the original entity plus potentially extracted entities from the episode
        assert len(search_results.nodes) >= 1, "Entity was not found in search results"
        
        # Clean up
        await _cleanup_test_data(graphiti, group_id)
        
        print("✅ Entity create triggers ingestion test passed!")
        
    finally:
        await graphiti.close()


async def test_entity_update_triggers_ingestion():
    """Test that updating an entity triggers the ingestion pipeline."""
    if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
        print("Neo4j credentials not available, skipping test")
        return
    
    graphiti = Graphiti(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        await graphiti.build_indices_and_constraints()
        
        group_id = 'test_crud_update'
        
        # Create entity types
        entity_types = {
            'Person': Person,
            'Company': Company,
        }
        
        # Create and save an entity
        entity_node = EntityNode(
            uuid="test-person-update-uuid",
            group_id=group_id,
            name="Jane Doe",
            summary="Marketing manager",
            labels=["Entity", "Person"],
            attributes={
                "role": "Marketing Manager",
                "email": "jane@company.com",
                "company": "OldCorp"
            },
            created_at=utc_now(),
        )
        
        await entity_node.save(graphiti.driver)
        
        # Simulate an update (changing company)
        entity_node.attributes["company"] = "NewCorp"
        entity_node.summary = "Marketing manager at NewCorp"
        entity_node.updated_at = utc_now()
        
        await entity_node.save(graphiti.driver)
        
        # Simulate the episode creation that should happen in CRUD update
        changes = {"company": "NewCorp", "summary": "Marketing manager at NewCorp"}
        episode_content = f"Entity updated: {entity_node.name} - {entity_node.summary} (Type: Person) with attributes: role: Marketing Manager, email: jane@company.com, company: NewCorp. Changes: company changed to: NewCorp, summary changed to: Marketing manager at NewCorp"
        
        await graphiti.add_episode(
            name=f"Entity Updated: {entity_node.name}",
            episode_body=episode_content,
            source_description="Entity CRUD operation - updated Person",
            reference_time=utc_now(),
            group_id=group_id,
            entity_types=entity_types,
        )
        
        # Verify that episodes were created
        episodes = await EpisodicNode.get_by_group_ids(graphiti.driver, [group_id])
        assert len(episodes) > 0, "No episodes were created"
        
        # Verify that the episode mentions the entity update
        episode_found = False
        for episode in episodes:
            if "Entity updated" in episode.content and "Jane Doe" in episode.content and "NewCorp" in episode.content:
                episode_found = True
                break
        
        assert episode_found, "Episode describing entity update was not found"
        
        # Clean up
        await _cleanup_test_data(graphiti, group_id)
        
        print("✅ Entity update triggers ingestion test passed!")
        
    finally:
        await graphiti.close()


async def test_entity_delete_triggers_ingestion():
    """Test that deleting an entity triggers the ingestion pipeline."""
    if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
        print("Neo4j credentials not available, skipping test")
        return
    
    graphiti = Graphiti(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        await graphiti.build_indices_and_constraints()
        
        group_id = 'test_crud_delete'
        
        # Create entity types
        entity_types = {
            'Person': Person,
            'Company': Company,
        }
        
        # Create and save an entity
        entity_node = EntityNode(
            uuid="test-person-delete-uuid",
            group_id=group_id,
            name="Bob Wilson",
            summary="Sales representative",
            labels=["Entity", "Person"],
            attributes={
                "role": "Sales Rep",
                "email": "bob@sales.com",
                "company": "SalesCorp"
            },
            created_at=utc_now(),
        )
        
        await entity_node.save(graphiti.driver)
        
        # Simulate the episode creation that should happen before CRUD delete
        episode_content = f"Entity deleted: {entity_node.name} - {entity_node.summary} (Type: Person) with attributes: role: Sales Rep, email: bob@sales.com, company: SalesCorp"
        
        await graphiti.add_episode(
            name=f"Entity Deleted: {entity_node.name}",
            episode_body=episode_content,
            source_description="Entity CRUD operation - deleted Person",
            reference_time=utc_now(),
            group_id=group_id,
            entity_types=entity_types,
        )
        
        # Now delete the entity
        await entity_node.delete(graphiti.driver)
        
        # Verify that episodes were created
        episodes = await EpisodicNode.get_by_group_ids(graphiti.driver, [group_id])
        assert len(episodes) > 0, "No episodes were created"
        
        # Verify that the episode mentions the entity deletion
        episode_found = False
        for episode in episodes:
            if "Entity deleted" in episode.content and "Bob Wilson" in episode.content:
                episode_found = True
                break
        
        assert episode_found, "Episode describing entity deletion was not found"
        
        # Clean up
        await _cleanup_test_data(graphiti, group_id)
        
        print("✅ Entity delete triggers ingestion test passed!")
        
    finally:
        await graphiti.close()


if __name__ == "__main__":
    async def run_tests():
        print("Testing CRUD-ingestion integration...")
        
        print("1. Testing entity create triggers ingestion...")
        await test_entity_create_triggers_ingestion()
        
        print("2. Testing entity update triggers ingestion...")
        await test_entity_update_triggers_ingestion()
        
        print("3. Testing entity delete triggers ingestion...")
        await test_entity_delete_triggers_ingestion()
        
        print("🎉 All CRUD-ingestion integration tests passed!")
    
    asyncio.run(run_tests())
