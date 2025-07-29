# Entity Types API

The Entity Types API allows you to define and manage custom entity types for use in the Graphiti knowledge graph. Custom entity types enable more precise entity extraction and structured data capture when processing episodes.

## Overview

Custom entity types are defined using Pydantic-style field definitions and can be used when adding episodes to the knowledge graph. This allows for:

- More precise entity extraction based on domain-specific types
- Structured attribute capture for entities
- Better organization and querying of knowledge graph data

## API Endpoints

### Register Entity Type

**POST** `/entity-types/`

Register a new custom entity type.

#### Request Body

```json
{
  "name": "Person",
  "description": "A human person mentioned in conversations",
  "fields": [
    {
      "name": "first_name",
      "type": "str",
      "description": "First name of the person",
      "required": true
    },
    {
      "name": "last_name", 
      "type": "str",
      "description": "Last name of the person",
      "required": false,
      "default": null
    },
    {
      "name": "age",
      "type": "int",
      "description": "Age in years",
      "required": false
    }
  ]
}
```

#### Response

```json
{
  "name": "Person",
  "description": "A human person mentioned in conversations",
  "fields": [...],
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "json_schema": {
    "type": "object",
    "properties": {
      "first_name": {
        "type": "string",
        "description": "First name of the person"
      },
      ...
    },
    "required": ["first_name"]
  }
}
```

### List Entity Types

**GET** `/entity-types/`

List all registered entity types.

#### Response

```json
{
  "entity_types": [
    {
      "name": "Person",
      "description": "A human person",
      "fields": [...],
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z",
      "json_schema": {...}
    }
  ],
  "total": 1
}
```

### Get Entity Type

**GET** `/entity-types/{name}`

Get a specific entity type by name.

#### Response

```json
{
  "name": "Person",
  "description": "A human person",
  "fields": [...],
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "json_schema": {...}
}
```

### Update Entity Type

**PUT** `/entity-types/{name}`

Update an existing entity type.

#### Request Body

```json
{
  "description": "Updated description",
  "fields": [
    {
      "name": "full_name",
      "type": "str", 
      "description": "Full name of the person",
      "required": true
    }
  ]
}
```

### Delete Entity Type

**DELETE** `/entity-types/{name}`

Delete an entity type.

#### Response

```json
{
  "message": "Entity type 'Person' deleted successfully",
  "success": true
}
```

### Get Entity Type Schema

**GET** `/entity-types/{name}/schema`

Get the JSON schema for an entity type.

#### Response

```json
{
  "type": "object",
  "properties": {
    "first_name": {
      "type": "string",
      "description": "First name of the person"
    }
  },
  "required": ["first_name"]
}
```

## Using Entity Types with Messages

### Messages with Entity Types (Dedicated Endpoint)

**POST** `/messages-with-entity-types`

Add messages with specific entity types.

#### Request Body

```json
{
  "group_id": "conversation_123",
  "messages": [
    {
      "content": "Hi, I'm John Smith, a 30-year-old software engineer",
      "role_type": "user",
      "role": "John"
    }
  ],
  "entity_type_names": ["Person", "Organization"],
  "excluded_entity_types": ["Location"]
}
```

### Messages with Query Parameters

**POST** `/messages?entity_type_names=Person,Organization&excluded_entity_types=Location`

Add messages using query parameters to specify entity types.

## Field Types

Supported field types for entity definitions:

- `str` - String values
- `int` - Integer values  
- `float` - Floating point values
- `bool` - Boolean values
- `list` - List values
- `dict` - Dictionary values
- `List[str]` - List of strings
- `Optional[str]` - Optional string (can be null)

## Validation Rules

### Entity Type Names
- Must be valid Python identifiers
- Cannot conflict with reserved names: `entity`, `node`, `edge`, `episode`
- Must be unique

### Field Names
- Must be valid Python identifiers
- Cannot conflict with protected EntityNode fields: `uuid`, `name`, `group_id`, `labels`, `created_at`, `name_embedding`, `summary`, `attributes`
- Must be unique within the entity type

### Field Types
- Must be one of the supported types
- Type strings must be properly formatted (e.g., `Optional[str]`, `List[int]`)

## Examples

### Complete Example: Customer Support System

```python
import requests

# Register entity types
person_type = {
    "name": "Customer",
    "description": "A customer in our support system",
    "fields": [
        {
            "name": "customer_id",
            "type": "str",
            "description": "Unique customer identifier",
            "required": true
        },
        {
            "name": "tier",
            "type": "str", 
            "description": "Customer tier (bronze, silver, gold)",
            "required": false
        },
        {
            "name": "satisfaction_score",
            "type": "int",
            "description": "Customer satisfaction score 1-10",
            "required": false
        }
    ]
}

issue_type = {
    "name": "SupportIssue",
    "description": "A customer support issue",
    "fields": [
        {
            "name": "issue_type",
            "type": "str",
            "description": "Type of issue (billing, technical, etc.)",
            "required": true
        },
        {
            "name": "priority",
            "type": "str",
            "description": "Issue priority (low, medium, high, critical)",
            "required": true
        },
        {
            "name": "resolved",
            "type": "bool",
            "description": "Whether the issue is resolved",
            "required": false,
            "default": false
        }
    ]
}

# Register the types
requests.post("http://localhost:8000/entity-types/", json=person_type)
requests.post("http://localhost:8000/entity-types/", json=issue_type)

# Use them in messages
message_data = {
    "group_id": "support_session_123",
    "messages": [
        {
            "content": "Customer John Doe (ID: CUST001, Gold tier) reported a critical billing issue with his account",
            "role_type": "system",
            "role": "Support System"
        }
    ],
    "entity_type_names": ["Customer", "SupportIssue"]
}

requests.post("http://localhost:8000/messages-with-entity-types", json=message_data)
```

This will extract structured entities with the defined attributes, enabling richer knowledge graph representation and more precise querying.
