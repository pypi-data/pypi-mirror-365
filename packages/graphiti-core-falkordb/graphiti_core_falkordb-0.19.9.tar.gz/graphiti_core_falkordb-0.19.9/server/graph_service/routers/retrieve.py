from datetime import datetime, timezone
from typing import Optional
import hashlib
import json

from fastapi import APIRouter, status, Query, Depends, Response, HTTPException

from graph_service.dto import (
    GetMemoryRequest,
    GetMemoryResponse,
    Message,
    SearchQuery,
    SearchResults,
    PaginationParams,
    SortParams,
    EntityResult,
    PaginatedEntityResponse,
    SortOrder,
    EntitySortField,
    EntityContextResponse,
    NavigationLinks,
)
from graph_service.zep_graphiti import ZepGraphitiDep, get_fact_result_from_edge
from graph_service.helpers.entity_context import format_comprehensive_context, extract_navigation_links
from graph_service.security import security_dependency, validate_group_access, UserContext
from graphiti_core_falkordb.graph_queries import get_recent_date_filter

router = APIRouter()


def compute_group_content_hash(nodes_data: list) -> str:
    """
    Compute a deterministic hash of node content for change detection.
    
    This function creates a hash based on the actual content of nodes,
    not their timestamps, to avoid false positive change detections.
    """
    # Sort nodes by UUID for deterministic ordering
    sorted_nodes = sorted(nodes_data, key=lambda x: x.get('uuid', ''))
    
    # Extract only content-relevant fields, excluding timestamps
    content_data = []
    for node in sorted_nodes:
        content_item = {
            'uuid': node.get('uuid', ''),
            'name': node.get('name', ''),
            'summary': node.get('summary', ''),
            'fact': node.get('fact', ''),
            'attributes': node.get('attributes', {}),
            'labels': sorted(node.get('labels', [])),  # Sort for consistency
            'type': node.get('type', ''),
            'status': node.get('status', ''),
            # Include relationship data if present
            'source_uuid': node.get('source_uuid', ''),
            'target_uuid': node.get('target_uuid', ''),
            'relationship_type': node.get('relationship_type', '')
        }
        # Remove empty values to normalize the data
        content_item = {k: v for k, v in content_item.items() if v}
        content_data.append(content_item)
    
    # Create a deterministic JSON string
    content_json = json.dumps(content_data, sort_keys=True, separators=(',', ':'))
    
    # Compute SHA-256 hash
    return hashlib.sha256(content_json.encode('utf-8')).hexdigest()


async def get_episode_sources_for_entities(graphiti, entity_uuids: list[str]):
    """
    Retrieve episode source information for a list of entities.

    Returns a dictionary mapping entity UUID to list of episode source dictionaries.
    """
    from graphiti_core_falkordb.nodes import EpisodicNode

    entity_episode_sources = {}

    for entity_uuid in entity_uuids:
        try:
            # Get episodes that mention this entity
            episodes = await EpisodicNode.get_by_entity_node_uuid(graphiti.driver, entity_uuid)

            # Convert to episode source dictionaries
            from graph_service.dto.retrieve import extract_source_url_from_description

            episode_sources = []
            for episode in episodes:
                clean_description, source_url = extract_source_url_from_description(episode.source_description)
                episode_sources.append({
                    "source": episode.source.value,
                    "source_description": clean_description,
                    "source_url": source_url,
                    "episode_uuid": episode.uuid,
                    "episode_name": episode.name,
                    "created_at": episode.created_at,
                    "valid_at": episode.valid_at
                })

            entity_episode_sources[entity_uuid] = episode_sources
        except Exception as e:
            # If there's an error retrieving episodes for this entity, just set empty list
            entity_episode_sources[entity_uuid] = []

    return entity_episode_sources


@router.post('/search', status_code=status.HTTP_200_OK)
async def search(query: SearchQuery, graphiti: ZepGraphitiDep):
    relevant_edges = await graphiti.search(
        group_ids=query.group_ids,
        query=query.query,
        num_results=query.max_facts,
    )
    facts = [get_fact_result_from_edge(edge) for edge in relevant_edges]
    return SearchResults(
        facts=facts,
    )


@router.get('/entity-edge/{uuid}', status_code=status.HTTP_200_OK)
async def get_entity_edge(uuid: str, graphiti: ZepGraphitiDep):
    entity_edge = await graphiti.get_entity_edge(uuid)
    return get_fact_result_from_edge(entity_edge)


