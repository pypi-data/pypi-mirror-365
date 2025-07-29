# Entity Pagination and Sorting API

This document provides comprehensive documentation for the entity pagination and sorting capabilities in the Graphiti knowledge graph server.

## Overview

The Entity Pagination API allows you to efficiently retrieve and browse entities with support for:

- **Pagination**: Both page-based and cursor-based pagination
- **Sorting**: Sort by standard fields or custom entity attributes
- **Filtering**: Filter entities by group ID
- **Metadata**: Rich pagination metadata for building UIs

## Endpoints

### Get Paginated Entities

**GET** `/entities/{group_id}/paginated`

Retrieve entities for a specific group with pagination and sorting support.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `group_id` | string | The group ID to retrieve entities from |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-based, min: 1) |
| `page_size` | integer | 20 | Number of items per page (min: 1, max: 100) |
| `sort_by` | string | "created_at" | Field to sort by: "name", "created_at", "summary", "uuid" |
| `sort_order` | string | "desc" | Sort order: "asc" or "desc" |
| `attribute_sort_field` | string | null | Custom attribute field to sort by (overrides sort_by) |
| `cursor` | string | null | Entity UUID for cursor-based pagination |

#### Response

```json
{
  "entities": [
    {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "summary": "Software engineer at Tech Corp",
      "attributes": {
        "age": 30,
        "department": "Engineering",
        "salary": 75000
      },
      "labels": ["Entity", "Person"],
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "has_next": true,
    "has_previous": false,
    "count": 20,
    "next_cursor": "550e8400-e29b-41d4-a716-446655440001",
    "previous_cursor": null
  },
  "total_count": 150
}
```

#### Examples

**Basic pagination:**
```bash
curl "http://localhost:8000/entities/my_group/paginated"
```

**Custom page size:**
```bash
curl "http://localhost:8000/entities/my_group/paginated?page=2&page_size=50"
```

**Sort by name ascending:**
```bash
curl "http://localhost:8000/entities/my_group/paginated?sort_by=name&sort_order=asc"
```

**Sort by custom attribute:**
```bash
curl "http://localhost:8000/entities/my_group/paginated?attribute_sort_field=age&sort_order=desc"
```

**Cursor-based pagination:**
```bash
curl "http://localhost:8000/entities/my_group/paginated?cursor=550e8400-e29b-41d4-a716-446655440000"
```

### Get Available Sort Fields

**GET** `/entities/{group_id}/sort-fields`

Get the available fields for sorting entities in the specified group.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `group_id` | string | The group ID to analyze |

#### Response

```json
{
  "group_id": "my_group",
  "sort_fields": {
    "standard_fields": ["name", "created_at", "summary", "uuid"],
    "attribute_fields": ["age", "department", "salary", "location"]
  },
  "description": {
    "standard_fields": "Built-in entity fields that are always available for sorting",
    "attribute_fields": "Custom attribute fields from entity types that are available for sorting"
  }
}
```

#### Example

```bash
curl "http://localhost:8000/entities/my_group/sort-fields"
```

## Pagination Strategies

### Page-based Pagination

Use `page` and `page_size` parameters for traditional pagination:

```bash
# Page 1
curl "http://localhost:8000/entities/my_group/paginated?page=1&page_size=20"

# Page 2
curl "http://localhost:8000/entities/my_group/paginated?page=2&page_size=20"
```

**Pros:**
- Simple to implement in UIs
- Easy to jump to specific pages
- Provides total count

**Cons:**
- Can have inconsistencies if data changes between requests
- Performance degrades with large offsets

### Cursor-based Pagination

Use the `cursor` parameter with entity UUIDs for consistent pagination:

```bash
# First page
curl "http://localhost:8000/entities/my_group/paginated?page_size=20"

# Next page using cursor from previous response
curl "http://localhost:8000/entities/my_group/paginated?cursor=last_entity_uuid&page_size=20"
```

**Pros:**
- Consistent results even if data changes
- Better performance for large datasets
- No duplicate or missing items

**Cons:**
- Cannot jump to arbitrary pages
- More complex to implement

## Sorting Options

### Standard Fields

All entities support sorting by these built-in fields:

- `name`: Entity name (string)
- `created_at`: Creation timestamp (datetime)
- `summary`: Entity summary (string)
- `uuid`: Unique identifier (string)

### Custom Attributes

Sort by any custom attribute defined in your entity types:

```bash
# Sort by age (numeric attribute)
curl "http://localhost:8000/entities/my_group/paginated?attribute_sort_field=age&sort_order=desc"

# Sort by department (string attribute)
curl "http://localhost:8000/entities/my_group/paginated?attribute_sort_field=department&sort_order=asc"
```

**Note:** Custom attributes are sorted as their native types (string, number, etc.).

## Error Handling

### Validation Errors (422)

Invalid parameters will return a 422 status with details:

```json
{
  "detail": [
    {
      "loc": ["query", "page"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge",
      "ctx": {"limit_value": 1}
    }
  ]
}
```

### Common Validation Rules

- `page`: Must be ≥ 1
- `page_size`: Must be between 1 and 100
- `sort_order`: Must be "asc" or "desc"
- `sort_by`: Must be a valid standard field name

## Performance Considerations

1. **Page Size**: Larger page sizes reduce the number of requests but increase response time and memory usage
2. **Sorting**: Sorting by indexed fields (like `created_at`) is faster than custom attributes
3. **Total Count**: The total count query can be expensive for large datasets
4. **Cursor Pagination**: Generally more efficient for large datasets than page-based pagination

## Best Practices

1. **Use appropriate page sizes**: 20-50 items per page for most use cases
2. **Implement cursor pagination**: For real-time data or large datasets
3. **Cache sort field metadata**: Call `/sort-fields` once and cache the results
4. **Handle empty results**: Always check the `count` field in pagination metadata
5. **Use consistent sorting**: Always specify `sort_by` and `sort_order` for predictable results

## Integration Examples

### JavaScript/Frontend

```javascript
async function getEntities(groupId, page = 1, sortBy = 'created_at') {
  const response = await fetch(
    `/entities/${groupId}/paginated?page=${page}&sort_by=${sortBy}&sort_order=desc`
  );
  return await response.json();
}

// Get available sort fields
async function getSortFields(groupId) {
  const response = await fetch(`/entities/${groupId}/sort-fields`);
  return await response.json();
}
```

### Python

```python
import requests

def get_entities(group_id, page=1, page_size=20, sort_by='created_at', sort_order='desc'):
    url = f"http://localhost:8000/entities/{group_id}/paginated"
    params = {
        'page': page,
        'page_size': page_size,
        'sort_by': sort_by,
        'sort_order': sort_order
    }
    response = requests.get(url, params=params)
    return response.json()
```
