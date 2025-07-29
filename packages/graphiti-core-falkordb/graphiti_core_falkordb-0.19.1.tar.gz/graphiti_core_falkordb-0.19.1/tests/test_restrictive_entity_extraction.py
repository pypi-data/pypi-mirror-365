"""
Test restrictive entity extraction to ensure only concrete, business-relevant entities are extracted.
"""

import os
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from graphiti_core_falkordb.graphiti import Graphiti

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


async def _cleanup_test_nodes(graphiti: Graphiti, group_id: str):
    """Helper to clean up test nodes."""
    try:
        # Search for all nodes in the test group
        search_results = await graphiti.search_(query="", group_ids=[group_id])
        
        # Delete all found nodes
        for node in search_results.nodes:
            await node.delete(graphiti.driver)
            
        # Also delete any edges
        for edge in search_results.edges:
            await edge.delete(graphiti.driver)
    except Exception as e:
        print(f"Cleanup error: {e}")


async def test_hypothetical_speakers_not_extracted():
    """Test that hypothetical speakers like 'Speaker A' and 'Speaker B' are not extracted."""
    if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
        print("Neo4j credentials not available, skipping test")
        return
    
    graphiti = Graphiti(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        await graphiti.build_indices_and_constraints()
        
        entity_types = {
            'Person': Person,
            'Company': Company,
        }
        
        # Test content with hypothetical speakers
        episode_content = """
        Speaker A: I think we should consider the new project proposal from TechCorp.
        Speaker B: Yes, I agree. John Smith from TechCorp presented it well.
        Speaker A: Should we schedule a follow-up meeting?
        Speaker B: Definitely. Let's also invite Sarah Johnson from our team.
        """
        
        result = await graphiti.add_episode(
            name='Hypothetical Speaker Test',
            episode_body=episode_content,
            source_description='Meeting transcript with hypothetical speakers',
            reference_time=datetime.now(timezone.utc),
            entity_types=entity_types,
            group_id='test_hypothetical_speakers',
        )
        
        assert result is not None
        
        # Search for entities
        search_results = await graphiti.search_(
            query='Speaker TechCorp John Smith Sarah Johnson', 
            group_ids=['test_hypothetical_speakers']
        )
        
        # Check that hypothetical speakers were NOT extracted
        found_names = [node.name for node in search_results.nodes]
        
        # Should NOT find hypothetical speakers
        assert 'Speaker A' not in found_names, "Speaker A should not be extracted"
        assert 'Speaker B' not in found_names, "Speaker B should not be extracted"
        
        # Should find concrete entities
        assert any('John Smith' in name for name in found_names), "John Smith should be extracted"
        assert any('Sarah Johnson' in name for name in found_names), "Sarah Johnson should be extracted"
        assert any('TechCorp' in name for name in found_names), "TechCorp should be extracted"
        
        # Clean up
        await _cleanup_test_nodes(graphiti, 'test_hypothetical_speakers')
        
    finally:
        await graphiti.close()


async def test_generic_roles_not_extracted():
    """Test that generic roles without names are not extracted."""
    if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
        print("Neo4j credentials not available, skipping test")
        return
    
    graphiti = Graphiti(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        await graphiti.build_indices_and_constraints()
        
        entity_types = {
            'Person': Person,
            'Company': Company,
        }
        
        # Test content with generic roles
        episode_content = """
        The manager discussed the project with the developer.
        A customer called about the new product from Microsoft.
        The CEO of Apple announced new features.
        """
        
        result = await graphiti.add_episode(
            name='Generic Roles Test',
            episode_body=episode_content,
            source_description='Text with generic roles',
            reference_time=datetime.now(timezone.utc),
            entity_types=entity_types,
            group_id='test_generic_roles',
        )
        
        assert result is not None
        
        # Search for entities
        search_results = await graphiti.search_(
            query='manager developer customer CEO Microsoft Apple', 
            group_ids=['test_generic_roles']
        )
        
        found_names = [node.name for node in search_results.nodes]
        
        # Should NOT find generic roles
        assert 'manager' not in [name.lower() for name in found_names], "Generic 'manager' should not be extracted"
        assert 'developer' not in [name.lower() for name in found_names], "Generic 'developer' should not be extracted"
        assert 'customer' not in [name.lower() for name in found_names], "Generic 'customer' should not be extracted"
        assert 'CEO' not in found_names, "Generic 'CEO' should not be extracted"
        
        # Should find concrete company names
        assert any('Microsoft' in name for name in found_names), "Microsoft should be extracted"
        assert any('Apple' in name for name in found_names), "Apple should be extracted"
        
        # Clean up
        await _cleanup_test_nodes(graphiti, 'test_generic_roles')
        
    finally:
        await graphiti.close()


async def test_concrete_entities_still_extracted():
    """Test that concrete, business-relevant entities are still properly extracted."""
    if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
        print("Neo4j credentials not available, skipping test")
        return
    
    graphiti = Graphiti(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        await graphiti.build_indices_and_constraints()
        
        entity_types = {
            'Person': Person,
            'Company': Company,
        }
        
        # Test content with concrete entities
        episode_content = """
        John Smith from Acme Corporation called about the Q4 project.
        Sarah Johnson will be leading the initiative with Microsoft.
        The contract with Google needs to be reviewed by Alice Brown.
        """
        
        result = await graphiti.add_episode(
            name='Concrete Entities Test',
            episode_body=episode_content,
            source_description='Business communication with concrete entities',
            reference_time=datetime.now(timezone.utc),
            entity_types=entity_types,
            group_id='test_concrete_entities',
        )
        
        assert result is not None
        
        # Search for entities
        search_results = await graphiti.search_(
            query='John Smith Sarah Johnson Alice Brown Acme Corporation Microsoft Google', 
            group_ids=['test_concrete_entities']
        )
        
        found_names = [node.name for node in search_results.nodes]
        
        # Should find all concrete entities
        assert any('John Smith' in name for name in found_names), "John Smith should be extracted"
        assert any('Sarah Johnson' in name for name in found_names), "Sarah Johnson should be extracted"
        assert any('Alice Brown' in name for name in found_names), "Alice Brown should be extracted"
        assert any('Acme Corporation' in name for name in found_names), "Acme Corporation should be extracted"
        assert any('Microsoft' in name for name in found_names), "Microsoft should be extracted"
        assert any('Google' in name for name in found_names), "Google should be extracted"
        
        # Clean up
        await _cleanup_test_nodes(graphiti, 'test_concrete_entities')
        
    finally:
        await graphiti.close()


if __name__ == "__main__":
    import asyncio
    
    async def run_tests():
        print("Testing restrictive entity extraction...")
        
        print("1. Testing hypothetical speakers...")
        await test_hypothetical_speakers_not_extracted()
        print("✅ Hypothetical speakers test passed!")
        
        print("2. Testing generic roles...")
        await test_generic_roles_not_extracted()
        print("✅ Generic roles test passed!")
        
        print("3. Testing concrete entities...")
        await test_concrete_entities_still_extracted()
        print("✅ Concrete entities test passed!")
        
        print("🎉 All restrictive entity extraction tests passed!")
    
    asyncio.run(run_tests())