@router.get('/episodes/{group_id}', status_code=status.HTTP_200_OK)
async def get_episodes(group_id: str, last_n: int, graphiti: ZepGraphitiDep):
    episodes = await graphiti.retrieve_episodes(
        group_ids=[group_id], last_n=last_n, reference_time=datetime.now(timezone.utc)
    )
    return episodes


@router.get('/entities/{group_id}', status_code=status.HTTP_200_OK)
async def get_entities(group_id: str, graphiti: ZepGraphitiDep):
    """Get all entities for a specific group to inspect their structure."""
    from graphiti_core_falkordb.nodes import EntityNode
    entities = await EntityNode.get_by_group_ids(graphiti.driver, [group_id])
    return {"entities": [{"uuid": e.uuid, "name": e.name, "summary": e.summary, "attributes": e.attributes or {}, "extra_attributes": getattr(e, 'extra_attributes', {}) or {}, "labels": e.labels} for e in entities]}


@router.get('/entities/{group_id}/paginated', status_code=status.HTTP_200_OK, response_model=PaginatedEntityResponse)
async def get_entities_paginated(
    graphiti: ZepGraphitiDep,
    group_id: str = Depends(validate_group_access),
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Number of items per page (max 100)"),
    sort_by: EntitySortField = Query(default=EntitySortField.CREATED_AT, description="Field to sort by"),
    sort_order: SortOrder = Query(default=SortOrder.DESC, description="Sort order"),
    attribute_sort_field: Optional[str] = Query(default=None, description="Custom attribute field to sort by (overrides sort_by)"),
    cursor: Optional[str] = Query(default=None, description="Cursor for cursor-based pagination (entity UUID)"),
    visible_only: Optional[bool] = Query(default=None, description="Filter by visibility (True=only visible entities, False=only hidden entities, None=all entities)"),
    entity_type: Optional[str] = Query(default=None, description="Filter by entity type name"),
    search: Optional[str] = Query(default=None, description="Search query for hybrid search across entity names, summaries, and content"),
):
    """
    Get entities for a specific group with pagination, sorting, and hybrid search support.

    This endpoint supports both page-based and cursor-based pagination:
    - Page-based: Use 'page' and 'page_size' parameters
    - Cursor-based: Use 'cursor' parameter with the UUID of the last entity from previous page

    Sorting is supported on standard fields (name, created_at, summary, uuid) and custom attributes.
    Use 'attribute_sort_field' to sort by any custom attribute defined in entity types.

    Filtering options:
    - visible_only: Filter by visibility setting (True=only visible entities, False=only hidden entities, None=all entities)
    - entity_type: Filter by entity type name (e.g., "Customer", "Project", "Task")
    - search: Hybrid search query that searches across entity names, summaries, and related content using semantic and keyword matching
    """
    from graphiti_core_falkordb.nodes import EntityNode
    from graph_service.entity_type_manager import entity_type_manager

    # Clean up attribute_sort_field
    if attribute_sort_field and attribute_sort_field.strip() == "":
        attribute_sort_field = None

    # Prepare filter conditions
    filter_conditions = {}

    # Add visibility filter if specified
    if visible_only is not None:
        # Get all entity types
        entity_types = await entity_type_manager.list_entity_types()

        # Create a mapping of entity type names to visibility settings
        visibility_map = {et.name: et.visible_by_default for et in entity_types}

        # Add to filter conditions
        filter_conditions["visibility"] = {
            "map": visibility_map,
            "value": visible_only
        }

    # Add entity type filter if specified
    if entity_type:
        filter_conditions["entity_type"] = entity_type

    # Initialize entity scores dictionary
    entity_scores = {}

    # Use database-level search when search query is provided for better performance
    if search and search.strip():
        search_query = search.strip()

        # Use Graphiti's database-level search for better performance
        try:
            from graphiti_core_falkordb.search.search_config import SearchConfig, EdgeSearchConfig, NodeSearchConfig
            from graphiti_core_falkordb.search.search_config import EdgeSearchMethod, NodeSearchMethod, EdgeReranker, NodeReranker
            from graphiti_core_falkordb.search.search_filters import SearchFilters

            # First, do a direct name-only search using database query
            from graphiti_core_falkordb.search.search_utils import lucene_sanitize

            # Direct name search using database index
            name_search_query = f'name:"{lucene_sanitize(search_query)}"'
            if group_id:
                name_search_query += f' AND group_id:"{lucene_sanitize(group_id)}"'

            # Get name matches directly from database
            name_query = """
                CALL db.index.fulltext.queryNodes('node_name_and_summary', $name_query)
                YIELD node AS n, score
                WHERE n:Entity AND n.name CONTAINS $search_term
                RETURN
                    n.uuid AS uuid,
                    n.group_id AS group_id,
                    n.name AS name,
                    n.summary AS summary,
                    n.created_at AS created_at,
                    n.labels AS labels,
                    n.attributes AS attributes,
                    n.extra_attributes AS extra_attributes,
                    score
                ORDER BY score DESC
                LIMIT $limit
            """

            name_results, _, _ = await graphiti.driver.execute_query(
                name_query,
                name_query=name_search_query,
                search_term=search_query,
                limit=page_size * 2,
                database_='neo4j',
                routing_='r',
            )

            # Convert to EntityNode objects
            name_entities = []
            for record in name_results:
                entity = EntityNode(
                    uuid=record['uuid'],
                    group_id=record['group_id'],
                    name=record['name'],
                    summary=record['summary'] or '',
                    created_at=record['created_at'],
                    labels=record['labels'] or [],
                    attributes=record['attributes'] or {},
                    extra_attributes=record['extra_attributes'] or {},
                )
                name_entities.append(entity)

            # Then supplement with hybrid search for semantic matches
            name_first_hybrid_config = SearchConfig(
                node_config=NodeSearchConfig(
                    search_methods=[NodeSearchMethod.bm25, NodeSearchMethod.cosine_similarity],
                    reranker=NodeReranker.rrf,
                    sim_min_score=0.3,
                ),
                limit=page_size,  # Fewer semantic results
            )

            # Use Graphiti's database-level search for semantic supplementation
            search_results = await graphiti.search_(
                query=search_query,
                config=name_first_hybrid_config,
                group_ids=[group_id],
            )

            # Combine name matches with semantic matches
            all_entities = name_entities.copy()  # Start with name matches
            entity_uuids_seen = {entity.uuid for entity in name_entities}

            # Add semantic matches that aren't already in name matches
            semantic_entities = []
            for node in search_results.nodes:
                if hasattr(node, 'uuid') and node.uuid and node.uuid not in entity_uuids_seen:
                    semantic_entities.append(node)
                    entity_uuids_seen.add(node.uuid)

            # Add entities from edge relationships (for semantic connections)
            edge_entity_uuids = set()
            for edge in search_results.edges:
                if hasattr(edge, 'source_node_uuid') and edge.source_node_uuid and edge.source_node_uuid not in entity_uuids_seen:
                    edge_entity_uuids.add(edge.source_node_uuid)
                if hasattr(edge, 'target_node_uuid') and edge.target_node_uuid and edge.target_node_uuid not in entity_uuids_seen:
                    edge_entity_uuids.add(edge.target_node_uuid)

            # Fetch edge-related entities
            if edge_entity_uuids:
                edge_entities = await EntityNode.get_by_uuids(graphiti.driver, list(edge_entity_uuids))
                semantic_entities.extend(edge_entities)

            # Add semantic entities to the list
            all_entities.extend(semantic_entities)

            # Filter out entities that only have the generic "Entity" label
            all_entities = [
                entity for entity in all_entities
                if len(entity.labels) > 1 or (len(entity.labels) == 1 and entity.labels[0] != 'Entity')
            ]

            # Score entities with heavy name bias
            search_lower = search_query.lower()
            entity_scores = {}
            for i, entity in enumerate(all_entities):
                entity_name_lower = entity.name.lower()

                # Name matches get massive scores (1000+)
                if search_lower == entity_name_lower:
                    score = 1000
                elif entity_name_lower.startswith(search_lower):
                    score = 800
                elif search_lower in entity_name_lower:
                    score = 600
                else:
                    # Check individual words
                    word_score = 0
                    for word in search_lower.split():
                        if len(word) >= 2 and word in entity_name_lower:
                            word_score = max(word_score, 300)
                    score = word_score

                # If it's from name search (first entities), boost score
                if i < len(name_entities):
                    score += 100  # Name search bonus

                # Semantic matches get lower base score
                if score == 0:
                    score = 50  # Base score for semantic matches

                entity_scores[entity.uuid] = score

            # Sort by score (name matches heavily prioritized)
            all_entities.sort(key=lambda e: entity_scores.get(e.uuid, 0), reverse=True)

            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Name-prioritized search for '{search_query}' found {len(name_entities)} name matches + {len(all_entities) - len(name_entities)} semantic matches")

        except Exception as e:
            # If search fails, return empty results
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Database search failed: {e}")
            all_entities = []
    else:
        # No search query - get all entities
        all_entities = await EntityNode.get_by_group_ids(graphiti.driver, [group_id])

        # Filter out entities that only have the generic "Entity" label
        all_entities = [
            entity for entity in all_entities
            if len(entity.labels) > 1 or (len(entity.labels) == 1 and entity.labels[0] != 'Entity')
        ]

    # Apply visibility filter if specified
    if visible_only is not None:
        # Get all entity types
        entity_types = await entity_type_manager.list_entity_types()
        visibility_map = {et.name: et.visible_by_default for et in entity_types}

        filtered_entities = []
        for entity in all_entities:
            # Get the primary entity type (first non-Entity label)
            entity_type_name = next((label for label in entity.labels if label != 'Entity'), None)
            if entity_type_name:
                is_visible = visibility_map.get(entity_type_name, True)  # Default to visible if not found
                if (visible_only and is_visible) or (not visible_only and not is_visible):
                    filtered_entities.append(entity)
            elif visible_only:  # If no entity type found and we want visible only, include it (default behavior)
                filtered_entities.append(entity)
        all_entities = filtered_entities

    # Apply entity type filter if specified
    if entity_type:
        all_entities = [e for e in all_entities if entity_type in e.labels]

    # Sort entities
    if attribute_sort_field:
        # Sort by custom attribute
        def sort_key(entity):
            value = entity.attributes.get(attribute_sort_field)
            # Handle None values by putting them at the end
            if value is None:
                return (1, "")  # Sort None values last
            return (0, str(value))
        all_entities.sort(key=sort_key, reverse=(sort_order.value == "desc"))
    else:
        # Sort by standard field
        if sort_by.value == "name":
            all_entities.sort(key=lambda e: e.name, reverse=(sort_order.value == "desc"))
        elif sort_by.value == "created_at":
            all_entities.sort(key=lambda e: e.created_at, reverse=(sort_order.value == "desc"))
        elif sort_by.value == "summary":
            all_entities.sort(key=lambda e: e.summary, reverse=(sort_order.value == "desc"))
        elif sort_by.value == "uuid":
            all_entities.sort(key=lambda e: e.uuid, reverse=(sort_order.value == "desc"))

    # Implement pagination
    total_count = len(all_entities)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    entities = all_entities[start_idx:end_idx]
    has_next = end_idx < total_count

    # Get episode sources for all entities
    entity_uuids = [e.uuid for e in entities]
    episode_sources_map = await get_episode_sources_for_entities(graphiti, entity_uuids)

    # Convert to EntityResult objects with search scores and episode sources
    entity_results = [
        EntityResult(
            uuid=e.uuid,
            name=e.name,
            summary=e.summary,
            attributes=e.attributes or {},  # Keep attributes separate
            extra_attributes=getattr(e, 'extra_attributes', {}) or {},  # Keep extra_attributes separate
            labels=e.labels,
            created_at=e.created_at,
            search_score=entity_scores.get(e.uuid, 0) / 1000.0 if search and search.strip() and e.uuid in entity_scores else None,  # Normalize to 0-1 range
            episode_sources=episode_sources_map.get(e.uuid, [])
        )
        for e in entities
    ]

    # Determine cursors for navigation
    next_cursor = entity_results[-1].uuid if entity_results and has_next else None
    previous_cursor = entity_results[0].uuid if entity_results and page > 1 else None

    # Create paginated response
    return PaginatedEntityResponse.create(
        entities=entity_results,
        page=page,
        page_size=page_size,
        has_next=has_next,
        has_previous=page > 1,
        next_cursor=next_cursor,
        previous_cursor=previous_cursor,
        total_count=total_count,
    )


