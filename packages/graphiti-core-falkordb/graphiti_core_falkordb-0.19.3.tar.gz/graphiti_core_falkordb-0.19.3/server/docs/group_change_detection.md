# Group Change Detection API

Simple endpoint to check if a group has changed since a given timestamp - perfect for cache invalidation.

## Endpoint

**GET** `/groups/{group_id}/changed?since={timestamp_or_cache_key}`

### Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `group_id` | string | The group ID to check | `conversation_123` |
| `since` | string | ISO timestamp or cache key to check against | `2024-01-15T10:30:00Z` or `group_123:1642781234` |

### Response

```json
{
  "changed": true,
  "cache_key": "conversation_123:1642781234"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `changed` | boolean | Whether the group has changed since the given timestamp |
| `cache_key` | string | New cache key if changed, or same cache key if unchanged |

## How It Works

1. **Parse Input**: Accepts either ISO timestamp or cache key format
2. **Quick Query**: Checks if any Episode or Entity in the group was created/updated after the timestamp
3. **Return Result**: Just a boolean and cache key - super lightweight

## Usage Examples

### 1. First Time (No Cache)

```bash
# Check if group has changed since epoch (will always be true for existing groups)
curl "http://localhost:8000/groups/conversation_123/changed?since=1970-01-01T00:00:00Z"
```

**Response:**
```json
{
  "changed": true,
  "cache_key": "conversation_123:1642781234"
}
```

### 2. Subsequent Checks (With Cache Key)

```bash
# Check using the cache key from previous response
curl "http://localhost:8000/groups/conversation_123/changed?since=conversation_123:1642781234"
```

**Response if unchanged:**
```json
{
  "changed": false,
  "cache_key": "conversation_123:1642781234"
}
```

**Response if changed:**
```json
{
  "changed": true,
  "cache_key": "conversation_123:1642781890"
}
```

### 3. Using ISO Timestamps

```bash
# Check using ISO timestamp
curl "http://localhost:8000/groups/conversation_123/changed?since=2024-01-15T10:30:00Z"
```

## Integration Pattern

### Basic Caching Logic

```javascript
// Your cache object
let cache = {
  "conversation_123": {
    data: [...], // Your cached data
    cacheKey: "conversation_123:1642781234"
  }
};

async function getGroupData(groupId) {
  const cached = cache[groupId];
  
  if (cached) {
    // Check if changed
    const response = await fetch(
      `http://localhost:8000/groups/${groupId}/changed?since=${cached.cacheKey}`
    );
    const { changed, cache_key } = await response.json();
    
    if (!changed) {
      console.log("Using cached data");
      return cached.data;
    }
    
    console.log("Data changed, fetching fresh");
    // Update cache key for next time
    cached.cacheKey = cache_key;
  }
  
  // Fetch fresh data
  const freshData = await fetchFreshGroupData(groupId);
  
  // Update cache
  cache[groupId] = {
    data: freshData,
    cacheKey: cache_key || `${groupId}:${Date.now()}`
  };
  
  return freshData;
}
```

### React Hook Example

```typescript
function useGroupData(groupId: string) {
  const [data, setData] = useState(null);
  const [cacheKey, setCacheKey] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const checkAndFetch = async () => {
    if (cacheKey) {
      // Check if changed
      const response = await fetch(
        `/api/groups/${groupId}/changed?since=${cacheKey}`
      );
      const { changed, cache_key } = await response.json();
      
      if (!changed) {
        setLoading(false);
        return; // Use existing data
      }
      
      setCacheKey(cache_key);
    }
    
    // Fetch fresh data
    setLoading(true);
    const freshData = await fetchGroupData(groupId);
    setData(freshData);
    setLoading(false);
  };
  
  useEffect(() => {
    checkAndFetch();
    
    // Poll every 30 seconds
    const interval = setInterval(checkAndFetch, 30000);
    return () => clearInterval(interval);
  }, [groupId]);
  
  return { data, loading, refresh: checkAndFetch };
}
```

### Polling Strategy

```javascript
class GroupCache {
  constructor() {
    this.cache = new Map();
    this.pollInterval = 30000; // 30 seconds
  }
  
  async startPolling(groupId) {
    const poll = async () => {
      try {
        const cached = this.cache.get(groupId);
        const since = cached?.cacheKey || '1970-01-01T00:00:00Z';
        
        const response = await fetch(
          `http://localhost:8000/groups/${groupId}/changed?since=${since}`
        );
        const { changed, cache_key } = await response.json();
        
        if (changed) {
          console.log(`Group ${groupId} changed, refreshing cache`);
          await this.refreshGroup(groupId, cache_key);
        }
      } catch (error) {
        console.error(`Error polling group ${groupId}:`, error);
      }
    };
    
    // Initial check
    await poll();
    
    // Set up polling
    return setInterval(poll, this.pollInterval);
  }
  
  async refreshGroup(groupId, cacheKey) {
    const freshData = await fetchGroupData(groupId);
    this.cache.set(groupId, {
      data: freshData,
      cacheKey,
      lastFetched: Date.now()
    });
    
    // Emit event for UI updates
    this.emit('groupUpdated', { groupId, data: freshData });
  }
}
```

## Performance Notes

- **Super Fast**: Just checks timestamps, doesn't return actual data
- **Lightweight Query**: Uses indexed fields (group_id, created_at)
- **Minimal Response**: Just boolean + cache key
- **Error Safe**: Returns `changed: true` on any error to be safe

## Cache Key Format

The cache key format is: `{group_id}:{unix_timestamp}`

Examples:
- `conversation_123:1642781234`
- `document_analysis_456:1642781890`

This makes it easy to:
1. **Parse**: Split on `:` to get timestamp
2. **Compare**: Numeric comparison of timestamps
3. **Debug**: Human-readable group ID + timestamp

## Error Handling

The endpoint is designed to be safe:
- **Invalid timestamp**: Returns `changed: true`
- **Database error**: Returns `changed: true`
- **No data found**: Returns `changed: false`

This ensures your cache never gets stuck with stale data.

## Use Cases

1. **Convex Caching**: Check before expensive data fetches
2. **Real-time Updates**: Poll for changes without full data transfer
3. **Mobile Apps**: Minimize data usage with change detection
4. **Background Sync**: Only sync when actually needed

Perfect for any scenario where you want to avoid unnecessary data fetching! 🎯
