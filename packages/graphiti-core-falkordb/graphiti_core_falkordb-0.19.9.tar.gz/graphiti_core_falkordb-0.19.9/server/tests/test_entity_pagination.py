"""
Tests for entity pagination and sorting functionality.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from graph_service.dto import (
    PaginationParams,
    SortParams,
    EntityResult,
    PaginatedEntityResponse,
    SortOrder,
    EntitySortField,
)
from graphiti_core_falkordb.nodes import EntityNode


class TestPaginationParams:
    """Test pagination parameter validation."""
    
    def test_valid_pagination_params(self):
        """Test valid pagination parameters."""
        params = PaginationParams(page=1, page_size=20)
        assert params.page == 1
        assert params.page_size == 20
        assert params.cursor is None
    
    def test_pagination_params_with_cursor(self):
        """Test pagination parameters with cursor."""
        cursor_uuid = str(uuid4())
        params = PaginationParams(page=2, page_size=10, cursor=cursor_uuid)
        assert params.cursor == cursor_uuid
    
    def test_invalid_page_number(self):
        """Test invalid page number validation."""
        with pytest.raises(ValueError):
            PaginationParams(page=0, page_size=20)
    
    def test_invalid_page_size(self):
        """Test invalid page size validation."""
        with pytest.raises(ValueError):
            PaginationParams(page=1, page_size=0)
        
        with pytest.raises(ValueError):
            PaginationParams(page=1, page_size=101)  # Max is 100


class TestSortParams:
    """Test sorting parameter validation."""
    
    def test_valid_sort_params(self):
        """Test valid sorting parameters."""
        params = SortParams(sort_by=EntitySortField.NAME, sort_order=SortOrder.ASC)
        assert params.sort_by == EntitySortField.NAME
        assert params.sort_order == SortOrder.ASC
        assert params.attribute_sort_field is None
    
    def test_sort_params_with_attribute_field(self):
        """Test sorting parameters with custom attribute field."""
        params = SortParams(
            sort_by=EntitySortField.NAME,
            sort_order=SortOrder.DESC,
            attribute_sort_field="custom_field"
        )
        assert params.attribute_sort_field == "custom_field"
    
    def test_empty_attribute_sort_field_becomes_none(self):
        """Test that empty string attribute_sort_field becomes None."""
        params = SortParams(attribute_sort_field="")
        assert params.attribute_sort_field is None
        
        params = SortParams(attribute_sort_field="   ")
        assert params.attribute_sort_field is None


class TestEntityResult:
    """Test EntityResult model."""
    
    def test_entity_result_creation(self):
        """Test creating an EntityResult."""
        now = datetime.now(timezone.utc)
        entity = EntityResult(
            uuid=str(uuid4()),
            name="Test Entity",
            summary="Test summary",
            attributes={"schema_field": "value"},
            extra_attributes={"custom_field": "custom_value"},
            labels=["Entity", "Person"],
            created_at=now,
        )
        
        assert entity.name == "Test Entity"
        assert entity.summary == "Test summary"
        assert entity.attributes["schema_field"] == "value"
        assert entity.extra_attributes["custom_field"] == "custom_value"
        assert "Person" in entity.labels


class TestPaginatedEntityResponse:
    """Test PaginatedEntityResponse model."""
    
    def test_create_paginated_response(self):
        """Test creating a paginated response."""
        entities = [
            EntityResult(
                uuid=str(uuid4()),
                name=f"Entity {i}",
                summary=f"Summary {i}",
                attributes={},
                extra_attributes={},
                labels=["Entity"],
                created_at=datetime.now(timezone.utc),
            )
            for i in range(3)
        ]
        
        response = PaginatedEntityResponse.create(
            entities=entities,
            page=1,
            page_size=10,
            has_next=False,
            has_previous=False,
            total_count=3,
        )
        
        assert len(response.entities) == 3
        assert response.pagination["page"] == 1
        assert response.pagination["page_size"] == 10
        assert response.pagination["has_next"] is False
        assert response.pagination["has_previous"] is False
        assert response.pagination["count"] == 3
        assert response.total_count == 3
    
    def test_paginated_response_with_cursors(self):
        """Test paginated response with navigation cursors."""
        entities = [
            EntityResult(
                uuid=str(uuid4()),
                name="Entity 1",
                summary="Summary 1",
                attributes={},
                labels=["Entity"],
                created_at=datetime.now(timezone.utc),
            )
        ]
        
        next_cursor = str(uuid4())
        prev_cursor = str(uuid4())
        
        response = PaginatedEntityResponse.create(
            entities=entities,
            page=2,
            page_size=1,
            has_next=True,
            has_previous=True,
            next_cursor=next_cursor,
            previous_cursor=prev_cursor,
        )
        
        assert response.pagination["next_cursor"] == next_cursor
        assert response.pagination["previous_cursor"] == prev_cursor
        assert response.pagination["has_next"] is True
        assert response.pagination["has_previous"] is True


@pytest.fixture
def mock_entity_node():
    """Create a mock EntityNode for testing."""
    entity = EntityNode(
        uuid=str(uuid4()),
        name="Test Entity",
        group_id="test_group",
        summary="Test summary",
        attributes={"custom_field": "value", "age": 25},
        labels=["Entity", "Person"],
        created_at=datetime.now(timezone.utc),
    )
    return entity


class TestEntityNodePagination:
    """Test EntityNode pagination methods."""
    
    @pytest.mark.asyncio
    async def test_get_paginated_by_group_ids_basic(self, mock_entity_node):
        """Test basic pagination functionality."""
        # Mock driver
        mock_driver = AsyncMock()
        mock_driver.execute_query.side_effect = [
            # Main query result
            ([{
                'uuid': mock_entity_node.uuid,
                'name': mock_entity_node.name,
                'group_id': mock_entity_node.group_id,
                'created_at': mock_entity_node.created_at,
                'summary': mock_entity_node.summary,
                'labels': mock_entity_node.labels,
                'attributes': mock_entity_node.attributes,
            }], None, None),
            # Count query result
            ([{'total': 1}], None, None),
        ]
        
        entities, has_next, total_count = await EntityNode.get_paginated_by_group_ids(
            driver=mock_driver,
            group_ids=["test_group"],
            page=1,
            page_size=10,
        )
        
        assert len(entities) == 1
        assert entities[0].name == "Test Entity"
        assert has_next is False
        assert total_count == 1
        
        # Verify driver was called correctly
        assert mock_driver.execute_query.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_available_sort_fields(self):
        """Test getting available sort fields."""
        mock_driver = AsyncMock()
        mock_driver.execute_query.return_value = (
            [{'attribute_fields': ['custom_field', 'age', 'department']}],
            None,
            None
        )
        
        sort_fields = await EntityNode.get_available_sort_fields(
            driver=mock_driver,
            group_ids=["test_group"],
        )
        
        assert "standard_fields" in sort_fields
        assert "attribute_fields" in sort_fields
        assert "name" in sort_fields["standard_fields"]
        assert "created_at" in sort_fields["standard_fields"]
        assert "age" in sort_fields["attribute_fields"]
        assert "custom_field" in sort_fields["attribute_fields"]
        assert "department" in sort_fields["attribute_fields"]


class TestEntityPaginationAPI:
    """Test the API endpoints for entity pagination."""
    
    def test_pagination_query_params_validation(self):
        """Test that query parameters are properly validated."""
        # This would be tested with a real TestClient in integration tests
        # For now, we test the parameter models directly
        
        # Valid parameters
        params = PaginationParams(page=1, page_size=20)
        assert params.page == 1
        assert params.page_size == 20
        
        # Test sort parameters
        sort_params = SortParams(
            sort_by=EntitySortField.NAME,
            sort_order=SortOrder.ASC,
            attribute_sort_field="custom_field"
        )
        assert sort_params.sort_by == EntitySortField.NAME
        assert sort_params.sort_order == SortOrder.ASC
        assert sort_params.attribute_sort_field == "custom_field"
