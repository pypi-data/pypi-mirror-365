from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from graph_service.dto.common import Message
from graph_service.dto.retrieve import EpisodeSource


class AddMessagesRequest(BaseModel):
    group_id: str = Field(..., description='The group id of the messages to add')
    messages: list[Message] = Field(..., description='The messages to add')


class AddEntityNodeRequest(BaseModel):
    uuid: str = Field(..., description='The uuid of the node to add')
    group_id: str = Field(..., description='The group id of the node to add')
    name: str = Field(..., description='The name of the node to add')
    summary: str = Field(default='', description='The summary of the node to add')


class CreateEntityRequest(BaseModel):
    """Request model for creating a new entity with entity type support."""
    group_id: str = Field(..., description='The group id for the entity')
    name: str = Field(..., description='The name of the entity')
    entity_type: str = Field(..., description='The entity type name (e.g., Customer, Project, Task)')
    summary: Optional[str] = Field(None, description='Optional summary of the entity')
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict, description='Entity attributes based on entity type schema')
    extra_attributes: Optional[Dict[str, Any]] = Field(default_factory=dict, description='Additional attributes not defined in entity type schema')


class UpdateEntityRequest(BaseModel):
    """Request model for updating an existing entity."""
    name: Optional[str] = Field(None, description='Updated name of the entity')
    summary: Optional[str] = Field(None, description='Updated summary of the entity')
    attributes: Optional[Dict[str, Any]] = Field(None, description='Updated entity attributes')
    extra_attributes: Optional[Dict[str, Any]] = Field(None, description='Updated additional attributes not defined in entity type schema')


class EntityResponse(BaseModel):
    """Response model for entity operations."""
    uuid: str = Field(..., description='Entity UUID')
    group_id: str = Field(..., description='Group ID')
    name: str = Field(..., description='Entity name')
    summary: str = Field(..., description='Entity summary')
    attributes: Dict[str, Any] = Field(..., description='Entity attributes (merged with extra_attributes for backward compatibility)')
    extra_attributes: Optional[Dict[str, Any]] = Field(default_factory=dict, description='Additional attributes not defined in entity type schema')
    labels: list[str] = Field(..., description='Entity labels/types')
    created_at: str = Field(..., description='Creation timestamp')
    updated_at: Optional[str] = Field(None, description='Last update timestamp')
    episode_sources: list[EpisodeSource] = Field(default_factory=list, description='Sources from related episodes')
