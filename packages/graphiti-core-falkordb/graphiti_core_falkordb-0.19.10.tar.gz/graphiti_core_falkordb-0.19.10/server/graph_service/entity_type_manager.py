"""
Entity Type Manager for handling custom entity type definitions.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field, create_model
from graphiti_core_falkordb.utils.datetime_utils import utc_now
from graphiti_core_falkordb.utils.ontology_utils.entity_types_utils import validate_entity_types
from graphiti_core_falkordb.errors import EntityTypeValidationError
from graphiti_core_falkordb.driver.driver import GraphDriver
from graphiti_core_falkordb.llm_client import LLMClient

from .dto.entity_types import (
    EntityTypeField,
    EntityTypeSchema,
    EntityTypeResponse,
    RegisterEntityTypeRequest,
    UpdateEntityTypeRequest,
)


class DiscoveredField(BaseModel):
    """A field discovered from message analysis."""
    name: str = Field(..., description="Field name in snake_case")
    type: str = Field(..., description="Field type (str, int, float, bool)")
    description: str = Field(..., description="Description of what this field represents")
    required: bool = Field(..., description="Whether this field is required")
    example_value: Optional[str] = Field(None, description="Example value from the message")


class DiscoveredEntityType(BaseModel):
    """An entity type discovered from message analysis."""
    name: str = Field(..., description="Entity type name in PascalCase")
    description: str = Field(..., description="Description of what this entity type represents")
    fields: List[DiscoveredField] = Field(..., description="List of fields for this entity type")
    confidence: float = Field(..., description="Confidence score (0.0-1.0) for this entity type")
    visible_by_default: bool = Field(True, description="Whether this entity type should be visible by default in UI")


class EntityDiscoveryResponse(BaseModel):
    """Response from entity type discovery analysis."""
    discovered_entities: List[DiscoveredEntityType] = Field(..., description="List of discovered entity types")
    reasoning: str = Field(..., description="Explanation of the discovery process")


class StoredEntityType:
    """Internal representation of a stored entity type."""
    
    def __init__(
        self,
        name: str,
        description: Optional[str],
        fields: List[EntityTypeField],
        visible_by_default: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.name = name
        self.description = description
        self.fields = fields
        self.visible_by_default = visible_by_default
        self.created_at = created_at or utc_now()
        self.updated_at = updated_at or utc_now()
        self._pydantic_model: Optional[Type[BaseModel]] = None
        self._json_schema: Optional[Dict[str, Any]] = None
    
    def get_pydantic_model(self) -> Type[BaseModel]:
        """Generate and cache the Pydantic model for this entity type."""
        if self._pydantic_model is None:
            self._pydantic_model = self._create_pydantic_model()
        return self._pydantic_model
    
    def get_json_schema(self) -> Dict[str, Any]:
        """Generate and cache the JSON schema for this entity type."""
        if self._json_schema is None:
            model = self.get_pydantic_model()
            self._json_schema = model.model_json_schema()
        return self._json_schema
    
    def _create_pydantic_model(self) -> Type[BaseModel]:
        """Create a Pydantic model from the field definitions."""
        field_definitions = {}
        
        for field in self.fields:
            # Parse the type string to get the actual Python type
            field_type = self._parse_type_string(field.type)
            
            # Create the field definition
            if field.required:
                if field.default is not None:
                    field_definitions[field.name] = (field_type, Field(default=field.default, description=field.description))
                else:
                    field_definitions[field.name] = (field_type, Field(..., description=field.description))
            else:
                default_value = field.default if field.default is not None else None
                field_definitions[field.name] = (Optional[field_type], Field(default=default_value, description=field.description))
        
        # Create the model with a docstring as description
        model = create_model(
            self.name,
            __doc__=self.description,
            **field_definitions
        )
        
        return model
    
    def _parse_type_string(self, type_str: str) -> Type:
        """Parse a type string into a Python type."""
        # Validate type string format
        if not type_str or not isinstance(type_str, str):
            raise ValueError(f"Invalid type string: {type_str}")

        # Handle basic types
        type_mapping = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
        }

        # Remove Optional wrapper if present
        if type_str.startswith('Optional[') and type_str.endswith(']'):
            inner_type = type_str[9:-1]
            if not inner_type:
                raise ValueError(f"Empty Optional type: {type_str}")
            return self._parse_type_string(inner_type)

        # Handle List types
        if type_str.startswith('List[') and type_str.endswith(']'):
            inner_type = type_str[5:-1]
            if not inner_type:
                raise ValueError(f"Empty List type: {type_str}")
            return List[self._parse_type_string(inner_type)]

        # Handle Dict types
        if type_str.startswith('Dict[') and type_str.endswith(']'):
            return dict

        if type_str not in type_mapping:
            raise ValueError(f"Unsupported type: {type_str}. Supported types: {list(type_mapping.keys())}")

        return type_mapping[type_str]
    
    def to_response(self) -> EntityTypeResponse:
        """Convert to response model."""
        return EntityTypeResponse(
            name=self.name,
            description=self.description,
            fields=self.fields,
            visible_by_default=self.visible_by_default,
            created_at=self.created_at,
            updated_at=self.updated_at,
            json_schema=self.get_json_schema(),
        )


class EntityTypeManager:
    """Manages custom entity type definitions with persistent storage."""

    def __init__(self, driver: Optional[GraphDriver] = None, llm_client: Optional[LLMClient] = None):
        self._entity_types: Dict[str, StoredEntityType] = {}
        self._driver = driver
        self._llm_client = llm_client
        self._loaded = False

    def set_driver(self, driver: GraphDriver) -> None:
        """Set the database driver for persistence."""
        self._driver = driver

    def set_llm_client(self, llm_client: LLMClient) -> None:
        """Set the LLM client for auto-discovery."""
        self._llm_client = llm_client

    async def _ensure_loaded(self) -> None:
        """Ensure entity types are loaded from database."""
        if not self._loaded and self._driver:
            await self._load_from_database()
            await self._seed_core_entity_types()
            self._loaded = True

    async def _load_from_database(self) -> None:
        """Load entity types from the database."""
        if not self._driver:
            return

        try:
            records, _, _ = await self._driver.execute_query(
                """
                MATCH (et:EntityType)
                RETURN et.name AS name,
                       et.description AS description,
                       et.fields AS fields,
                       et.visible_by_default AS visible_by_default,
                       et.created_at AS created_at,
                       et.updated_at AS updated_at
                """,
                routing_='r'
            )

            for record in records:
                fields_data = json.loads(record['fields'])
                fields = [EntityTypeField(**field) for field in fields_data]

                # Handle backward compatibility - default to True if field doesn't exist
                visible_by_default = record.get('visible_by_default', True)
                if visible_by_default is None:
                    visible_by_default = True

                stored_type = StoredEntityType(
                    name=record['name'],
                    description=record['description'],
                    fields=fields,
                    visible_by_default=visible_by_default,
                    created_at=datetime.fromisoformat(record['created_at']),
                    updated_at=datetime.fromisoformat(record['updated_at'])
                )
                self._entity_types[record['name']] = stored_type

        except Exception as e:
            # If there's an error loading (e.g., no EntityType nodes exist yet), continue
            pass

    async def _seed_core_entity_types(self) -> None:
        """Seed core entity types for CRM/KMS/IMS use cases if they don't exist."""
        core_entity_types = [
            {
                "name": "Customer",
                "description": "A customer or client of the business",
                "fields": [
                    {"name": "full_name", "type": "str", "description": "Full name of the customer", "required": True},
                    {"name": "email", "type": "str", "description": "Email address", "required": False},
                    {"name": "phone", "type": "str", "description": "Phone number", "required": False},
                    {"name": "company", "type": "str", "description": "Company name", "required": False},
                    {"name": "status", "type": "str", "description": "Customer status: cold_lead, warm_lead, hot_lead, active, churned", "required": False},
                    {"name": "source", "type": "str", "description": "How the customer was acquired", "required": False},
                    {"name": "value", "type": "str", "description": "Customer lifetime value or deal size", "required": False},
                    {"name": "last_contact", "type": "str", "description": "Date of last contact", "required": False},
                    {"name": "next_action", "type": "str", "description": "Next planned action or follow-up", "required": False},
                    {"name": "industry", "type": "str", "description": "Customer's industry", "required": False},
                    {"name": "territory", "type": "str", "description": "Sales territory or region", "required": False},
                    {"name": "profile_image_url", "type": "str", "description": "URL to customer's profile image", "required": False},
                    {"name": "linkedin_url", "type": "str", "description": "LinkedIn profile URL", "required": False},
                    {"name": "website_url", "type": "str", "description": "Customer's personal or company website", "required": False},
                    {"name": "notes", "type": "str", "description": "Additional notes about the customer", "required": False},
                    {"name": "extra", "type": "str", "description": "JSON string for storing custom fields", "default": "{}", "required": False}
                ],
                "visible_by_default": True
            },
            {
                "name": "Project",
                "description": "A business project or initiative",
                "fields": [
                    {"name": "title", "type": "str", "description": "Project name", "required": True},
                    {"name": "description", "type": "str", "description": "Project description", "required": False},
                    {"name": "status", "type": "str", "description": "Project status: planning, active, on_hold, completed, cancelled", "required": False},
                    {"name": "priority", "type": "str", "description": "Project priority: low, medium, high, critical", "required": False},
                    {"name": "deadline", "type": "str", "description": "Project deadline", "required": False},
                    {"name": "start_date", "type": "str", "description": "Project start date", "required": False},
                    {"name": "budget", "type": "str", "description": "Project budget", "required": False},
                    {"name": "actual_cost", "type": "str", "description": "Actual cost incurred", "required": False},
                    {"name": "owner", "type": "str", "description": "Project owner or manager", "required": False},
                    {"name": "team_members", "type": "str", "description": "Team members involved", "required": False},
                    {"name": "client", "type": "str", "description": "Client or stakeholder", "required": False},
                    {"name": "progress", "type": "str", "description": "Completion percentage or progress notes", "required": False},
                    {"name": "risks", "type": "str", "description": "Known risks or issues", "required": False},
                    {"name": "project_url", "type": "str", "description": "URL to project dashboard or workspace", "required": False},
                    {"name": "repository_url", "type": "str", "description": "Code repository URL", "required": False},
                    {"name": "documentation_url", "type": "str", "description": "Project documentation URL", "required": False},
                    {"name": "extra", "type": "str", "description": "JSON string for storing custom fields", "default": "{}", "required": False}
                ],
                "visible_by_default": True
            },
            {
                "name": "Task",
                "description": "A specific task or work item",
                "fields": [
                    {"name": "title", "type": "str", "description": "Task title", "required": True},
                    {"name": "description", "type": "str", "description": "Task description", "required": False},
                    {"name": "status", "type": "str", "description": "Task status: todo, in_progress, review, done, blocked", "required": False},
                    {"name": "priority", "type": "str", "description": "Task priority: low, medium, high, critical", "required": False},
                    {"name": "assignee", "type": "str", "description": "Person assigned to the task", "required": False},
                    {"name": "reporter", "type": "str", "description": "Person who created the task", "required": False},
                    {"name": "due_date", "type": "str", "description": "Task due date", "required": False},
                    {"name": "estimated_hours", "type": "str", "description": "Estimated hours to complete", "required": False},
                    {"name": "actual_hours", "type": "str", "description": "Actual hours spent", "required": False},
                    {"name": "project", "type": "str", "description": "Associated project", "required": False},
                    {"name": "tags", "type": "str", "description": "Task tags or labels", "required": False},
                    {"name": "dependencies", "type": "str", "description": "Task dependencies", "required": False},
                    {"name": "extra", "type": "str", "description": "JSON string for storing custom fields", "default": "{}", "required": False}
                ],
                "visible_by_default": True
            },
            {
                "name": "Company",
                "description": "A business organization or company",
                "fields": [
                    {"name": "company_name", "type": "str", "description": "Company name", "required": True},
                    {"name": "industry", "type": "str", "description": "Industry sector", "required": False},
                    {"name": "location", "type": "str", "description": "Company location", "required": False},
                    {"name": "size", "type": "str", "description": "Company size: startup, small, medium, large, enterprise", "required": False},
                    {"name": "website_url", "type": "str", "description": "Company website URL", "required": False},
                    {"name": "linkedin_url", "type": "str", "description": "Company LinkedIn page URL", "required": False},
                    {"name": "logo_url", "type": "str", "description": "Company logo image URL", "required": False},
                    {"name": "status", "type": "str", "description": "Relationship status: prospect, partner, client, competitor", "required": False},
                    {"name": "notes", "type": "str", "description": "Additional notes about the company", "required": False},
                    {"name": "extra", "type": "str", "description": "JSON string for storing custom fields", "default": "{}", "required": False}
                ],
                "visible_by_default": True
            },
            {
                "name": "Contact",
                "description": "A business contact or person",
                "fields": [
                    {"name": "full_name", "type": "str", "description": "Full name", "required": True},
                    {"name": "title", "type": "str", "description": "Job title", "required": False},
                    {"name": "email", "type": "str", "description": "Email address", "required": False},
                    {"name": "phone", "type": "str", "description": "Phone number", "required": False},
                    {"name": "company", "type": "str", "description": "Company name", "required": False},
                    {"name": "department", "type": "str", "description": "Department", "required": False},
                    {"name": "location", "type": "str", "description": "Office location or address", "required": False},
                    {"name": "relationship", "type": "str", "description": "Relationship type: colleague, client, vendor, partner", "required": False},
                    {"name": "last_contact", "type": "str", "description": "Date of last contact", "required": False},
                    {"name": "preferred_contact", "type": "str", "description": "Preferred contact method", "required": False},
                    {"name": "profile_image_url", "type": "str", "description": "URL to contact's profile image", "required": False},
                    {"name": "linkedin_url", "type": "str", "description": "LinkedIn profile URL", "required": False},
                    {"name": "portfolio_url", "type": "str", "description": "Portfolio or personal website URL", "required": False},
                    {"name": "extra", "type": "str", "description": "JSON string for storing custom fields", "default": "{}", "required": False}
                ],
                "visible_by_default": True
            },
            {
                "name": "Meeting",
                "description": "A business meeting or appointment",
                "fields": [
                    {"name": "title", "type": "str", "description": "Meeting title or subject", "required": True},
                    {"name": "description", "type": "str", "description": "Meeting description or agenda", "required": False},
                    {"name": "date_time", "type": "str", "description": "Meeting date and time", "required": False},
                    {"name": "duration", "type": "str", "description": "Meeting duration", "required": False},
                    {"name": "location", "type": "str", "description": "Meeting location or platform", "required": False},
                    {"name": "attendees", "type": "str", "description": "Meeting attendees", "required": False},
                    {"name": "organizer", "type": "str", "description": "Meeting organizer", "required": False},
                    {"name": "status", "type": "str", "description": "Meeting status: scheduled, in_progress, completed, cancelled", "required": False},
                    {"name": "meeting_type", "type": "str", "description": "Type: client_meeting, team_meeting, interview, presentation", "required": False},
                    {"name": "outcome", "type": "str", "description": "Meeting outcome or decisions", "required": False},
                    {"name": "action_items", "type": "str", "description": "Action items from the meeting", "required": False},
                    {"name": "recording_link", "type": "str", "description": "Link to meeting recording", "required": False},
                    {"name": "extra", "type": "str", "description": "JSON string for storing custom fields", "default": "{}", "required": False}
                ],
                "visible_by_default": True
            },
            {
                "name": "Document",
                "description": "A business document or file",
                "fields": [
                    {"name": "title", "type": "str", "description": "Document title", "required": True},
                    {"name": "content", "type": "str", "description": "Full text content of the document", "required": False},
                    {"name": "description", "type": "str", "description": "Document description or summary", "required": False},
                    {"name": "document_type", "type": "str", "description": "Type: contract, proposal, report, manual, policy, specification, guide", "required": False},
                    {"name": "author", "type": "str", "description": "Document author", "required": False},
                    {"name": "created_date", "type": "str", "description": "Creation date", "required": False},
                    {"name": "last_modified", "type": "str", "description": "Last modification date", "required": False},
                    {"name": "version", "type": "str", "description": "Document version", "required": False},
                    {"name": "status", "type": "str", "description": "Status: draft, review, approved, archived", "required": False},
                    {"name": "file_url", "type": "str", "description": "URL to the document file", "required": False},
                    {"name": "preview_url", "type": "str", "description": "URL to document preview or thumbnail", "required": False},
                    {"name": "edit_url", "type": "str", "description": "URL for editing the document", "required": False},
                    {"name": "tags", "type": "str", "description": "Document tags or categories", "required": False},
                    {"name": "access_level", "type": "str", "description": "Access level: public, internal, confidential", "required": False},
                    {"name": "related_project", "type": "str", "description": "Associated project", "required": False},
                    {"name": "word_count", "type": "str", "description": "Approximate word count", "required": False},
                    {"name": "language", "type": "str", "description": "Document language", "required": False},
                    {"name": "extra", "type": "str", "description": "JSON string for storing custom fields", "default": "{}", "required": False}
                ],
                "visible_by_default": True
            },
            {
                "name": "Deal",
                "description": "A sales deal or opportunity",
                "fields": [
                    {"name": "deal_name", "type": "str", "description": "Deal or opportunity name", "required": True},
                    {"name": "customer", "type": "str", "description": "Customer or prospect", "required": False},
                    {"name": "value", "type": "str", "description": "Deal value or amount", "required": False},
                    {"name": "stage", "type": "str", "description": "Sales stage: lead, qualified, proposal, negotiation, closed_won, closed_lost", "required": False},
                    {"name": "probability", "type": "str", "description": "Probability of closing", "required": False},
                    {"name": "close_date", "type": "str", "description": "Expected close date", "required": False},
                    {"name": "sales_rep", "type": "str", "description": "Assigned sales representative", "required": False},
                    {"name": "lead_source", "type": "str", "description": "Lead source", "required": False},
                    {"name": "competitors", "type": "str", "description": "Known competitors", "required": False},
                    {"name": "next_action", "type": "str", "description": "Next planned action", "required": False},
                    {"name": "notes", "type": "str", "description": "Deal notes and updates", "required": False},
                    {"name": "extra", "type": "str", "description": "JSON string for storing custom fields", "default": "{}", "required": False}
                ],
                "visible_by_default": True
            },
            {
                "name": "Issue",
                "description": "A support issue or ticket",
                "fields": [
                    {"name": "title", "type": "str", "description": "Issue title", "required": True},
                    {"name": "description", "type": "str", "description": "Issue description", "required": False},
                    {"name": "status", "type": "str", "description": "Status: open, in_progress, resolved, closed", "required": False},
                    {"name": "priority", "type": "str", "description": "Priority: low, medium, high, critical", "required": False},
                    {"name": "severity", "type": "str", "description": "Severity level", "required": False},
                    {"name": "reporter", "type": "str", "description": "Person who reported the issue", "required": False},
                    {"name": "assignee", "type": "str", "description": "Person assigned to resolve", "required": False},
                    {"name": "category", "type": "str", "description": "Issue category or type", "required": False},
                    {"name": "created_date", "type": "str", "description": "Date issue was created", "required": False},
                    {"name": "resolution_date", "type": "str", "description": "Date issue was resolved", "required": False},
                    {"name": "resolution", "type": "str", "description": "Resolution details", "required": False},
                    {"name": "customer_impact", "type": "str", "description": "Impact on customer", "required": False},
                    {"name": "extra", "type": "str", "description": "JSON string for storing custom fields", "default": "{}", "required": False}
                ],
                "visible_by_default": True
            },
            {
                "name": "Person",
                "description": "A person or individual",
                "fields": [
                    {"name": "full_name", "type": "str", "description": "Full name", "required": True},
                    {"name": "first_name", "type": "str", "description": "First name", "required": False},
                    {"name": "last_name", "type": "str", "description": "Last name", "required": False},
                    {"name": "email", "type": "str", "description": "Email address", "required": False},
                    {"name": "phone", "type": "str", "description": "Phone number", "required": False},
                    {"name": "title", "type": "str", "description": "Job title or role", "required": False},
                    {"name": "company", "type": "str", "description": "Company or organization", "required": False},
                    {"name": "department", "type": "str", "description": "Department", "required": False},
                    {"name": "location", "type": "str", "description": "Location or address", "required": False},
                    {"name": "bio", "type": "str", "description": "Biography or description", "required": False},
                    {"name": "skills", "type": "str", "description": "Skills or expertise", "required": False},
                    {"name": "interests", "type": "str", "description": "Interests or hobbies", "required": False},
                    {"name": "profile_image_url", "type": "str", "description": "URL to profile image", "required": False},
                    {"name": "linkedin_url", "type": "str", "description": "LinkedIn profile URL", "required": False},
                    {"name": "website_url", "type": "str", "description": "Personal website URL", "required": False},
                    {"name": "extra", "type": "str", "description": "JSON string for storing custom fields", "default": "{}", "required": False}
                ],
                "visible_by_default": True
            }
        ]

        for entity_type_data in core_entity_types:
            # Check if entity type already exists
            if entity_type_data["name"] in self._entity_types:
                continue

            # Convert field data to EntityTypeField objects
            fields = [
                EntityTypeField(
                    name=field["name"],
                    type=field["type"],
                    description=field["description"],
                    required=field["required"],
                    default=field.get("default")
                )
                for field in entity_type_data["fields"]
            ]

            # Create registration request
            request = RegisterEntityTypeRequest(
                name=entity_type_data["name"],
                description=entity_type_data["description"],
                fields=fields,
                visible_by_default=entity_type_data["visible_by_default"]
            )

            try:
                # Register the entity type
                await self.register_entity_type(request)
                print(f"DEBUG: Seeded core entity type: {entity_type_data['name']}")
            except Exception as e:
                # If registration fails (e.g., entity type already exists), continue
                print(f"DEBUG: Failed to seed entity type {entity_type_data['name']}: {e}")
                continue

    async def _save_to_database(self, stored_type: StoredEntityType) -> None:
        """Save an entity type to the database."""
        if not self._driver:
            return

        fields_json = json.dumps([field.model_dump() for field in stored_type.fields])

        await self._driver.execute_query(
            """
            MERGE (et:EntityType {name: $name})
            SET et.description = $description,
                et.fields = $fields,
                et.visible_by_default = $visible_by_default,
                et.created_at = $created_at,
                et.updated_at = $updated_at
            """,
            name=stored_type.name,
            description=stored_type.description,
            fields=fields_json,
            visible_by_default=stored_type.visible_by_default,
            created_at=stored_type.created_at.isoformat(),
            updated_at=stored_type.updated_at.isoformat(),
            routing_='w'
        )

    async def _delete_from_database(self, name: str) -> None:
        """Delete an entity type from the database."""
        if not self._driver:
            return

        await self._driver.execute_query(
            """
            MATCH (et:EntityType {name: $name})
            DELETE et
            """,
            name=name,
            routing_='w'
        )

    def _validate_entity_type_name(self, name: str) -> None:
        """Validate entity type name."""
        if not name or not isinstance(name, str):
            raise ValueError("Entity type name must be a non-empty string")

        if not name.isidentifier():
            raise ValueError(f"Entity type name '{name}' must be a valid Python identifier")

        if name.lower() in ['entity', 'node', 'edge', 'episode']:
            raise ValueError(f"Entity type name '{name}' conflicts with reserved names")

    def _validate_field_name(self, field_name: str) -> None:
        """Validate field name."""
        if not field_name or not isinstance(field_name, str):
            raise ValueError("Field name must be a non-empty string")

        if not field_name.isidentifier():
            raise ValueError(f"Field name '{field_name}' must be a valid Python identifier")

        # Check against EntityNode protected fields
        from graphiti_core_falkordb.nodes import EntityNode
        protected_fields = set(EntityNode.model_fields.keys())
        if field_name in protected_fields:
            raise ValueError(f"Field name '{field_name}' conflicts with protected EntityNode field")

    def _validate_fields(self, fields: List[EntityTypeField]) -> None:
        """Validate field definitions."""
        if not fields:
            raise ValueError("Entity type must have at least one field")

        field_names = set()
        for field in fields:
            self._validate_field_name(field.name)

            if field.name in field_names:
                raise ValueError(f"Duplicate field name: {field.name}")
            field_names.add(field.name)

            # Validate type string by attempting to parse it
            try:
                # Create a temporary instance to validate the type string
                temp_instance = StoredEntityType("temp", None, [])
                temp_instance._parse_type_string(field.type)
            except ValueError as e:
                raise ValueError(f"Invalid type for field '{field.name}': {e}")
    
    async def register_entity_type(self, request: RegisterEntityTypeRequest) -> EntityTypeResponse:
        """Register a new entity type."""
        await self._ensure_loaded()

        # Validate entity type name
        self._validate_entity_type_name(request.name)

        if request.name in self._entity_types:
            raise ValueError(f"Entity type '{request.name}' already exists")

        # Validate fields
        self._validate_fields(request.fields)

        # Add the 'extra' field automatically to all entity types for custom fields
        from graph_service.dto.entity_types import EntityTypeField
        extra_field = EntityTypeField(
            name="extra",
            type="str",
            description="JSON string for storing custom fields",
            default="{}",
            required=False
        )

        # Check if 'extra' field already exists, if not add it
        field_names = [field.name for field in request.fields]
        if "extra" not in field_names:
            request.fields.append(extra_field)

        # Create stored type and validate Pydantic model creation
        stored_type = StoredEntityType(
            name=request.name,
            description=request.description,
            fields=request.fields,
            visible_by_default=request.visible_by_default,
        )

        # Create the Pydantic model to validate it
        try:
            pydantic_model = stored_type.get_pydantic_model()
            # Create a dummy instance for validation with minimal required fields
            dummy_data = {}
            for field in stored_type.fields:
                if field.required:
                    # Provide dummy values for required fields based on type
                    if field.type == "str":
                        dummy_data[field.name] = "dummy_value"
                    elif field.type == "int":
                        dummy_data[field.name] = 0
                    elif field.type == "float":
                        dummy_data[field.name] = 0.0
                    elif field.type == "bool":
                        dummy_data[field.name] = False
                    else:
                        dummy_data[field.name] = None

            dummy_instance = pydantic_model(**dummy_data)
            # Validate against EntityNode protected fields
            validate_entity_types({request.name: dummy_instance})
        except Exception as e:
            raise EntityTypeValidationError(request.name, str(e))

        # Save to database and memory
        await self._save_to_database(stored_type)
        self._entity_types[request.name] = stored_type
        return stored_type.to_response()
    
    async def get_entity_type(self, name: str) -> Optional[EntityTypeResponse]:
        """Get an entity type by name."""
        await self._ensure_loaded()
        stored_type = self._entity_types.get(name)
        return stored_type.to_response() if stored_type else None

    async def list_entity_types(self) -> List[EntityTypeResponse]:
        """List all registered entity types."""
        await self._ensure_loaded()
        return [stored_type.to_response() for stored_type in self._entity_types.values()]
    
    async def update_entity_type(self, name: str, request: UpdateEntityTypeRequest) -> Optional[EntityTypeResponse]:
        """Update an existing entity type."""
        await self._ensure_loaded()
        stored_type = self._entity_types.get(name)
        if not stored_type:
            return None

        # Validate updated fields if provided
        if request.fields is not None:
            self._validate_fields(request.fields)

        # Update fields
        if request.description is not None:
            stored_type.description = request.description
        if request.fields is not None:
            stored_type.fields = request.fields
        if request.visible_by_default is not None:
            stored_type.visible_by_default = request.visible_by_default

        stored_type.updated_at = utc_now()

        # Clear cached model and schema
        stored_type._pydantic_model = None
        stored_type._json_schema = None

        # Validate the updated entity type
        try:
            pydantic_model = stored_type.get_pydantic_model()
            # Create a dummy instance for validation with minimal required fields
            dummy_data = {}
            for field in stored_type.fields:
                if field.required:
                    # Provide dummy values for required fields based on type
                    if field.type == "str":
                        dummy_data[field.name] = "dummy_value"
                    elif field.type == "int":
                        dummy_data[field.name] = 0
                    elif field.type == "float":
                        dummy_data[field.name] = 0.0
                    elif field.type == "bool":
                        dummy_data[field.name] = False
                    else:
                        dummy_data[field.name] = None

            dummy_instance = pydantic_model(**dummy_data)
            validate_entity_types({name: dummy_instance})
        except Exception as e:
            raise EntityTypeValidationError(name, str(e))

        # Save to database
        await self._save_to_database(stored_type)
        return stored_type.to_response()
    
    async def delete_entity_type(self, name: str) -> bool:
        """Delete an entity type."""
        await self._ensure_loaded()
        if name in self._entity_types:
            await self._delete_from_database(name)
            del self._entity_types[name]
            return True
        return False

    async def get_pydantic_models(self, names: Optional[List[str]] = None) -> Dict[str, Type[BaseModel]]:
        """Get Pydantic models for specified entity types or all if names is None."""
        await self._ensure_loaded()
        if names is None:
            return {name: stored_type.get_pydantic_model() for name, stored_type in self._entity_types.items()}

        models = {}
        for name in names:
            stored_type = self._entity_types.get(name)
            if stored_type:
                models[name] = stored_type.get_pydantic_model()
        return models

    async def discover_entity_types_from_message(self, message_content: str) -> List[DiscoveredEntityType]:
        """Discover potential entity types from a message using LLM analysis."""
        print(f"DEBUG: discover_entity_types_from_message called with: {message_content}")
        if not self._llm_client:
            print("DEBUG: No LLM client available")
            return []
        print("DEBUG: LLM client is available")

        await self._ensure_loaded()
        existing_types = list(self._entity_types.keys())

        prompt = f"""
Analyze the following message and identify potential entity types that could be extracted.
IMPORTANT: Be extremely restrictive - only suggest entity types that are core business entities suitable for a CRM, KMS, or IMS system.

Existing entity types: {existing_types}

Message: "{message_content}"

STRICT GUIDELINES:
1. ONLY suggest entity types from this approved list of core business categories:
   - Customer, Client, Lead, Prospect (customer-related entities)
   - Project, Initiative, Campaign (project-related entities)
   - Task, Issue, Ticket, Request (work item entities)
   - Company, Organization, Vendor, Partner (business entities)
   - Contact, Person, Employee (people entities)
   - Product, Service, Offering (business offerings)
   - Meeting, Interview, Event, Appointment (scheduled activities)
   - Deal, Order, Invoice, Contract (transactional entities)
   - Document, Report, Manual, Policy (documentation entities)

2. DO NOT suggest entity types for:
   - Technical concepts (APIs, databases, systems, logs)
   - Temporary data (sessions, tokens, IDs)
   - Abstract concepts (weather, emotions, general topics)
   - Location-only entities (use location as a field instead)
   - Time-only entities (use date/time as fields instead)
   - Simple attributes that should be fields (colors, sizes, categories)

3. REUSE existing entity types whenever possible - do not create variations
   - Use "Customer" instead of "Client", "Lead", "Prospect" unless truly different
   - Use "Contact" instead of "Person", "Employee" unless role-specific fields needed
   - Use "Company" instead of "Organization", "Business" unless different structure needed

4. Require HIGH CONFIDENCE (>= 0.85) - only suggest if you're very certain the entity:
   - Has clear business value for tracking
   - Contains structured information worth extracting
   - Would be actively managed by business users
   - Fits standard CRM/KMS/IMS patterns

5. Field requirements:
   - Must include relevant status fields for entities that change state
   - Field names in snake_case (e.g., full_name, company_name)
   - Entity type names in PascalCase (e.g., Customer, Project)
   - Focus on actionable business fields, not descriptive text

APPROVED ENTITY TYPE EXAMPLES:
- Customer: full_name, email, phone, company, status (cold_lead/warm_lead/active/churned), source, value, territory, profile_image_url, linkedin_url
- Project: name, description, status (planning/active/completed), priority, deadline, owner, budget, progress, project_url, repository_url
- Task: title, description, status (todo/in_progress/done), priority, assignee, due_date, project
- Company: company_name, industry, location, size, website_url, linkedin_url, logo_url, status (prospect/partner/client)
- Contact: full_name, title, email, phone, company, department, relationship, last_contact, profile_image_url, linkedin_url
- Meeting: title, date_time, attendees, organizer, status (scheduled/completed), meeting_type, outcome, recording_link
- Interview: candidate_name, position, interviewer, status (scheduled/completed), rating, feedback
- Document: title, content, document_type, author, status (draft/approved), version, access_level, file_url, preview_url
- Deal: deal_name, customer, value, stage (lead/qualified/closed_won), probability, sales_rep
- Issue: title, status (open/resolved), priority, assignee, category, resolution

Return only entity types with confidence >= 0.85 and that match the approved business categories above.
If the message doesn't contain clear business entities worth tracking, return an empty list.
"""

        try:
            print("DEBUG: Calling LLM for entity discovery")
            from graphiti_core_falkordb.prompts.models import Message
            messages = [Message(role="user", content=prompt)]
            response_dict = await self._llm_client.generate_response(
                messages,
                response_model=EntityDiscoveryResponse
            )
            print(f"DEBUG: LLM response dict: {response_dict}")

            # Convert dictionary response to EntityDiscoveryResponse object
            response = EntityDiscoveryResponse(**response_dict)
            print(f"DEBUG: Parsed response: {response}")

            # Filter by confidence and business relevance
            filtered_entities = []
            for entity in response.discovered_entities:
                if entity.confidence >= 0.85 and self._is_valid_business_entity(entity):
                    filtered_entities.append(entity)

            print(f"DEBUG: Filtered business entities: {filtered_entities}")
            return filtered_entities

        except Exception as e:
            # If LLM analysis fails, return empty list
            print(f"DEBUG: LLM analysis failed: {e}")
            return []

    def _is_valid_business_entity(self, entity: DiscoveredEntityType) -> bool:
        """Validate that an entity type fits core business patterns."""
        # Define approved entity type categories
        approved_categories = {
            # Customer-related
            'customer', 'client', 'lead', 'prospect',
            # Project-related
            'project', 'initiative', 'campaign',
            # Work items
            'task', 'issue', 'ticket', 'request',
            # Business entities
            'company', 'organization', 'vendor', 'partner',
            # People
            'contact', 'person', 'employee',
            # Offerings
            'product', 'service', 'offering',
            # Activities
            'event', 'meeting', 'appointment', 'interview',
            # Transactions
            'order', 'invoice', 'contract', 'deal',
            # Documentation
            'document', 'report', 'manual', 'policy'
        }

        # Check if entity name matches approved categories
        entity_name_lower = entity.name.lower()
        if not any(category in entity_name_lower for category in approved_categories):
            print(f"DEBUG: Entity '{entity.name}' rejected - not in approved categories")
            return False

        # Reject technical/system entities
        technical_keywords = [
            'log', 'debug', 'system', 'api', 'database', 'config', 'session',
            'token', 'id', 'reference', 'temp', 'cache', 'queue', 'batch'
        ]

        if any(keyword in entity_name_lower for keyword in technical_keywords):
            print(f"DEBUG: Entity '{entity.name}' rejected - contains technical keywords")
            return False

        # Require meaningful fields (not just name/description)
        meaningful_fields = [field for field in entity.fields
                           if field.name not in ['name', 'description', 'summary']]

        if len(meaningful_fields) < 2:
            print(f"DEBUG: Entity '{entity.name}' rejected - insufficient meaningful fields")
            return False

        print(f"DEBUG: Entity '{entity.name}' approved as valid business entity")
        return True

    def _fix_protected_field_names(self, discovered_entity: DiscoveredEntityType) -> DiscoveredEntityType:
        """Fix field names that conflict with protected EntityNode fields."""
        from graphiti_core_falkordb.nodes import EntityNode
        protected_fields = set(EntityNode.model_fields.keys())

        # Mapping for common protected field renames
        field_rename_map = {
            'name': 'full_name',
            'uuid': 'entity_id',
            'group_id': 'group_identifier',
            'labels': 'categories',
            'created_at': 'creation_date',
            'summary': 'description',
            'attributes': 'properties'
        }

        fixed_fields = []
        for field in discovered_entity.fields:
            if field.name in protected_fields:
                # Try to use the mapping first
                new_name = field_rename_map.get(field.name, f"{field.name}_value")
                print(f"DEBUG: Renaming protected field '{field.name}' to '{new_name}'")

                # Create new field with renamed field
                fixed_field = DiscoveredField(
                    name=new_name,
                    type=field.type,
                    description=field.description,
                    required=field.required,
                    example_value=field.example_value
                )
                fixed_fields.append(fixed_field)
            else:
                fixed_fields.append(field)

        # Return new entity with fixed fields
        return DiscoveredEntityType(
            name=discovered_entity.name,
            description=discovered_entity.description,
            fields=fixed_fields,
            confidence=discovered_entity.confidence,
            visible_by_default=discovered_entity.visible_by_default
        )

    async def auto_register_discovered_entities(self, discovered_entities: List[DiscoveredEntityType]) -> List[str]:
        """Automatically register discovered entity types that don't already exist."""
        print(f"DEBUG: auto_register_discovered_entities called with {len(discovered_entities)} entities")
        registered_types = []

        for entity in discovered_entities:
            print(f"DEBUG: Processing entity type: {entity.name}")

            # Additional validation before registration
            if not self._is_valid_business_entity(entity):
                print(f"DEBUG: Entity type {entity.name} failed business validation, skipping")
                continue

            # Check if entity type already exists
            if entity.name in self._entity_types:
                print(f"DEBUG: Entity type {entity.name} already exists, skipping")
                continue

            # Fix any protected field names
            fixed_entity = self._fix_protected_field_names(entity)

            # Convert discovered fields to EntityTypeField objects
            fields = []
            for field in fixed_entity.fields:
                fields.append(EntityTypeField(
                    name=field.name,
                    type=field.type,
                    description=field.description,
                    required=field.required,
                    default=getattr(field, 'default', None)
                ))

            # Create registration request
            request = RegisterEntityTypeRequest(
                name=fixed_entity.name,
                description=fixed_entity.description,
                fields=fields,
                visible_by_default=fixed_entity.visible_by_default
            )

            try:
                print(f"DEBUG: Attempting to register entity type: {fixed_entity.name}")
                await self.register_entity_type(request)
                registered_types.append(fixed_entity.name)
                print(f"DEBUG: Successfully registered entity type: {fixed_entity.name}")
            except Exception as e:
                # If registration fails, continue with other entities
                print(f"DEBUG: Failed to register entity type {fixed_entity.name}: {e}")
                continue

        print(f"DEBUG: auto_register_discovered_entities returning: {registered_types}")
        return registered_types

    async def discover_and_register_from_message(self, message_content: str) -> List[str]:
        """Discover and automatically register entity types from a message."""
        discovered = await self.discover_entity_types_from_message(message_content)
        if discovered:
            return await self.auto_register_discovered_entities(discovered)
        return []


# Global instance - driver will be set during app startup
entity_type_manager = EntityTypeManager()