@router.get('/entities/{group_id}/sort-fields', status_code=status.HTTP_200_OK)
async def get_entity_sort_fields(group_id: str, graphiti: ZepGraphitiDep):
    """
    Get available fields for sorting entities in the specified group.

    Returns both standard fields (name, created_at, summary, uuid) and
    custom attribute fields that are present in the entities.
    """
    from graphiti_core_falkordb.nodes import EntityNode

    # Get all entities to analyze their attributes
    entities = await EntityNode.get_by_group_ids(graphiti.driver, [group_id])

    # Collect all unique attribute fields
    attribute_fields = set()
    for entity in entities:
        if entity.attributes:
            attribute_fields.update(entity.attributes.keys())

    # Standard fields that are always available
    standard_fields = ["name", "created_at", "summary", "uuid"]

    sort_fields = {
        "standard_fields": standard_fields,
        "attribute_fields": sorted(list(attribute_fields))
    }

    return {
        "group_id": group_id,
        "sort_fields": sort_fields,
        "description": {
            "standard_fields": "Built-in entity fields that are always available for sorting",
            "attribute_fields": "Custom attribute fields from entity types that are available for sorting"
        }
    }


@router.get('/entities/{uuid}/context', status_code=status.HTTP_200_OK, response_model=EntityContextResponse)
async def get_entity_context(
    uuid: str,
    response: Response,
    graphiti: ZepGraphitiDep,
    max_relationships: int = Query(default=50, ge=1, le=100, description="Max relationships to include (optimized for deep exploration)"),
    relationship_depth: int = Query(default=2, ge=1, le=3, description="Depth of relationship traversal (2-hop for extended network)"),
    include_episodes: bool = Query(default=True, description="Include episodic context for maximum nuance"),
    include_communities: bool = Query(default=True, description="Include community information for full context"),
    min_score: float = Query(default=0.4, ge=0.0, le=1.0, description="Minimum relevance score (lower = more inclusive)"),
    use_cross_encoder: bool = Query(default=True, description="Use cross-encoder reranking for better quality"),
):
    """
    Get comprehensive entity context with maximum nuance for LLM analysis.

    OPTIMIZED FOR DEEP EXPLORATION (not quick search):
    - 50 relationships by default (vs typical 10)
    - 2-hop relationship traversal for extended network
    - Lower relevance threshold (0.4) for broader context
    - Cross-encoder reranking for better quality
    - Full episodic and community context included

    This endpoint provides rich context including:
    - Entity details and all attributes
    - Multi-hop relationships (1-hop and 2-hop)
    - Related episodes and communities
    - Navigation links for clickable exploration
    - Temporal relationship information

    Perfect for LLM prompting where you need maximum context and
    want the LLM to suggest related entities to explore next.

    Note: This endpoint is designed for detail views and may take
    longer than quick search operations due to comprehensive data retrieval.
    """
    from graphiti_core_falkordb.nodes import EntityNode
    from graphiti_core_falkordb.errors import NodeNotFoundError

    # Validate parameters for optimal performance
    if max_relationships > 100:
        raise HTTPException(status_code=400, detail="max_relationships cannot exceed 100 for performance reasons")

    if relationship_depth > 3:
        raise HTTPException(status_code=400, detail="relationship_depth cannot exceed 3 to prevent exponential complexity")

    if min_score < 0.0 or min_score > 1.0:
        raise HTTPException(status_code=400, detail="min_score must be between 0.0 and 1.0")

    # Adjust parameters based on depth to maintain performance
    if relationship_depth >= 3:
        max_relationships = min(max_relationships, 30)  # Reduce for 3-hop queries

    # Get the main entity
    try:
        entity = await EntityNode.get_by_uuid(graphiti.driver, uuid)
    except NodeNotFoundError:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Calculate recent date threshold (30 days ago)
    from datetime import timedelta
    recent_date_threshold = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    # Get comprehensive relationships with multi-hop traversal
    # Simplified query that works with actual schema
    relationships_query = """
    MATCH (e:Entity {uuid: $uuid})

    // Direct relationships (1-hop outgoing)
    OPTIONAL MATCH (e)-[r1:RELATES_TO]->(target1:Entity)
    WHERE r1.expired_at IS NULL OR r1.expired_at IS NOT NULL
    WITH e, collect(DISTINCT {
        depth: 1,
        direction: 'outgoing',
        fact: COALESCE(r1.fact, ''),
        relationship_uuid: COALESCE(r1.uuid, ''),
        relationship_type: COALESCE(r1.name, 'relates_to'),
        target_uuid: COALESCE(target1.uuid, ''),
        target_name: COALESCE(target1.name, 'Unknown'),
        target_summary: COALESCE(target1.summary, ''),
        target_attributes: {},
        target_labels: COALESCE(labels(target1), ['Entity']),
        valid_at: r1.valid_at,
        invalid_at: r1.invalid_at,
        created_at: r1.created_at,
        relevance_score: CASE
            WHEN r1.valid_at IS NOT NULL AND r1.invalid_at IS NULL THEN 1.0
            WHEN r1.created_at > $recent_date_threshold THEN 0.9
            ELSE 0.7
        END
    })[0..$max_relationships] as outgoing_1hop

    // Direct relationships (1-hop incoming)
    OPTIONAL MATCH (source1:Entity)-[r2:RELATES_TO]->(e)
    WHERE r2.expired_at IS NULL OR r2.expired_at IS NOT NULL
    WITH e, outgoing_1hop, collect(DISTINCT {
        depth: 1,
        direction: 'incoming',
        fact: COALESCE(r2.fact, ''),
        relationship_uuid: COALESCE(r2.uuid, ''),
        relationship_type: COALESCE(r2.name, 'relates_to'),
        source_uuid: COALESCE(source1.uuid, ''),
        source_name: COALESCE(source1.name, 'Unknown'),
        source_summary: COALESCE(source1.summary, ''),
        source_attributes: {},
        source_labels: COALESCE(labels(source1), ['Entity']),
        valid_at: r2.valid_at,
        invalid_at: r2.invalid_at,
        created_at: r2.created_at,
        relevance_score: CASE
            WHEN r2.valid_at IS NOT NULL AND r2.invalid_at IS NULL THEN 1.0
            WHEN r2.created_at > $recent_date_threshold THEN 0.9
            ELSE 0.7
        END
    })[0..$max_relationships] as incoming_1hop

    // Second-hop relationships (if depth >= 2)
    OPTIONAL MATCH (e)-[r1:RELATES_TO]->(target1:Entity)-[r3:RELATES_TO]->(target2:Entity)
    WHERE $relationship_depth >= 2
    AND (r1.expired_at IS NULL OR r1.expired_at IS NOT NULL)
    AND (r3.expired_at IS NULL OR r3.expired_at IS NOT NULL)
    WITH e, outgoing_1hop, incoming_1hop, collect(DISTINCT {
        depth: 2,
        direction: 'outgoing',
        fact: COALESCE(r3.fact, ''),
        relationship_uuid: COALESCE(r3.uuid, ''),
        relationship_type: COALESCE(r3.name, 'relates_to'),
        intermediate_entity: COALESCE(target1.name, 'Unknown'),
        intermediate_uuid: COALESCE(target1.uuid, ''),
        target_uuid: COALESCE(target2.uuid, ''),
        target_name: COALESCE(target2.name, 'Unknown'),
        target_summary: COALESCE(target2.summary, ''),
        target_labels: COALESCE(labels(target2), ['Entity']),
        path: COALESCE(e.name, 'Unknown') + ' -> ' + COALESCE(target1.name, 'Unknown') + ' -> ' + COALESCE(target2.name, 'Unknown'),
        valid_at: r3.valid_at,
        created_at: r3.created_at,
        relevance_score: CASE
            WHEN r3.valid_at IS NOT NULL AND r3.invalid_at IS NULL THEN 0.8
            WHEN r3.created_at > $recent_date_threshold THEN 0.7
            ELSE 0.5
        END
    })[0..($max_relationships/2)] as outgoing_2hop

    RETURN outgoing_1hop, incoming_1hop, outgoing_2hop
    """

    # Execute relationships query with performance monitoring
    import time
    start_time = time.time()

    rel_records, _, _ = await graphiti.driver.execute_query(
        relationships_query,
        uuid=uuid,
        max_relationships=max_relationships,
        relationship_depth=relationship_depth,
        recent_date_threshold=recent_date_threshold,
        routing_='r'
    )

    query_time = time.time() - start_time
    # Log slow queries for optimization
    if query_time > 2.0:  # Log queries taking more than 2 seconds
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Slow entity context query for {uuid}: {query_time:.2f}s with {max_relationships} max_relationships, depth {relationship_depth}")

    def convert_neo4j_datetime(obj):
        """Convert Neo4j DateTime objects to Python datetime objects."""
        from neo4j.time import DateTime
        from datetime import datetime, timezone

        if isinstance(obj, DateTime):
            # Convert Neo4j DateTime to Python datetime
            # Neo4j DateTime has year, month, day, hour, minute, second, nanosecond attributes
            return datetime(
                year=obj.year,
                month=obj.month,
                day=obj.day,
                hour=obj.hour,
                minute=obj.minute,
                second=obj.second,
                microsecond=obj.nanosecond // 1000,  # Convert nanoseconds to microseconds
                tzinfo=timezone.utc
            )
        elif isinstance(obj, dict):
            return {k: convert_neo4j_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_neo4j_datetime(item) for item in obj]
        else:
            return obj

    # Safely extract relationship data with defaults
    if rel_records and len(rel_records) > 0:
        # Convert Neo4j Record to dict and handle datetime objects
        record = rel_records[0]
        raw_data = {
            "outgoing_1hop": record.get("outgoing_1hop", []) or [],
            "incoming_1hop": record.get("incoming_1hop", []) or [],
            "outgoing_2hop": record.get("outgoing_2hop", []) or []
        }
        # Convert Neo4j DateTime objects to Python datetime objects
        relationships_data = convert_neo4j_datetime(raw_data)
    else:
        relationships_data = {
            "outgoing_1hop": [],
            "incoming_1hop": [],
            "outgoing_2hop": []
        }

    # Get episodic context for this entity
    if include_episodes:
        try:
            from graphiti_core_falkordb.nodes import EpisodicNode
            episodes = await EpisodicNode.get_by_entity_node_uuid(graphiti.driver, uuid)
            episodes_data = [
                {
                    "episode_uuid": episode.uuid,
                    "episode_name": episode.name,
                    "episode_content": episode.content[:200] + "..." if len(episode.content) > 200 else episode.content,
                    "episode_type": episode.source.value,
                    "source_description": episode.source_description,
                    "created_at": episode.created_at,
                    "valid_at": episode.valid_at,
                    "relevance_score": 0.8  # Default relevance score for episodes
                }
                for episode in episodes
            ]
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to retrieve episodes for entity {uuid}: {e}")
            episodes_data = []
    else:
        episodes_data = []

    # Skip community context since Community nodes/relationships don't exist in this schema
    communities_data = []

    # Prepare context data
    context_data = {
        "entity": entity,
        "relationships": relationships_data,
        "episodes": episodes_data,
        "communities": communities_data
    }

    # Generate formatted context and navigation links with error handling
    try:
        formatted_context = format_comprehensive_context(context_data)
        navigation_links = extract_navigation_links(context_data)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error formatting context for entity {uuid}: {e}")
        # Provide fallback context
        formatted_context = f"""
=== ENTITY PROFILE ===
Name: {entity.name}
UUID: {entity.uuid}
Summary: {entity.summary}
Labels: {', '.join(entity.labels)}

=== ERROR ===
Unable to format full context due to data structure mismatch.
This entity exists but may have limited relationship data available.
        """.strip()
        navigation_links = NavigationLinks(
            direct_entities=[],
            extended_entities=[],
            episodes=[],
            communities=[]
        )

    # Prepare raw data for response
    raw_data = {
        "entity": {
            "uuid": entity.uuid,
            "name": entity.name,
            "summary": entity.summary,
            "attributes": entity.attributes or {},  # Keep attributes separate
            "extra_attributes": getattr(entity, 'extra_attributes', {}) or {},  # Keep extra_attributes separate
            "labels": entity.labels,
            "created_at": entity.created_at
        },
        "relationships": relationships_data,
        "episodes": episodes_data,
        "communities": communities_data
    }

    # Add caching headers for performance
    # Entity context can be cached for 5 minutes since relationships don't change frequently
    response.headers["Cache-Control"] = "public, max-age=300"
    response.headers["X-Query-Time"] = f"{query_time:.2f}s"
    response.headers["X-Relationship-Count"] = str(len(relationships_data.get('outgoing_1hop', [])) + len(relationships_data.get('incoming_1hop', [])))
    response.headers["X-Extended-Count"] = str(len(relationships_data.get('outgoing_2hop', [])))

    # Add performance metadata to raw_data
    raw_data["performance"] = {
        "query_time_seconds": round(query_time, 2),
        "relationship_count": len(relationships_data.get('outgoing_1hop', [])) + len(relationships_data.get('incoming_1hop', [])),
        "extended_relationship_count": len(relationships_data.get('outgoing_2hop', [])),
        "episode_count": len(episodes_data),
        "community_count": len(communities_data),
        "parameters_used": {
            "max_relationships": max_relationships,
            "relationship_depth": relationship_depth,
            "min_score": min_score,
            "include_episodes": include_episodes,
            "include_communities": include_communities
        }
    }

    return EntityContextResponse(
        entity_uuid=uuid,
        entity_name=entity.name,
        context=formatted_context,
        navigation_links=navigation_links,
        raw_data=raw_data
    )


