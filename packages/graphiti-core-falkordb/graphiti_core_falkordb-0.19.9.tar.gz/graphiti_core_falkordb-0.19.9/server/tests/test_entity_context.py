"""
Tests for the comprehensive entity context endpoint.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from graph_service.dto import EntityContextResponse, NavigationLinks, NavigationLink
from graph_service.helpers.entity_context import (
    format_comprehensive_context,
    extract_navigation_links,
    get_primary_entity_type,
    extract_key_attributes
)


class TestEntityContextHelpers:
    """Test helper functions for entity context formatting."""
    
    def test_get_primary_entity_type(self):
        """Test extracting primary entity type from labels."""
        labels = ["Entity", "Person", "Customer"]
        assert get_primary_entity_type(labels) == "Person"
        
        labels = ["Entity"]
        assert get_primary_entity_type(labels) == "Entity"
        
        labels = ["Customer", "Entity", "VIP"]
        assert get_primary_entity_type(labels) == "Customer"
    
    def test_extract_key_attributes(self):
        """Test extracting key attributes for display."""
        attributes = {
            "email": "john@example.com",
            "phone": "123-456-7890",
            "random_field": "value",
            "company": "Tech Corp",
            "age": 30
        }
        
        key_attrs = extract_key_attributes(attributes)
        assert "email" in key_attrs
        assert "phone" in key_attrs
        assert "company" in key_attrs
        assert "random_field" not in key_attrs
        assert "age" not in key_attrs
    
    def test_format_comprehensive_context_basic(self):
        """Test basic context formatting."""
        mock_entity = MagicMock()
        mock_entity.uuid = str(uuid4())
        mock_entity.name = "John Doe"
        mock_entity.summary = "Software engineer"
        mock_entity.labels = ["Entity", "Person"]
        mock_entity.attributes = {"email": "john@example.com", "company": "Tech Corp"}
        mock_entity.created_at = datetime.now(timezone.utc)
        
        data = {
            "entity": mock_entity,
            "relationships": {
                "outgoing_1hop": [],
                "incoming_1hop": [],
                "outgoing_2hop": []
            },
            "episodes": [],
            "communities": []
        }
        
        context = format_comprehensive_context(data)
        
        assert "John Doe" in context
        assert "Person" in context
        assert "Software engineer" in context
        assert "email: john@example.com" in context
        assert "company: Tech Corp" in context
        assert "NAVIGATION INSTRUCTIONS" in context
    
    def test_format_comprehensive_context_with_relationships(self):
        """Test context formatting with relationships."""
        mock_entity = MagicMock()
        mock_entity.uuid = str(uuid4())
        mock_entity.name = "John Doe"
        mock_entity.summary = "Software engineer"
        mock_entity.labels = ["Entity", "Person"]
        mock_entity.attributes = {}
        mock_entity.created_at = datetime.now(timezone.utc)
        
        relationships = {
            "outgoing_1hop": [{
                "fact": "John Doe works at Tech Corp",
                "target_uuid": str(uuid4()),
                "target_name": "Tech Corp",
                "target_summary": "Technology company",
                "target_labels": ["Entity", "Company"],
                "target_attributes": {"industry": "Technology"},
                "relationship_type": "works_at",
                "valid_at": datetime.now(timezone.utc),
                "invalid_at": None
            }],
            "incoming_1hop": [],
            "outgoing_2hop": []
        }
        
        data = {
            "entity": mock_entity,
            "relationships": relationships,
            "episodes": [],
            "communities": []
        }
        
        context = format_comprehensive_context(data)
        
        assert "DIRECT RELATIONSHIPS (OUTGOING)" in context
        assert "John Doe works at Tech Corp" in context
        assert "Tech Corp" in context
        assert "Company" in context
    
    def test_extract_navigation_links(self):
        """Test extracting navigation links from context data."""
        relationships = {
            "outgoing_1hop": [{
                "target_uuid": "target-uuid-1",
                "target_name": "Tech Corp",
                "target_labels": ["Entity", "Company"],
                "fact": "John works at Tech Corp"
            }],
            "incoming_1hop": [{
                "source_uuid": "source-uuid-1",
                "source_name": "Engineering Team",
                "source_labels": ["Entity", "Team"],
                "fact": "Engineering Team includes John"
            }],
            "outgoing_2hop": [{
                "intermediate_uuid": "intermediate-uuid",
                "intermediate_entity": "Tech Corp",
                "target_uuid": "target-uuid-2",
                "target_name": "San Francisco",
                "target_labels": ["Entity", "Location"],
                "path": "John -> Tech Corp -> San Francisco"
            }]
        }
        
        episodes = [{
            "episode_uuid": "episode-uuid-1",
            "episode_name": "Meeting Notes"
        }]
        
        communities = [{
            "community_uuid": "community-uuid-1",
            "community_name": "Engineering Community"
        }]
        
        data = {
            "entity": MagicMock(),
            "relationships": relationships,
            "episodes": episodes,
            "communities": communities
        }
        
        links = extract_navigation_links(data)
        
        assert isinstance(links, NavigationLinks)
        assert len(links.direct_entities) == 2  # outgoing + incoming
        assert len(links.extended_entities) == 2  # intermediate + target
        assert len(links.episodes) == 1
        assert len(links.communities) == 1
        
        # Check direct entities
        direct_uuids = [link.uuid for link in links.direct_entities]
        assert "target-uuid-1" in direct_uuids
        assert "source-uuid-1" in direct_uuids
        
        # Check extended entities
        extended_uuids = [link.uuid for link in links.extended_entities]
        assert "intermediate-uuid" in extended_uuids
        assert "target-uuid-2" in extended_uuids


class TestEntityContextResponse:
    """Test EntityContextResponse model."""
    
    def test_entity_context_response_creation(self):
        """Test creating an EntityContextResponse."""
        navigation_links = NavigationLinks(
            direct_entities=[
                NavigationLink(uuid="uuid1", name="Entity 1", type="Person")
            ],
            extended_entities=[],
            episodes=[],
            communities=[]
        )
        
        response = EntityContextResponse(
            entity_uuid="main-uuid",
            entity_name="John Doe",
            context="Formatted context string",
            navigation_links=navigation_links,
            raw_data={"entity": {"name": "John Doe"}}
        )
        
        assert response.entity_uuid == "main-uuid"
        assert response.entity_name == "John Doe"
        assert response.context == "Formatted context string"
        assert len(response.navigation_links.direct_entities) == 1
        assert response.navigation_links.direct_entities[0].name == "Entity 1"


class TestEntityContextAPI:
    """Test the entity context API endpoint (integration-style tests)."""
    
    @patch('graph_service.routers.retrieve.EntityNode.get_by_uuid')
    def test_entity_context_endpoint_structure(self, mock_get_by_uuid):
        """Test that the endpoint has the correct structure."""
        # This is a structural test - we're testing the endpoint exists
        # and has the right parameters without actually calling it
        
        from graph_service.routers.retrieve import get_entity_context
        import inspect
        
        # Check function signature
        sig = inspect.signature(get_entity_context)
        params = list(sig.parameters.keys())
        
        expected_params = [
            'uuid', 'graphiti', 'max_relationships', 
            'relationship_depth', 'include_episodes', 'include_communities'
        ]
        
        for param in expected_params:
            assert param in params, f"Missing parameter: {param}"
    
    def test_navigation_link_model(self):
        """Test NavigationLink model validation."""
        # Test required fields
        link = NavigationLink(uuid="test-uuid", name="Test Entity", type="Person")
        assert link.uuid == "test-uuid"
        assert link.name == "Test Entity"
        assert link.type == "Person"
        assert link.relationship is None
        assert link.path is None
        
        # Test optional fields
        link_with_optional = NavigationLink(
            uuid="test-uuid",
            name="Test Entity", 
            type="Person",
            relationship="works at",
            path="A -> B -> C"
        )
        assert link_with_optional.relationship == "works at"
        assert link_with_optional.path == "A -> B -> C"


if __name__ == "__main__":
    # Run basic tests
    test_helpers = TestEntityContextHelpers()
    test_helpers.test_get_primary_entity_type()
    test_helpers.test_extract_key_attributes()
    print("✅ All helper function tests passed!")
    
    test_response = TestEntityContextResponse()
    test_response.test_entity_context_response_creation()
    print("✅ Response model tests passed!")
    
    test_api = TestEntityContextAPI()
    test_api.test_entity_context_endpoint_structure()
    test_api.test_navigation_link_model()
    print("✅ API structure tests passed!")
    
    print("🎉 All tests completed successfully!")
