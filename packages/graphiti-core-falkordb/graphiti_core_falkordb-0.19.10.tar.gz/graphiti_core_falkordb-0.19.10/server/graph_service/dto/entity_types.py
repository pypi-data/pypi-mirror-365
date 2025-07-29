"""
Entity Types DTOs
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from .common import Message


class EntityTypeField(BaseModel):
    """Field definition for an entity type."""

    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Field type (str, int, float, bool, list, dict)")
    description: str = Field(..., description="Field description")
    default: Optional[str] = Field(None, description="Default value")
    required: bool = Field(True, description="Whether the field is required")


class EntityTypeSchema(BaseModel):
    """Schema definition for an entity type."""
    
    name: str = Field(..., description="Entity type name")
    description: Optional[str] = Field(None, description="Entity type description")
    fields: List[EntityTypeField] = Field(..., description="List of fields")


class RegisterEntityTypeRequest(BaseModel):
    """Request model for registering a new entity type."""

    name: str = Field(..., description="Entity type name")
    description: Optional[str] = Field(None, description="Entity type description")
    fields: List[EntityTypeField] = Field(..., description="List of fields")
    visible_by_default: bool = Field(True, description="Whether this entity type should be visible by default in UI")


class UpdateEntityTypeRequest(BaseModel):
    """Request model for updating an entity type."""

    description: Optional[str] = Field(None, description="Updated entity type description")
    fields: Optional[List[EntityTypeField]] = Field(None, description="Updated list of fields")
    visible_by_default: Optional[bool] = Field(None, description="Updated visibility setting")


class EntityTypeResponse(BaseModel):
    """Response model for entity type operations."""

    name: str = Field(..., description="Entity type name")
    description: Optional[str] = Field(None, description="Entity type description")
    fields: List[EntityTypeField] = Field(..., description="List of fields")
    visible_by_default: bool = Field(True, description="Whether this entity type should be visible by default in UI")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    json_schema: dict = Field(..., description="JSON schema representation")


class EntityTypeListResponse(BaseModel):
    """Response model for listing entity types."""
    
    entity_types: List[EntityTypeResponse] = Field(..., description="List of entity types")
    total: int = Field(..., description="Total number of entity types")


class AddMessagesWithEntityTypesRequest(BaseModel):
    """Extended request model for adding messages with entity types."""

    group_id: str = Field(..., description="The group id of the messages to add")
    messages: List[Message] = Field(..., description="The messages to add")
    entity_type_names: Optional[List[str]] = Field(None, description="Names of entity types to use")
    excluded_entity_types: Optional[List[str]] = Field(None, description="Names of entity types to exclude")
    auto_discover_entities: bool = Field(True, description="Whether to automatically discover and register new entity types from the message content")