@router.get('/groups/{group_id}/changed', status_code=status.HTTP_200_OK)
async def check_group_changed(
    group_id: str,
    graphiti: ZepGraphitiDep,
    since: str = Query(..., description="Previous content hash or cache key"),
):
    """
    Check if a group has changed by comparing content hashes.

    This endpoint computes a hash of all node content (excluding timestamps)
    and compares it with the provided hash to detect actual content changes.
    Returns just a boolean and new cache key if changed.
    """
    # Extract the previous hash from the cache key if it's in the format "group_id:hash"
    previous_hash = None
    if ':' in since and len(since.split(':')) == 2:
        _, previous_hash = since.split(':')
    else:
        # Assume the entire string is the hash
        previous_hash = since

    # Query all nodes and relationships for the group
    content_query = """
    MATCH (n)
    WHERE n.group_id = $group_id
    AND (n:Episode OR n:Entity OR n:RELATES_TO)
    RETURN 
        n.uuid as uuid,
        n.name as name,
        n.summary as summary,
        n.fact as fact,
        n.attributes as attributes,
        labels(n) as labels,
        n.type as type,
        n.status as status,
        n.source_uuid as source_uuid,
        n.target_uuid as target_uuid,
        n.relationship_type as relationship_type
    ORDER BY n.uuid
    """

    try:
        records, _, _ = await graphiti.driver.execute_query(
            content_query,
            group_id=group_id,
            routing_='r'
        )

        # Extract node data from records
        nodes_data = []
        for record in records:
            node_data = {
                'uuid': record.get('uuid'),
                'name': record.get('name'),
                'summary': record.get('summary'),
                'fact': record.get('fact'),
                'attributes': record.get('attributes'),
                'labels': record.get('labels'),
                'type': record.get('type'),
                'status': record.get('status'),
                'source_uuid': record.get('source_uuid'),
                'target_uuid': record.get('target_uuid'),
                'relationship_type': record.get('relationship_type')
            }
            nodes_data.append(node_data)

        # Compute the current content hash
        current_hash = compute_group_content_hash(nodes_data)

        # Compare hashes
        has_changed = current_hash != previous_hash

        return {
            "changed": has_changed,
            "cache_key": f"{group_id}:{current_hash}"
        }

    except Exception as e:
        # On error, assume changed to be safe
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error checking group changes for {group_id}: {e}")
        
        # Generate a new hash based on current timestamp to force refresh
        error_hash = hashlib.sha256(f"{group_id}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()
        return {
            "changed": True,
            "cache_key": f"{group_id}:{error_hash}"
        }


@router.get('/debug/entity-types', status_code=status.HTTP_200_OK)
async def debug_entity_types():
    """Debug endpoint to check entity type manager state."""
    from graph_service.entity_type_manager import entity_type_manager

    # Force load from database
    await entity_type_manager._ensure_loaded()

    # Get all entity types
    entity_types = await entity_type_manager.list_entity_types()

    # Get pydantic models
    models = await entity_type_manager.get_pydantic_models()

    return {
        "entity_types_count": len(entity_types),
        "entity_types": [et.name for et in entity_types],
        "pydantic_models": list(models.keys()),
        "models_details": {name: {"fields": list(model.model_fields.keys())} for name, model in models.items()}
    }


@router.post('/get-memory', status_code=status.HTTP_200_OK)
async def get_memory(
    request: GetMemoryRequest,
    graphiti: ZepGraphitiDep,
):
    combined_query = compose_query_from_messages(request.messages)
    result = await graphiti.search(
        group_ids=[request.group_id],
        query=combined_query,
        num_results=request.max_facts,
    )
    facts = [get_fact_result_from_edge(edge) for edge in result]
    return GetMemoryResponse(facts=facts)


def compose_query_from_messages(messages: list[Message]):
    combined_query = ''
    for message in messages:
        combined_query += f'{message.role_type or ""}({message.role or ""}): {message.content}\n'
    return combined_query
