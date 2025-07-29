import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, validator

from graph_service.dto.common import Message


def extract_source_url_from_description(source_description: str) -> tuple[str, Optional[str]]:
    """
    Extract source URL from enhanced source description.

    Returns:
        tuple: (clean_description, extracted_url)
    """
    if not source_description:
        return source_description, None

    # Pattern to match " | Source URL: {url}" at the end or middle of the description
    url_pattern = r'\s*\|\s*Source URL:\s*([^\|]+?)(?:\s*\|\s*|$)'
    match = re.search(url_pattern, source_description)

    if match:
        url = match.group(1).strip()
        # Remove the URL part from the description
        clean_description = re.sub(url_pattern, '', source_description).strip()
        return clean_description, url

    return source_description, None


class SearchQuery(BaseModel):
    group_ids: list[str] | None = Field(
        None, description='The group ids for the memories to search'
    )
    query: str
    max_facts: int = Field(default=10, description='The maximum number of facts to retrieve')


class FactResult(BaseModel):
    uuid: str
    name: str
    fact: str
    valid_at: datetime | None
    invalid_at: datetime | None
    created_at: datetime
    expired_at: datetime | None

    class Config:
        json_encoders = {datetime: lambda v: v.astimezone(timezone.utc).isoformat()}


class SearchResults(BaseModel):
    facts: list[FactResult]


class GetMemoryRequest(BaseModel):
    group_id: str = Field(..., description='The group id of the memory to get')
    max_facts: int = Field(default=10, description='The maximum number of facts to retrieve')
    center_node_uuid: str | None = Field(
        ..., description='The uuid of the node to center the retrieval on'
    )
    messages: list[Message] = Field(
        ..., description='The messages to build the retrieval query from '
    )


class GetMemoryResponse(BaseModel):
    facts: list[FactResult] = Field(..., description='The facts that were retrieved from the graph')


class SortOrder(str, Enum):
    """Sort order enumeration."""
    ASC = "asc"
    DESC = "desc"


class EntitySortField(str, Enum):
    """Available fields for sorting entities."""
    NAME = "name"
    CREATED_AT = "created_at"
    SUMMARY = "summary"
    UUID = "uuid"


class PaginationParams(BaseModel):
    """Pagination parameters for entity queries."""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of items per page (max 100)")
    cursor: Optional[str] = Field(default=None, description="Cursor for cursor-based pagination (entity UUID)")
    visible_only: Optional[bool] = Field(default=None, description="Filter by visibility (True=only visible entities, False=only hidden entities, None=all entities)")
    entity_type: Optional[str] = Field(default=None, description="Filter by entity type name")


class SortParams(BaseModel):
    """Sorting parameters for entity queries."""
    sort_by: EntitySortField = Field(default=EntitySortField.CREATED_AT, description="Field to sort by")
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")
    attribute_sort_field: Optional[str] = Field(default=None, description="Custom attribute field to sort by (overrides sort_by)")

    @validator('attribute_sort_field')
    def validate_attribute_sort_field(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v


class EpisodeSource(BaseModel):
    """Episode source information."""
    source: str = Field(description="Episode source type (message, json, text)")
    source_description: str = Field(description="Description of the data source")
    source_url: Optional[str] = Field(default=None, description="URL or file path of the source document/file")
    episode_uuid: str = Field(description="UUID of the episode")
    episode_name: str = Field(description="Name of the episode")
    created_at: datetime = Field(description="When the episode was created")
    valid_at: datetime = Field(description="When the episode content was valid")

    class Config:
        json_encoders = {datetime: lambda v: v.astimezone(timezone.utc).isoformat()}


class EntityResult(BaseModel):
    """Entity result model for paginated responses."""
    uuid: str
    name: str
    summary: str
    attributes: dict[str, Any]
    extra_attributes: dict[str, Any] = Field(default_factory=dict, description="Custom fields and additional attributes")
    labels: list[str]
    created_at: datetime
    search_score: Optional[float] = Field(default=None, description="Search relevance score (0.0-1.0)")
    episode_sources: list[EpisodeSource] = Field(default_factory=list, description="Sources from related episodes")

    class Config:
        json_encoders = {datetime: lambda v: v.astimezone(timezone.utc).isoformat()}


class PaginatedEntityResponse(BaseModel):
    """Paginated response for entities."""
    entities: list[EntityResult]
    pagination: dict[str, Any] = Field(description="Pagination metadata")
    total_count: Optional[int] = Field(default=None, description="Total number of entities (if available)")

    @classmethod
    def create(
        cls,
        entities: list[EntityResult],
        page: int,
        page_size: int,
        has_next: bool,
        has_previous: bool,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
        total_count: Optional[int] = None,
    ):
        """Create a paginated response with metadata."""
        pagination_meta = {
            "page": page,
            "page_size": page_size,
            "has_next": has_next,
            "has_previous": has_previous,
            "count": len(entities),
        }

        if next_cursor:
            pagination_meta["next_cursor"] = next_cursor
        if previous_cursor:
            pagination_meta["previous_cursor"] = previous_cursor

        return cls(
            entities=entities,
            pagination=pagination_meta,
            total_count=total_count,
        )


class NavigationLink(BaseModel):
    """Navigation link for entity exploration."""
    uuid: str = Field(default="", description="Entity UUID")
    name: str = Field(default="Unknown", description="Entity name")
    type: str = Field(default="Entity", description="Entity type")
    relationship: Optional[str] = Field(default=None, description="Relationship description")
    path: Optional[str] = Field(default=None, description="Connection path")


class NavigationLinks(BaseModel):
    """Collection of navigation links for entity context."""
    direct_entities: list[NavigationLink] = Field(description="Directly connected entities")
    extended_entities: list[NavigationLink] = Field(description="2-hop connected entities")
    episodes: list[NavigationLink] = Field(description="Related episodes")
    communities: list[NavigationLink] = Field(description="Related communities")


class EntityContextResponse(BaseModel):
    """Comprehensive entity context response for LLM prompting."""
    entity_uuid: str
    entity_name: str
    context: str = Field(description="Formatted context for LLM prompting")
    navigation_links: NavigationLinks = Field(description="Clickable links for exploration")
    raw_data: dict[str, Any] = Field(description="Raw structured data")

    class Config:
        json_encoders = {datetime: lambda v: v.astimezone(timezone.utc).isoformat()}
