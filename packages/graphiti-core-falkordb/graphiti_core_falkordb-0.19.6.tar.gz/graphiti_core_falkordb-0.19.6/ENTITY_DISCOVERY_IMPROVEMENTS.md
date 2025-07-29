# Entity Discovery Improvements

## Overview

This document outlines the improvements made to entity discovery in the Graphiti system, focusing on visibility suggestions and status field examples to enhance user experience.

## Key Features Implemented

### 1. Entity Type Visibility Settings

**What it does:** Allows entity types to be marked as visible or hidden by default in the UI.

**Files modified:**
- `server/graph_service/dto/entity_types.py` - Added `visible_by_default` field to DTOs
- `server/graph_service/entity_type_manager.py` - Updated storage and discovery logic
- `server/graph_service/routers/retrieve.py` - Added visibility filtering to endpoints

**Key changes:**
- Added `visible_by_default: bool` field to `EntityTypeField`, `RegisterEntityTypeRequest`, `UpdateEntityTypeRequest`, and `EntityTypeResponse`
- Updated `StoredEntityType` class to handle visibility with backward compatibility
- Modified database operations to store and retrieve visibility settings
- Enhanced entity listing endpoints with visibility filtering

### 2. Smart Visibility Suggestions

**What it does:** Automatically suggests whether entity types should be visible based on their usefulness to users.

**Logic implemented:**
- **Visible by default:** Customer, Client, User, Person, Project, Task, Issue, Ticket, Company, Organization, Product, Service, Event, Meeting, Appointment
- **Hidden by default:** System IDs, Reference numbers, Log entries, Debug info, Internal configuration, Temporary data

**Example prompt guidelines:**
```
- Set visible_by_default=true for entity types users would want to see prominently:
  * Customer, Client, User, Person (people entities)
  * Project, Task, Issue, Ticket (work items)
  * Company, Organization (business entities)
  * Product, Service (offerings)
  * Event, Meeting, Appointment (activities)
- Set visible_by_default=false for internal/technical entities:
  * System IDs, Reference numbers
  * Log entries, Debug info
  * Internal configuration data
  * Temporary or derived data
```

### 3. Status Field Examples

**What it does:** Provides relevant status field examples for entities that commonly change state.

**Status examples by entity type:**
- **Customer:** `cold_lead`, `warm_lead`, `hot_lead`, `active`, `churned`
- **Task:** `todo`, `in_progress`, `review`, `done`, `blocked`
- **Project:** `planning`, `active`, `on_hold`, `completed`, `cancelled`
- **Issue/Ticket:** `open`, `in_progress`, `resolved`, `closed`
- **Order:** `pending`, `processing`, `shipped`, `delivered`, `cancelled`
- **Event:** `planned`, `confirmed`, `in_progress`, `completed`, `cancelled`

### 4. Enhanced Entity Listing

**What it does:** Adds filtering capabilities to entity retrieval endpoints.

**New query parameters:**
- `visible_only`: Filter by visibility (True=only visible entities, False=only hidden entities, None=all entities)
- `entity_type`: Filter by entity type name (e.g., "Customer", "Project", "Task")

**Example usage:**
```bash
# Get only visible entities
GET /entities/my_group/paginated?visible_only=true

# Get only Customer entities
GET /entities/my_group/paginated?entity_type=Customer

# Get hidden Task entities
GET /entities/my_group/paginated?entity_type=Task&visible_only=false
```

## Technical Implementation Details

### Database Schema Changes

The `EntityType` nodes in Neo4j now include a `visible_by_default` field:

```cypher
MERGE (et:EntityType {name: $name})
SET et.description = $description,
    et.fields = $fields,
    et.visible_by_default = $visible_by_default,
    et.created_at = $created_at,
    et.updated_at = $updated_at
```

### Backward Compatibility

- Existing entity types without the `visible_by_default` field default to `true` (visible)
- The loading logic handles missing fields gracefully
- No breaking changes to existing API endpoints

### Discovery Prompt Enhancement

The LLM discovery prompt now includes:
1. Visibility guidelines with specific examples
2. Status field examples for common entity types
3. Instructions to include status fields for entities that change state

## API Changes

### Entity Type Registration

```json
{
  "name": "Customer",
  "description": "A customer in our system",
  "visible_by_default": true,
  "fields": [
    {
      "name": "full_name",
      "type": "str",
      "description": "Customer's full name",
      "required": true
    },
    {
      "name": "status",
      "type": "str", 
      "description": "Customer status (cold_lead, warm_lead, hot_lead, active, churned)",
      "required": false
    }
  ]
}
```

### Entity Listing with Filters

```json
{
  "entities": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "has_next": true,
    "has_previous": false,
    "count": 20
  },
  "total_count": 150
}
```

## Benefits

1. **Better User Experience:** Users see relevant entities by default, with technical entities hidden
2. **Status Tracking:** Common status fields are suggested automatically for entities that change state
3. **Flexible Filtering:** Users can filter entities by visibility and type
4. **Backward Compatible:** Existing systems continue to work without changes
5. **Smart Defaults:** The system suggests appropriate visibility settings automatically

## Testing

A comprehensive test suite (`test_entity_discovery_improvements.py`) verifies:
- Visibility logic works correctly for different entity types
- Status field examples are appropriate
- Entity type creation includes visibility settings
- Discovery responses include visibility information

## Future Enhancements

1. **UI Integration:** Frontend components to leverage visibility settings
2. **Advanced Filtering:** More sophisticated filtering options
3. **User Preferences:** Allow users to customize visibility settings
4. **Analytics:** Track which entity types are most commonly used
5. **Smart Suggestions:** Learn from user behavior to improve visibility suggestions
