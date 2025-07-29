# graph-service

Graph service is a fast api server implementing the [graphiti](https://github.com/getzep/graphiti) package.


## Running Instructions

1. Ensure you have Docker and Docker Compose installed on your system.

2. Add `zepai/graphiti:latest` to your service setup

3. Make sure to pass the following environment variables to the service

   ```
   OPENAI_API_KEY=your_openai_api_key
   NEO4J_USER=your_neo4j_user
   NEO4J_PASSWORD=your_neo4j_password
   NEO4J_PORT=your_neo4j_port
   ```

4. This service depends on having access to a neo4j instance, you may wish to add a neo4j image to your service setup as well. Or you may wish to use neo4j cloud or a desktop version if running this locally.

   An example of docker compose setup may look like this:

   ```yml
      version: '3.8'

      services:
      graph:
         image: zepai/graphiti:latest
         ports:
            - "8000:8000"
         
         environment:
            - OPENAI_API_KEY=${OPENAI_API_KEY}
            - NEO4J_URI=bolt://neo4j:${NEO4J_PORT}
            - NEO4J_USER=${NEO4J_USER}
            - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      neo4j:
         image: neo4j:5.22.0
         
         ports:
            - "7474:7474"  # HTTP
            - "${NEO4J_PORT}:${NEO4J_PORT}"  # Bolt
         volumes:
            - neo4j_data:/data
         environment:
            - NEO4J_AUTH=${NEO4J_USER}/${NEO4J_PASSWORD}

      volumes:
      neo4j_data:
   ```

5. Once you start the service, it will be available at `http://localhost:8000` (or the port you have specified in the docker compose file).

6. You may access the swagger docs at `http://localhost:8000/docs`. You may also access redocs at `http://localhost:8000/redoc`.

7. You may also access the neo4j browser at `http://localhost:7474` (the port depends on the neo4j instance you are using).

## Features

### Custom Entity Types

The graph service now supports custom entity types that allow you to define domain-specific entities with structured attributes. This enables more precise entity extraction and better organization of your knowledge graph data.

#### Key Features:
- **Define Custom Schemas**: Create entity types with custom fields and validation
- **Type-Safe Extraction**: Use Pydantic models for structured entity extraction
- **Flexible Integration**: Use entity types with existing message endpoints
- **Full CRUD Operations**: Create, read, update, and delete entity type definitions

#### Quick Example:

```bash
# Register a custom entity type
curl -X POST "http://localhost:8000/entity-types/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Person",
    "description": "A human person",
    "fields": [
      {
        "name": "first_name",
        "type": "str",
        "description": "First name",
        "required": true
      },
      {
        "name": "age",
        "type": "int",
        "description": "Age in years",
        "required": false
      }
    ]
  }'

# Use the entity type when adding messages
curl -X POST "http://localhost:8000/messages-with-entity-types" \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": "conversation_123",
    "messages": [
      {
        "content": "Hi, I am John Smith and I am 30 years old",
        "role_type": "user"
      }
    ],
    "entity_type_names": ["Person"]
  }'
```

For detailed documentation, see [Entity Types API Documentation](docs/entity_types_api.md).

## Entity Pagination and Sorting

The Graphiti server provides powerful pagination and sorting capabilities for entity retrieval, allowing you to efficiently browse large datasets and organize entities by various criteria.

### Features

- **Page-based pagination**: Navigate through entities using page numbers
- **Cursor-based pagination**: Use entity UUIDs as cursors for consistent pagination
- **Multi-field sorting**: Sort by standard fields (name, created_at, summary, uuid)
- **Custom attribute sorting**: Sort by any custom attribute defined in entity types
- **Flexible page sizes**: Configure page sizes from 1 to 100 entities per page
- **Metadata**: Get pagination metadata including total counts and navigation info

### Quick Examples

#### Basic Pagination
```bash
# Get first page of entities (default: 20 per page, sorted by created_at desc)
curl "http://localhost:8000/entities/my_group/paginated"

# Get second page with 10 entities per page
curl "http://localhost:8000/entities/my_group/paginated?page=2&page_size=10"
```

#### Sorting by Standard Fields
```bash
# Sort by name ascending
curl "http://localhost:8000/entities/my_group/paginated?sort_by=name&sort_order=asc"

# Sort by creation date descending (default)
curl "http://localhost:8000/entities/my_group/paginated?sort_by=created_at&sort_order=desc"
```

#### Sorting by Custom Attributes
```bash
# Sort by a custom 'age' attribute
curl "http://localhost:8000/entities/my_group/paginated?attribute_sort_field=age&sort_order=desc"

# Sort by department with pagination
curl "http://localhost:8000/entities/my_group/paginated?attribute_sort_field=department&sort_order=asc&page_size=50"
```

#### Cursor-based Pagination
```bash
# Use cursor for consistent pagination (useful for real-time data)
curl "http://localhost:8000/entities/my_group/paginated?cursor=uuid-of-last-entity&page_size=20"
```

#### Get Available Sort Fields
```bash
# Discover what fields are available for sorting
curl "http://localhost:8000/entities/my_group/sort-fields"
```

### Response Format

The paginated endpoint returns a structured response with entities and metadata:

```json
{
  "entities": [
    {
      "uuid": "entity-uuid",
      "name": "Entity Name",
      "summary": "Entity summary",
      "attributes": {
        "custom_field": "value",
        "age": 25
      },
      "labels": ["Entity", "Person"],
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "has_next": true,
    "has_previous": false,
    "count": 20,
    "next_cursor": "next-entity-uuid",
    "previous_cursor": null
  },
  "total_count": 150
}
```

## API Endpoints

### Core Endpoints
- `POST /messages` - Add messages to the knowledge graph
- `POST /entity-node` - Add individual entity nodes
- `POST /search` - Search for facts in the knowledge graph
- `GET /episodes/{group_id}` - Retrieve episodes for a group

### Entity Retrieval
- `GET /entities/{group_id}` - Get all entities for a group (basic)
- `GET /entities/{group_id}/paginated` - Get entities with pagination and sorting
- `GET /entities/{group_id}/sort-fields` - Get available fields for sorting entities

### Entity Type Management
- `POST /entity-types/` - Register new entity type
- `GET /entity-types/` - List all entity types
- `GET /entity-types/{name}` - Get specific entity type
- `PUT /entity-types/{name}` - Update entity type
- `DELETE /entity-types/{name}` - Delete entity type
- `POST /messages-with-entity-types` - Add messages with custom entity types

### Documentation
- `GET /docs` - Swagger/OpenAPI documentation
- `GET /redoc` - ReDoc documentation