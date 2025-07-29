"""
Integration tests for entity pagination and sorting API endpoints.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from graph_service.main import app
from graph_service.dto import EntitySortField, SortOrder


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_entities():
    """Create mock entities for testing."""
    base_time = datetime.now(timezone.utc)
    entities = []
    
    for i in range(25):  # Create 25 entities for pagination testing
        entity_data = {
            'uuid': str(uuid4()),
            'name': f'Entity {i:02d}',
            'group_id': 'test_group',
            'created_at': base_time.replace(minute=i),  # Different creation times
            'summary': f'Summary for entity {i}',
            'labels': ['Entity', 'TestType'],
            'attributes': {
                'age': 20 + i,
                'department': f'Dept_{i % 3}',  # Cycle through 3 departments
                'score': 100 - i,  # Descending scores
            }
        }
        entities.append(entity_data)
    
    return entities


class TestEntityPaginationEndpoints:
    """Test entity pagination API endpoints."""
    
    @patch('graph_service.routers.retrieve.EntityNode.get_paginated_by_group_ids')
    @patch('graph_service.zep_graphiti.ZepGraphiti')
    def test_get_entities_paginated_basic(self, mock_graphiti, mock_get_paginated, client, mock_entities):
        """Test basic pagination endpoint."""
        # Setup mocks
        mock_graphiti_instance = AsyncMock()
        mock_graphiti.return_value = mock_graphiti_instance
        
        # Return first 10 entities
        page_entities = mock_entities[:10]
        mock_entity_nodes = []
        
        for entity_data in page_entities:
            mock_node = AsyncMock()
            mock_node.uuid = entity_data['uuid']
            mock_node.name = entity_data['name']
            mock_node.summary = entity_data['summary']
            mock_node.attributes = entity_data['attributes']
            mock_node.labels = entity_data['labels']
            mock_node.created_at = entity_data['created_at']
            mock_entity_nodes.append(mock_node)
        
        mock_get_paginated.return_value = (mock_entity_nodes, True, 25)  # has_next=True, total=25
        
        # Make request
        response = client.get("/entities/test_group/paginated?page=1&page_size=10")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "entities" in data
        assert "pagination" in data
        assert "total_count" in data
        
        # Check pagination metadata
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 10
        assert pagination["has_next"] is True
        assert pagination["has_previous"] is False
        assert pagination["count"] == 10
        
        # Check total count
        assert data["total_count"] == 25
        
        # Check entities
        assert len(data["entities"]) == 10
        assert data["entities"][0]["name"] == "Entity 00"
    
    @patch('graph_service.routers.retrieve.EntityNode.get_paginated_by_group_ids')
    @patch('graph_service.zep_graphiti.ZepGraphiti')
    def test_get_entities_paginated_with_sorting(self, mock_graphiti, mock_get_paginated, client, mock_entities):
        """Test pagination with custom sorting."""
        mock_graphiti_instance = AsyncMock()
        mock_graphiti.return_value = mock_graphiti_instance
        
        # Sort entities by name ascending for this test
        sorted_entities = sorted(mock_entities, key=lambda x: x['name'])
        page_entities = sorted_entities[:5]
        
        mock_entity_nodes = []
        for entity_data in page_entities:
            mock_node = AsyncMock()
            mock_node.uuid = entity_data['uuid']
            mock_node.name = entity_data['name']
            mock_node.summary = entity_data['summary']
            mock_node.attributes = entity_data['attributes']
            mock_node.labels = entity_data['labels']
            mock_node.created_at = entity_data['created_at']
            mock_entity_nodes.append(mock_node)
        
        mock_get_paginated.return_value = (mock_entity_nodes, True, 25)
        
        # Make request with sorting
        response = client.get(
            "/entities/test_group/paginated"
            "?page=1&page_size=5&sort_by=name&sort_order=asc"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the mock was called with correct parameters
        mock_get_paginated.assert_called_once()
        call_args = mock_get_paginated.call_args
        assert call_args[1]['sort_by'] == 'name'
        assert call_args[1]['sort_order'] == 'asc'
        assert call_args[1]['page'] == 1
        assert call_args[1]['page_size'] == 5
    
    @patch('graph_service.routers.retrieve.EntityNode.get_paginated_by_group_ids')
    @patch('graph_service.zep_graphiti.ZepGraphiti')
    def test_get_entities_paginated_with_attribute_sorting(self, mock_graphiti, mock_get_paginated, client, mock_entities):
        """Test pagination with custom attribute sorting."""
        mock_graphiti_instance = AsyncMock()
        mock_graphiti.return_value = mock_graphiti_instance
        
        # Sort by age attribute
        sorted_entities = sorted(mock_entities, key=lambda x: x['attributes']['age'], reverse=True)
        page_entities = sorted_entities[:5]
        
        mock_entity_nodes = []
        for entity_data in page_entities:
            mock_node = AsyncMock()
            mock_node.uuid = entity_data['uuid']
            mock_node.name = entity_data['name']
            mock_node.summary = entity_data['summary']
            mock_node.attributes = entity_data['attributes']
            mock_node.labels = entity_data['labels']
            mock_node.created_at = entity_data['created_at']
            mock_entity_nodes.append(mock_node)
        
        mock_get_paginated.return_value = (mock_entity_nodes, False, 5)
        
        # Make request with attribute sorting
        response = client.get(
            "/entities/test_group/paginated"
            "?page=1&page_size=5&attribute_sort_field=age&sort_order=desc"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the mock was called with correct parameters
        mock_get_paginated.assert_called_once()
        call_args = mock_get_paginated.call_args
        assert call_args[1]['attribute_sort_field'] == 'age'
        assert call_args[1]['sort_order'] == 'desc'
    
    @patch('graph_service.routers.retrieve.EntityNode.get_available_sort_fields')
    @patch('graph_service.zep_graphiti.ZepGraphiti')
    def test_get_entity_sort_fields(self, mock_graphiti, mock_get_sort_fields, client):
        """Test getting available sort fields."""
        mock_graphiti_instance = AsyncMock()
        mock_graphiti.return_value = mock_graphiti_instance
        
        mock_get_sort_fields.return_value = {
            "standard_fields": ["name", "created_at", "summary", "uuid"],
            "attribute_fields": ["age", "department", "score"]
        }
        
        response = client.get("/entities/test_group/sort-fields")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "group_id" in data
        assert "sort_fields" in data
        assert "description" in data
        
        assert data["group_id"] == "test_group"
        assert "standard_fields" in data["sort_fields"]
        assert "attribute_fields" in data["sort_fields"]
        assert "age" in data["sort_fields"]["attribute_fields"]
        assert "name" in data["sort_fields"]["standard_fields"]
    
    def test_pagination_parameter_validation(self, client):
        """Test parameter validation for pagination endpoint."""
        # Test invalid page number
        response = client.get("/entities/test_group/paginated?page=0")
        assert response.status_code == 422  # Validation error
        
        # Test invalid page size
        response = client.get("/entities/test_group/paginated?page_size=101")
        assert response.status_code == 422  # Validation error
        
        # Test invalid sort order
        response = client.get("/entities/test_group/paginated?sort_order=invalid")
        assert response.status_code == 422  # Validation error
    
    @patch('graph_service.routers.retrieve.EntityNode.get_paginated_by_group_ids')
    @patch('graph_service.zep_graphiti.ZepGraphiti')
    def test_cursor_based_pagination(self, mock_graphiti, mock_get_paginated, client, mock_entities):
        """Test cursor-based pagination."""
        mock_graphiti_instance = AsyncMock()
        mock_graphiti.return_value = mock_graphiti_instance
        
        # Simulate second page with cursor
        page_entities = mock_entities[10:20]
        mock_entity_nodes = []
        
        for entity_data in page_entities:
            mock_node = AsyncMock()
            mock_node.uuid = entity_data['uuid']
            mock_node.name = entity_data['name']
            mock_node.summary = entity_data['summary']
            mock_node.attributes = entity_data['attributes']
            mock_node.labels = entity_data['labels']
            mock_node.created_at = entity_data['created_at']
            mock_entity_nodes.append(mock_node)
        
        mock_get_paginated.return_value = (mock_entity_nodes, True, 25)
        
        cursor_uuid = str(uuid4())
        response = client.get(f"/entities/test_group/paginated?cursor={cursor_uuid}&page_size=10")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify cursor was passed to the method
        mock_get_paginated.assert_called_once()
        call_args = mock_get_paginated.call_args
        assert call_args[1]['cursor'] == cursor_uuid
    
    @patch('graph_service.routers.retrieve.EntityNode.get_paginated_by_group_ids')
    @patch('graph_service.zep_graphiti.ZepGraphiti')
    def test_empty_results(self, mock_graphiti, mock_get_paginated, client):
        """Test handling of empty results."""
        mock_graphiti_instance = AsyncMock()
        mock_graphiti.return_value = mock_graphiti_instance
        
        mock_get_paginated.return_value = ([], False, 0)  # No entities
        
        response = client.get("/entities/empty_group/paginated")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["entities"] == []
        assert data["pagination"]["count"] == 0
        assert data["pagination"]["has_next"] is False
        assert data["pagination"]["has_previous"] is False
        assert data["total_count"] == 0
