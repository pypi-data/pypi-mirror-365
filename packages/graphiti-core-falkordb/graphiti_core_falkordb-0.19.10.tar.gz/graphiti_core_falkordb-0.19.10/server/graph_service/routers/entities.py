"""
Entity CRUD operations router.
Provides endpoints for creating, reading, updating, and deleting individual entities.
"""

import uuid as uuid_lib
import re
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Query, Depends
from pydantic import ValidationError

from graph_service.dto.ingest import CreateEntityRequest, UpdateEntityRequest, EntityResponse
from graph_service.dto.common import Result
from graph_service.zep_graphiti import ZepGraphitiDep
from graph_service.entity_type_manager import entity_type_manager
from graph_service.security import security_dependency, validate_group_access, UserContext
from graphiti_core_falkordb.nodes import EntityNode, EpisodeType
from graphiti_core_falkordb.utils.datetime_utils import utc_now

router = APIRouter(prefix="/entities", tags=["entities"])


def _is_valid_entity_name(name: str) -> tuple[bool, str]:
    """
    Validate whether an entity name is suitable for creation.

    This function prevents low-quality entities like placeholders, collections,
    or generic descriptions from being created.

    Args:
        name: The entity name to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Entity name cannot be empty"

    name = name.strip()

    # Reject entities that are clearly placeholders or collections
    placeholder_patterns = [
        r'^(research\s+)?tasks?$',  # "Research Tasks", "Tasks", "Task"
        r'^(various|multiple|several)\s+\w+',  # "Various projects", "Multiple tasks"
        r'^(collection|list|set)\s+of\s+\w+',  # "Collection of items"
        r'^(project|business|work)\s+(activities|items|things)$',  # Generic work references
        r'^(placeholder|example|sample|test)\s*\w*',  # Placeholder entities
        r'^(todo|to-do)\s+(list|items?)$',  # Generic todo references
        r'^(misc|miscellaneous)\s+\w+',  # Miscellaneous items
        r'^(general|generic)\s+\w+',  # General/generic items
        r'^(all|any)\s+\w+',  # "All projects", "Any tasks"
        r'^\w+\s+(and|or)\s+\w+\s+(activities|items|things)$',  # "X and Y activities"
    ]

    for pattern in placeholder_patterns:
        if re.match(pattern, name, re.IGNORECASE):
            return False, f"Entity name '{name}' appears to be a placeholder or collection rather than a specific entity"

    # Reject entities that are too generic or vague
    generic_terms = [
        'activities', 'items', 'things', 'stuff', 'work', 'business',
        'projects', 'tasks', 'issues', 'requests', 'documents', 'files',
        'data', 'information', 'content', 'materials', 'resources'
    ]

    # If the name is just a generic term (case-insensitive)
    if name.lower() in generic_terms:
        return False, f"Entity name '{name}' is too generic. Please use a specific name."

    # Reject entities that appear to be collections or lists
    collection_indicators = [
        'appears to be', 'collection of', 'list of', 'set of', 'group of',
        'various', 'multiple', 'several', 'different', 'assorted',
        'including', 'such as', 'for example', 'e.g.', 'etc.'
    ]

    name_lower = name.lower()
    for indicator in collection_indicators:
        if indicator in name_lower:
            return False, f"Entity name '{name}' appears to describe a collection rather than a specific entity"

    # Reject entities that are too long (likely descriptions rather than names)
    if len(name) > 100:
        return False, f"Entity name is too long ({len(name)} characters). Please use a shorter, more specific name."

    # Reject entities with too many words (likely descriptions)
    word_count = len(name.split())
    if word_count > 8:
        return False, f"Entity name has too many words ({word_count}). Please use a shorter, more specific name."

    # Reject entities that look like sentences or descriptions
    sentence_indicators = [
        'the entity', 'this is', 'it is', 'appears to', 'seems to',
        'consists of', 'includes', 'contains', 'represents'
    ]

    for indicator in sentence_indicators:
        if indicator in name_lower:
            return False, f"Entity name '{name}' appears to be a description rather than a name"

    return True, ""


async def _create_entity_episode(
    graphiti,
    action: str,
    entity: EntityNode,
    entity_type: str,
    changes: Optional[Dict[str, Any]] = None
):
    """
    Create an episode describing entity CRUD operations to trigger full ingestion pipeline.

    This ensures that entity changes are processed through the same pipeline as regular
    content ingestion, maintaining consistency and extracting relevant relationships.
    """
    # Build episode content describing the entity operation
    episode_content = f"Entity {action}: {entity.name}"

    if entity.summary:
        episode_content += f" - {entity.summary}"

    # Add entity type information
    episode_content += f" (Type: {entity_type})"

    # Add attributes information
    if entity.attributes:
        attr_descriptions = []
        for key, value in entity.attributes.items():
            attr_descriptions.append(f"{key}: {value}")
        if attr_descriptions:
            episode_content += f" with attributes: {', '.join(attr_descriptions)}"

    # Add change information for updates
    if changes and action == "updated":
        change_descriptions = []
        for key, value in changes.items():
            change_descriptions.append(f"{key} changed to: {value}")
        if change_descriptions:
            episode_content += f". Changes: {', '.join(change_descriptions)}"

    # Get entity types for the ingestion pipeline
    entity_types = await entity_type_manager.get_pydantic_models()

    # Create episode through the full ingestion pipeline
    try:
        await graphiti.add_episode(
            name=f"Entity {action.title()}: {entity.name}",
            episode_body=episode_content,
            source_description=f"Entity CRUD operation - {action} {entity_type}",
            reference_time=utc_now(),
            source=EpisodeType.text,
            group_id=entity.group_id,
            entity_types=entity_types,
        )
    except Exception as e:
        # Log the error but don't fail the CRUD operation
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to create episode for entity {action}: {e}")
        # Continue with the CRUD operation even if episode creation fails


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=EntityResponse)
async def create_entity(
    request: CreateEntityRequest,
    graphiti: ZepGraphitiDep,
    user: UserContext = Depends(security_dependency),
):
    """
    Create a new entity with entity type validation.

    This endpoint creates a new entity with proper entity type validation,
    ensuring the attributes match the entity type schema.
    """
    # Validate and authorize group access
    from graph_service.security import validate_and_authorize_group
    validated_group_id = validate_and_authorize_group(request.group_id, user)
    request.group_id = validated_group_id

    # Validate entity name quality
    is_valid_name, name_error = _is_valid_entity_name(request.name)
    if not is_valid_name:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entity name: {name_error}"
        )

    # Validate entity type exists
    entity_type = await entity_type_manager.get_entity_type(request.entity_type)
    if not entity_type:
        raise HTTPException(
            status_code=400, 
            detail=f"Entity type '{request.entity_type}' not found"
        )
    
    # Separate schema-defined attributes from extra attributes
    schema_attributes = {}
    extra_attributes = request.extra_attributes or {}

    # Validate attributes against entity type schema
    if request.attributes:
        try:
            # Get the Pydantic model for validation
            pydantic_models = await entity_type_manager.get_pydantic_models()
            entity_model = pydantic_models.get(request.entity_type)

            if entity_model:
                # Get defined field names from the entity type
                defined_fields = set(entity_model.model_fields.keys())

                # Separate attributes into schema-defined and extra
                for key, value in request.attributes.items():
                    if key in defined_fields:
                        schema_attributes[key] = value
                    else:
                        extra_attributes[key] = value

                # Validate only the schema-defined attributes
                if schema_attributes:
                    validated_data = entity_model(**schema_attributes)
                    schema_attributes = validated_data.model_dump()
            else:
                # If no entity model found, treat all as extra attributes
                extra_attributes.update(request.attributes)
        except ValidationError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Attribute validation failed: {e}"
            )
    
    # Generate UUID if not provided
    entity_uuid = str(uuid_lib.uuid4())
    
    # Create entity node with proper labels
    entity_node = EntityNode(
        uuid=entity_uuid,
        group_id=request.group_id,
        name=request.name,
        summary=request.summary or "",
        labels=["Entity", request.entity_type],
        attributes=schema_attributes,
        extra_attributes=extra_attributes,
        created_at=utc_now(),
    )
    
    # Generate embedding and save to database
    await entity_node.generate_name_embedding(graphiti.embedder)
    await entity_node.save(graphiti.driver)

    # Create an episode describing the entity creation to trigger full ingestion pipeline
    await _create_entity_episode(
        graphiti=graphiti,
        action="created",
        entity=entity_node,
        entity_type=request.entity_type,
        changes=None
    )

    # Merge attributes and extra_attributes for response
    merged_attributes = {**(entity_node.attributes or {}), **(getattr(entity_node, 'extra_attributes', {}) or {})}

    return EntityResponse(
        uuid=entity_node.uuid,
        group_id=entity_node.group_id,
        name=entity_node.name,
        summary=entity_node.summary,
        attributes=merged_attributes,  # Keep merged for backward compatibility
        extra_attributes=getattr(entity_node, 'extra_attributes', {}),  # Separate extra_attributes
        labels=entity_node.labels,
        created_at=entity_node.created_at.isoformat(),
        updated_at=entity_node.updated_at.isoformat() if hasattr(entity_node, 'updated_at') and entity_node.updated_at else None,
        episode_sources=[],  # New entity, no episodes yet
    )


@router.get("/{entity_uuid}", status_code=status.HTTP_200_OK, response_model=EntityResponse)
async def get_entity(
    entity_uuid: str,
    graphiti: ZepGraphitiDep,
    user: UserContext = Depends(security_dependency),
):
    """
    Get an entity by UUID.
    """
    from graphiti_core_falkordb.errors import NodeNotFoundError

    try:
        entity = await EntityNode.get_by_uuid(graphiti.driver, entity_uuid)
    except NodeNotFoundError:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Validate user has access to this entity's group
    from graph_service.security import validate_and_authorize_group
    validate_and_authorize_group(entity.group_id, user)
    
    # Merge attributes and extra_attributes for response
    merged_attributes = {**(entity.attributes or {}), **(getattr(entity, 'extra_attributes', {}) or {})}

    # Get episode sources for this entity
    episode_sources = []
    try:
        from graphiti_core_falkordb.nodes import EpisodicNode
        from graph_service.dto.retrieve import extract_source_url_from_description

        episodes = await EpisodicNode.get_by_entity_node_uuid(graphiti.driver, entity_uuid)
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
    except Exception as e:
        # If there's an error retrieving episodes, just use empty list
        episode_sources = []

    return EntityResponse(
        uuid=entity.uuid,
        group_id=entity.group_id,
        name=entity.name,
        summary=entity.summary,
        attributes=merged_attributes,  # Keep merged for backward compatibility
        extra_attributes=getattr(entity, 'extra_attributes', {}),  # Separate extra_attributes
        labels=entity.labels,
        created_at=entity.created_at.isoformat(),
        updated_at=entity.updated_at.isoformat() if hasattr(entity, 'updated_at') and entity.updated_at else None,
        episode_sources=episode_sources,
    )


@router.put("/{entity_uuid}", status_code=status.HTTP_200_OK, response_model=EntityResponse)
async def update_entity(
    entity_uuid: str,
    request: UpdateEntityRequest,
    graphiti: ZepGraphitiDep,
    user: UserContext = Depends(security_dependency),
):
    """
    Update an existing entity.
    
    This endpoint allows updating entity name, summary, and attributes.
    Attribute validation is performed against the entity's type schema.
    """
    from graphiti_core_falkordb.errors import NodeNotFoundError
    
    # Get existing entity
    try:
        entity = await EntityNode.get_by_uuid(graphiti.driver, entity_uuid)
    except NodeNotFoundError:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Validate user has access to this entity's group
    from graph_service.security import validate_and_authorize_group
    validate_and_authorize_group(entity.group_id, user)

    # Validate entity name quality if name is being updated
    if request.name is not None:
        is_valid_name, name_error = _is_valid_entity_name(request.name)
        if not is_valid_name:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid entity name: {name_error}"
            )

    # Get entity type for validation
    entity_type_name = next((label for label in entity.labels if label != 'Entity'), None)
    
    # Debug logging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f'🔍 PUT /entities/{entity_uuid} - Request data:')
    logger.info(f'🔍 PUT - request.name: {request.name}')
    logger.info(f'🔍 PUT - request.summary: {request.summary}')
    logger.info(f'🔍 PUT - request.attributes: {request.attributes}')
    logger.info(f'🔍 PUT - request.extra_attributes: {request.extra_attributes}')

    # Separate schema-defined attributes from extra attributes
    schema_attributes_update = {}
    extra_attributes_update = request.extra_attributes or {}

    # Validate attributes if provided
    if request.attributes and entity_type_name:
        try:
            # Get the Pydantic model for validation
            pydantic_models = await entity_type_manager.get_pydantic_models()
            entity_model = pydantic_models.get(entity_type_name)

            if entity_model:
                # Get defined field names from the entity type
                defined_fields = set(entity_model.model_fields.keys())

                # Separate attributes into schema-defined and extra
                for key, value in request.attributes.items():
                    if key in defined_fields:
                        schema_attributes_update[key] = value
                    else:
                        extra_attributes_update[key] = value

                # Validate only the schema-defined attributes
                if schema_attributes_update:
                    # Merge with existing schema attributes for validation
                    merged_schema_attributes = {**(entity.attributes or {}), **schema_attributes_update}
                    validated_data = entity_model(**merged_schema_attributes)
                    schema_attributes_update = validated_data.model_dump()
            else:
                # If no entity model found, treat all as extra attributes
                extra_attributes_update.update(request.attributes)
        except ValidationError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Attribute validation failed: {e}"
            )
    
    # Prepare updated data (don't modify the original entity object)
    updated_name = request.name if request.name is not None else entity.name
    updated_summary = request.summary if request.summary is not None else entity.summary
    updated_attributes = entity.attributes or {}
    if schema_attributes_update:
        # Merge with existing schema attributes
        updated_attributes = {**updated_attributes, **schema_attributes_update}

    # Handle extra_attributes safely
    existing_extra_attributes = getattr(entity, 'extra_attributes', {}) or {}
    updated_extra_attributes = existing_extra_attributes
    if extra_attributes_update:
        # Merge with existing extra attributes
        updated_extra_attributes = {**existing_extra_attributes, **extra_attributes_update}

    logger.info(f'🔍 PUT - existing_extra_attributes: {existing_extra_attributes}')
    logger.info(f'🔍 PUT - extra_attributes_update: {extra_attributes_update}')
    logger.info(f'🔍 PUT - updated_extra_attributes: {updated_extra_attributes}')

    logger.info(f'🔍 PUT - existing_extra_attributes: {existing_extra_attributes}')
    logger.info(f'🔍 PUT - extra_attributes_update: {extra_attributes_update}')
    logger.info(f'🔍 PUT - updated_extra_attributes: {updated_extra_attributes}')

    # Track changes for episode creation
    changes = {}
    if request.name is not None:
        changes['name'] = request.name
    if request.summary is not None:
        changes['summary'] = request.summary
    if schema_attributes_update:
        changes['attributes'] = schema_attributes_update
    if extra_attributes_update:
        changes['extra_attributes'] = extra_attributes_update

    # Set updated timestamp if anything changed
    if changes:
        logger.info(f'🔍 PUT - Creating EntityNode with:')
        logger.info(f'🔍 PUT - updated_attributes: {updated_attributes}')
        logger.info(f'🔍 PUT - updated_extra_attributes: {updated_extra_attributes}')

        # Create a new EntityNode with updated data and timestamp
        updated_entity = EntityNode(
            uuid=entity.uuid,
            group_id=entity.group_id,
            name=updated_name,
            summary=updated_summary,
            labels=entity.labels,
            attributes=updated_attributes,
            extra_attributes=updated_extra_attributes,
            created_at=entity.created_at,
            updated_at=utc_now(),
            name_embedding=entity.name_embedding
        )

        logger.info(f'🔍 PUT - EntityNode created with extra_attributes: {getattr(updated_entity, "extra_attributes", "NOT_FOUND")}')
        # Generate embedding and save
        await updated_entity.generate_name_embedding(graphiti.embedder)
        await updated_entity.save(graphiti.driver)
        entity = updated_entity  # Update reference for response
    else:
        # No changes, just save as-is (but ensure we have a complete entity with extra_attributes)
        if not hasattr(entity, 'extra_attributes') or entity.extra_attributes is None:
            # Create a new EntityNode with extra_attributes field for older entities
            entity = EntityNode(
                uuid=entity.uuid,
                group_id=entity.group_id,
                name=entity.name,
                summary=entity.summary,
                labels=entity.labels,
                attributes=entity.attributes,
                extra_attributes={},
                created_at=entity.created_at,
                updated_at=entity.updated_at,
                name_embedding=entity.name_embedding
            )
        await entity.save(graphiti.driver)

    # Create an episode describing the entity update to trigger full ingestion pipeline
    await _create_entity_episode(
        graphiti=graphiti,
        action="updated",
        entity=entity,
        entity_type=entity_type_name or "Entity",
        changes=changes
    )
    
    # Merge attributes and extra_attributes for response
    merged_attributes = {**(entity.attributes or {}), **(getattr(entity, 'extra_attributes', {}) or {})}

    # Get episode sources for this entity
    episode_sources = []
    try:
        from graphiti_core_falkordb.nodes import EpisodicNode
        from graph_service.dto.retrieve import extract_source_url_from_description

        episodes = await EpisodicNode.get_by_entity_node_uuid(graphiti.driver, entity.uuid)
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
    except Exception:
        # If there's an error retrieving episodes, just use empty list
        episode_sources = []

    return EntityResponse(
        uuid=entity.uuid,
        group_id=entity.group_id,
        name=entity.name,
        summary=entity.summary,
        attributes=merged_attributes,  # Keep merged for backward compatibility
        extra_attributes=getattr(entity, 'extra_attributes', {}),  # Separate extra_attributes
        labels=entity.labels,
        created_at=entity.created_at.isoformat(),
        updated_at=entity.updated_at.isoformat() if hasattr(entity, 'updated_at') and entity.updated_at else None,
        episode_sources=episode_sources,
    )


@router.delete("/{entity_uuid}", status_code=status.HTTP_200_OK, response_model=Result)
async def delete_entity(
    entity_uuid: str,
    graphiti: ZepGraphitiDep,
    cascade: bool = Query(False, description="Whether to delete related relationships"),
    user: UserContext = Depends(security_dependency),
):
    """
    Delete an entity by UUID.
    
    If cascade=True, also deletes all relationships involving this entity.
    """
    from graphiti_core_falkordb.errors import NodeNotFoundError

    # Check if entity exists and get its details for episode creation
    try:
        entity = await EntityNode.get_by_uuid(graphiti.driver, entity_uuid)
    except NodeNotFoundError:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Validate user has access to this entity's group
    from graph_service.security import validate_and_authorize_group
    validate_and_authorize_group(entity.group_id, user)

    # Get entity type for episode creation
    entity_type_name = next((label for label in entity.labels if label != 'Entity'), "Entity")

    # Create an episode describing the entity deletion before actually deleting
    await _create_entity_episode(
        graphiti=graphiti,
        action="deleted",
        entity=entity,
        entity_type=entity_type_name,
        changes=None
    )

    # Delete the entity (and optionally its relationships)
    if cascade:
        # Delete all relationships involving this entity
        await graphiti.driver.execute_query(
            """
            MATCH (e:Entity {uuid: $uuid})
            OPTIONAL MATCH (e)-[r]-()
            DELETE r, e
            """,
            params={"uuid": entity_uuid}
        )
    else:
        # Just delete the entity node
        await graphiti.driver.execute_query(
            """
            MATCH (e:Entity {uuid: $uuid})
            DETACH DELETE e
            """,
            params={"uuid": entity_uuid}
        )

    return Result(message=f"Entity {entity_uuid} deleted successfully", success=True)


@router.get("/{entity_uuid}/validate", status_code=status.HTTP_200_OK)
async def validate_entity(
    entity_uuid: str,
    graphiti: ZepGraphitiDep,
    user: UserContext = Depends(security_dependency),
):
    """
    Validate an entity against its entity type schema.
    
    Returns validation results and any schema violations.
    """
    from graphiti_core_falkordb.errors import NodeNotFoundError
    
    # Get entity
    try:
        entity = await EntityNode.get_by_uuid(graphiti.driver, entity_uuid)
    except NodeNotFoundError:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Validate user has access to this entity's group
    from graph_service.security import validate_and_authorize_group
    validate_and_authorize_group(entity.group_id, user)
    
    # Get entity type
    entity_type_name = next((label for label in entity.labels if label != 'Entity'), None)
    
    if not entity_type_name:
        return {
            "valid": True,
            "message": "Entity has no specific type, validation skipped",
            "entity_type": None,
            "violations": []
        }
    
    # Get entity type schema
    entity_type = await entity_type_manager.get_entity_type(entity_type_name)
    if not entity_type:
        return {
            "valid": False,
            "message": f"Entity type '{entity_type_name}' not found",
            "entity_type": entity_type_name,
            "violations": [f"Entity type '{entity_type_name}' is not registered"]
        }
    
    # Validate against schema
    violations = []
    try:
        pydantic_models = await entity_type_manager.get_pydantic_models()
        entity_model = pydantic_models.get(entity_type_name)
        
        if entity_model:
            validated_data = entity_model(**(entity.attributes or {}))
            return {
                "valid": True,
                "message": "Entity is valid according to its type schema",
                "entity_type": entity_type_name,
                "violations": [],
                "validated_attributes": validated_data.model_dump()
            }
    except ValidationError as e:
        violations = [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
    
    return {
        "valid": len(violations) == 0,
        "message": "Entity validation completed",
        "entity_type": entity_type_name,
        "violations": violations
    }
