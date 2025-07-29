"""
Entity Type Management Router
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from graph_service.dto import (
    RegisterEntityTypeRequest,
    UpdateEntityTypeRequest,
    EntityTypeResponse,
    EntityTypeListResponse,
    Result,
)
from graph_service.entity_type_manager import entity_type_manager
from graphiti_core_falkordb.errors import EntityTypeValidationError

router = APIRouter(prefix="/entity-types", tags=["entity-types"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=EntityTypeResponse)
async def register_entity_type(request: RegisterEntityTypeRequest):
    """
    Register a new custom entity type.

    This endpoint allows you to define a new entity type with custom fields
    that can be used when adding episodes to the knowledge graph.
    """
    try:
        return await entity_type_manager.register_entity_type(request)
    except ValueError as e:
        # Check if it's a duplicate entity type error
        if "already exists" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        else:
            # All other ValueError are validation errors
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except EntityTypeValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to register entity type: {str(e)}")


@router.get("/", response_model=EntityTypeListResponse)
async def list_entity_types():
    """
    List all registered entity types.
    
    Returns a list of all custom entity types that have been registered
    in the system along with their schemas and metadata.
    """
    try:
        entity_types = await entity_type_manager.list_entity_types()
        return EntityTypeListResponse(
            entity_types=entity_types,
            total=len(entity_types)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list entity types: {str(e)}")


@router.get("/{name}", response_model=EntityTypeResponse)
async def get_entity_type(name: str):
    """
    Get a specific entity type by name.
    
    Returns the complete definition of an entity type including its
    schema, fields, and metadata.
    """
    try:
        entity_type = await entity_type_manager.get_entity_type(name)
        if not entity_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity type '{name}' not found")
        return entity_type
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get entity type: {str(e)}")


@router.put("/{name}", response_model=EntityTypeResponse)
async def update_entity_type(name: str, request: UpdateEntityTypeRequest):
    """
    Update an existing entity type.

    Allows you to modify the description and fields of an existing entity type.
    Note that updating an entity type may affect existing entities of that type.
    """
    try:
        updated_entity_type = await entity_type_manager.update_entity_type(name, request)
        if not updated_entity_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity type '{name}' not found")
        return updated_entity_type
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except EntityTypeValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update entity type: {str(e)}")


@router.delete("/{name}", response_model=Result)
async def delete_entity_type(name: str):
    """
    Delete an entity type.
    
    Removes the entity type definition from the system. Note that this
    does not affect existing entities that were created with this type.
    """
    try:
        deleted = await entity_type_manager.delete_entity_type(name)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity type '{name}' not found")
        return Result(message=f"Entity type '{name}' deleted successfully", success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete entity type: {str(e)}")


@router.get("/{name}/schema")
async def get_entity_type_schema(name: str):
    """
    Get the JSON schema for a specific entity type.
    
    Returns the JSON schema representation that can be used for
    validation or documentation purposes.
    """
    try:
        entity_type = await entity_type_manager.get_entity_type(name)
        if not entity_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity type '{name}' not found")
        return entity_type.json_schema
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get entity type schema: {str(e)}")
