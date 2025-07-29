# Entity CRUD API Documentation

The Entity CRUD API provides comprehensive endpoints for creating, reading, updating, and deleting individual entities with full entity type validation and support.

## Base URL
```
/entities
```

## Endpoints

### 1. Create Entity
**POST** `/entities/`

Create a new entity with entity type validation.

#### Request Body
```json
{
  "group_id": "string",
  "name": "string", 
  "entity_type": "string",
  "summary": "string (optional)",
  "attributes": {
    "field_name": "value",
    "another_field": "another_value"
  }
}
```

#### Example: Create Customer
```bash
curl -X POST "http://localhost:8000/entities/" \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": "my-group",
    "name": "John Doe",
    "entity_type": "Customer",
    "summary": "A potential customer from the tech industry",
    "attributes": {
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "+1-555-0123",
      "company": "Tech Corp",
      "status": "warm_lead",
      "source": "website",
      "profile_image_url": "https://example.com/john.jpg",
      "linkedin_url": "https://linkedin.com/in/johndoe"
    }
  }'
```

#### Response (201 Created)
```json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "group_id": "my-group",
  "name": "John Doe",
  "summary": "A potential customer from the tech industry",
  "attributes": {
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "company": "Tech Corp",
    "status": "warm_lead",
    "source": "website",
    "profile_image_url": "https://example.com/john.jpg",
    "linkedin_url": "https://linkedin.com/in/johndoe"
  },
  "labels": ["Entity", "Customer"],
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2. Get Entity
**GET** `/entities/{entity_uuid}`

Retrieve an entity by its UUID.

#### Example
```bash
curl "http://localhost:8000/entities/123e4567-e89b-12d3-a456-426614174000"
```

#### Response (200 OK)
```json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "group_id": "my-group",
  "name": "John Doe",
  "summary": "A potential customer from the tech industry",
  "attributes": {
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "status": "warm_lead"
  },
  "labels": ["Entity", "Customer"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z"
}
```

### 3. Update Entity
**PUT** `/entities/{entity_uuid}`

Update an existing entity's name, summary, or attributes.

#### Request Body
```json
{
  "name": "string (optional)",
  "summary": "string (optional)",
  "attributes": {
    "field_to_update": "new_value",
    "another_field": "another_new_value"
  }
}
```

#### Example: Update Customer Status
```bash
curl -X PUT "http://localhost:8000/entities/123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "High-value customer from the tech industry",
    "attributes": {
      "status": "hot_lead",
      "value": "75000",
      "notes": "Very interested in our enterprise solution"
    }
  }'
```

#### Response (200 OK)
```json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "group_id": "my-group",
  "name": "John Doe",
  "summary": "High-value customer from the tech industry",
  "attributes": {
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "status": "hot_lead",
    "value": "75000",
    "notes": "Very interested in our enterprise solution"
  },
  "labels": ["Entity", "Customer"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

### 4. Delete Entity
**DELETE** `/entities/{entity_uuid}`

Delete an entity by its UUID.

#### Query Parameters
- `cascade` (boolean, optional): Whether to delete related relationships. Default: false

#### Example
```bash
curl -X DELETE "http://localhost:8000/entities/123e4567-e89b-12d3-a456-426614174000?cascade=true"
```

#### Response (200 OK)
```json
{
  "message": "Entity 123e4567-e89b-12d3-a456-426614174000 deleted successfully",
  "success": true
}
```

### 5. Validate Entity
**GET** `/entities/{entity_uuid}/validate`

Validate an entity against its entity type schema.

#### Example
```bash
curl "http://localhost:8000/entities/123e4567-e89b-12d3-a456-426614174000/validate"
```

#### Response (200 OK)
```json
{
  "valid": true,
  "message": "Entity is valid according to its type schema",
  "entity_type": "Customer",
  "violations": [],
  "validated_attributes": {
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "status": "hot_lead"
  }
}
```

## Entity Types

The API works with the following pre-seeded entity types:

### Customer
- `full_name` (required)
- `email`, `phone`, `company`
- `status`: cold_lead, warm_lead, hot_lead, active, churned
- `source`, `value`, `territory`
- `profile_image_url`, `linkedin_url`, `website_url`

### Project
- `name` (required)
- `description`, `status`: planning, active, on_hold, completed, cancelled
- `priority`, `deadline`, `start_date`, `budget`, `owner`
- `client`, `progress`, `risks`
- `project_url`, `repository_url`, `documentation_url`

### Task
- `title` (required)
- `description`, `status`: todo, in_progress, review, done, blocked
- `priority`, `assignee`, `reporter`, `due_date`
- `estimated_hours`, `actual_hours`, `project`, `tags`

### Company
- `company_name` (required)
- `industry`, `location`, `size`
- `website_url`, `linkedin_url`, `logo_url`
- `status`: prospect, partner, client, competitor

### Contact
- `full_name` (required)
- `title`, `email`, `phone`, `company`, `department`
- `relationship`, `last_contact`, `preferred_contact`
- `profile_image_url`, `linkedin_url`, `portfolio_url`

### Meeting
- `title` (required)
- `description`, `date_time`, `duration`, `location`
- `attendees`, `organizer`, `status`, `meeting_type`
- `outcome`, `action_items`, `recording_link`

### Interview
- `candidate_name` (required)
- `position`, `interviewer`, `interview_type`
- `status`, `rating`, `feedback`, `recommendation`

### Document
- `title` (required)
- `document_type`, `author`, `version`, `status`
- `file_url`, `preview_url`, `edit_url`
- `access_level`, `related_project`

### Deal
- `deal_name` (required)
- `customer`, `value`, `stage`, `probability`
- `sales_rep`, `source`, `competitors`

### Issue
- `title` (required)
- `description`, `status`, `priority`, `severity`
- `reporter`, `assignee`, `category`

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Entity type 'InvalidType' not found"
}
```

### 404 Not Found
```json
{
  "detail": "Entity not found"
}
```

### 422 Validation Error
```json
{
  "detail": "Attribute validation failed: field 'email' is required"
}
```

## Integration with Existing Endpoints

The Entity CRUD API works alongside existing endpoints:

- **List entities**: `GET /entities/{group_id}` (existing)
- **Paginated entities**: `GET /entities/{group_id}/paginated` (existing)
- **Entity context**: `GET /entities/{uuid}/context` (existing)
- **Entity types**: `GET /entity-types/` (existing)

This provides a complete entity management system with type safety, validation, and comprehensive CRUD operations.
