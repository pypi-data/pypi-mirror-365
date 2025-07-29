# Updated At Tracking in Graphiti

## Why This Was Missing

Graphiti was originally designed as a knowledge graph where entities were extracted from content and treated as relatively immutable. However, this created a significant gap:

### The Problem
1. **Entities DO get updated during ingestion** - summaries, attributes, and embeddings change
2. **No change tracking** - impossible to know when entities were modified
3. **Cache invalidation issues** - can't efficiently invalidate caches
4. **API inconsistency** - CRUD operations lacked standard timestamp behavior

### Real-World Impact
- **Convex Integration**: Needs to know when groups/entities changed for efficient caching
- **Performance**: Can't optimize queries based on modification time
- **Debugging**: No audit trail of when entities evolved
- **User Experience**: No way to show "last updated" information

## How Entities Get Updated

### During Ingestion Pipeline
1. **Attribute Extraction** (`extract_attributes_from_nodes`):
   - Updates `summary` with new information from episodes
   - Updates `attributes` with extracted properties
   - Happens for every entity during episode processing

2. **Deduplication Process** (`dedupe_nodes_bulk`):
   - Merges duplicate entities
   - Combines and updates summaries
   - Merges attributes from multiple sources

3. **Community Updates** (`update_community`):
   - Updates entity summaries when communities change
   - Regenerates names and descriptions

4. **Embedding Updates**:
   - Updates `name_embedding` when entities are processed

### During CRUD Operations
- Manual updates to name, summary, or attributes
- Direct modifications through API endpoints

## Implementation

### 1. Added `updated_at` Field to EntityNode

```python
class EntityNode(Node):
    # ... existing fields ...
    updated_at: datetime | None = Field(default=None, description='datetime of when the node was last updated')
```

### 2. Updated Save Method

The `save()` method now includes `updated_at` in the data saved to Neo4j:

```python
entity_data: dict[str, Any] = {
    'uuid': self.uuid,
    'name': self.name,
    # ... other fields ...
    'updated_at': self.updated_at,
}
```

### 3. Updated Ingestion Pipeline

In `extract_attributes_from_node()`, we now track changes and set `updated_at`:

```python
# Check if anything actually changed
old_summary = node.summary
old_attributes = node.attributes.copy()

# ... update logic ...

# Update timestamp if anything changed
if (node.summary != old_summary or 
    node.attributes != old_attributes):
    node.updated_at = utc_now()
```

### 4. Updated CRUD Operations

CRUD endpoints now set `updated_at` when entities are modified:

```python
# Set updated timestamp if anything changed
if changes:
    entity.updated_at = utc_now()
```

### 5. Updated Database Queries

The `get_entity_node_from_record()` function handles the `updated_at` field with backward compatibility:

```python
# Handle updated_at field which might not exist in older records
updated_at = None
if 'updated_at' in record and record['updated_at'] is not None:
    updated_at = parse_db_date(record['updated_at'])
```

## Behavior

### New Entities
- `created_at`: Set to current timestamp
- `updated_at`: `None` (not yet modified)

### Updated Entities
- `created_at`: Original creation time (unchanged)
- `updated_at`: Timestamp of last modification

### API Responses
```json
{
  "uuid": "entity-uuid",
  "name": "John Smith",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-20T14:30:00Z"  // or null if never updated
}
```

## Use Cases

### 1. Cache Invalidation
```python
# Check if entity changed since last cache
if entity.updated_at and entity.updated_at > last_cache_time:
    invalidate_cache(entity.uuid)
```

### 2. Change Detection
```python
# Find entities modified in last hour
recent_changes = await search_entities(
    updated_since=datetime.now() - timedelta(hours=1)
)
```

### 3. Audit Trails
```python
# Show entity evolution
print(f"Created: {entity.created_at}")
print(f"Last modified: {entity.updated_at or 'Never'}")
```

### 4. Convex Integration
```python
# Efficient polling - only fetch changed entities
def get_entities_since(last_sync: datetime):
    return entities.filter(
        lambda e: e.updated_at and e.updated_at > last_sync
    )
```

## Backward Compatibility

- Existing entities without `updated_at` will have `updated_at=None`
- Database queries handle missing `updated_at` fields gracefully
- API responses include `updated_at` field (null for legacy entities)
- No migration required - field is optional

## Benefits

1. **Efficient Caching**: Know exactly when to invalidate cached data
2. **Change Tracking**: Identify which entities have been modified
3. **Performance**: Optimize queries and data synchronization
4. **User Experience**: Show "last updated" information
5. **Debugging**: Track entity evolution over time
6. **API Consistency**: Standard timestamp behavior across all endpoints

## Integration Points

### Convex Caching
- Use `updated_at` to determine when to refresh cached entities
- Implement efficient polling by fetching only changed entities
- Optimize data synchronization between Graphiti and Convex

### Search and Filtering
- Filter entities by modification time
- Sort results by recency
- Implement "recently updated" views

### Monitoring and Analytics
- Track entity update frequency
- Identify most/least active entities
- Monitor system activity patterns

This implementation ensures that Graphiti now provides complete timestamp tracking for entities, enabling efficient caching, change detection, and better integration with external systems like Convex.
