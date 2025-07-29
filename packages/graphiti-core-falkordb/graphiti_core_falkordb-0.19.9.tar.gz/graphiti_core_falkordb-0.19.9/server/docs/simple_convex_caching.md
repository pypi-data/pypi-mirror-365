# Simple Convex Caching for Graphiti

A lightweight caching approach that's easy to implement and maintain.

## Quick Setup

### 1. Minimal Convex Schema

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  graphitiCache: defineTable({
    groupId: v.string(),
    cacheKey: v.string(), // group_id:timestamp
    lastModified: v.string(),
    data: v.any(), // Store whatever you need
    type: v.string(), // "entities", "context", etc.
    lastFetched: v.number(),
  }).index("by_group_and_type", ["groupId", "type"])
    .index("by_cache_key", ["cacheKey"]),
});
```

### 2. Core Caching Functions

```typescript
// convex/graphiti.ts
import { v } from "convex/values";
import { mutation, query, action } from "./_generated/server";

const GRAPHITI_BASE_URL = process.env.GRAPHITI_BASE_URL || "http://localhost:8000";

// Check if group data is stale
export const isGroupStale = action({
  args: { groupId: v.string(), type: v.string() },
  handler: async (ctx, { groupId, type }) => {
    // Get current cache
    const cached = await ctx.runQuery(api.graphiti.getCached, { groupId, type });
    
    // Check last modified from API
    const response = await fetch(`${GRAPHITI_BASE_URL}/groups/${groupId}/last-modified`);
    const { cache_key } = await response.json();
    
    return {
      isStale: !cached || cached.cacheKey !== cache_key,
      currentCacheKey: cached?.cacheKey,
      newCacheKey: cache_key
    };
  },
});

// Get cached data
export const getCached = query({
  args: { groupId: v.string(), type: v.string() },
  handler: async (ctx, { groupId, type }) => {
    return await ctx.db
      .query("graphitiCache")
      .withIndex("by_group_and_type", (q) => 
        q.eq("groupId", groupId).eq("type", type)
      )
      .first();
  },
});

// Smart fetch with caching
export const fetchEntities = action({
  args: { 
    groupId: v.string(),
    forceRefresh: v.optional(v.boolean())
  },
  handler: async (ctx, { groupId, forceRefresh = false }) => {
    const type = "entities";
    
    // Check if stale
    const staleCheck = await ctx.runAction(api.graphiti.isGroupStale, { groupId, type });
    
    if (!staleCheck.isStale && !forceRefresh) {
      // Return cached data
      const cached = await ctx.runQuery(api.graphiti.getCached, { groupId, type });
      return { data: cached?.data, fromCache: true };
    }
    
    // Fetch fresh data
    const response = await fetch(
      `${GRAPHITI_BASE_URL}/entities?group_ids=${groupId}&limit=1000`
    );
    const data = await response.json();
    
    // Update cache
    await ctx.runMutation(api.graphiti.updateCache, {
      groupId,
      type,
      cacheKey: staleCheck.newCacheKey,
      data: data.entities || []
    });
    
    return { data: data.entities || [], fromCache: false };
  },
});

// Update cache
export const updateCache = mutation({
  args: {
    groupId: v.string(),
    type: v.string(),
    cacheKey: v.string(),
    data: v.any()
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("graphitiCache")
      .withIndex("by_group_and_type", (q) => 
        q.eq("groupId", args.groupId).eq("type", args.type)
      )
      .first();
    
    const record = {
      ...args,
      lastFetched: Date.now()
    };
    
    if (existing) {
      await ctx.db.patch(existing._id, record);
    } else {
      await ctx.db.insert("graphitiCache", record);
    }
  },
});

// Fetch entity context with caching
export const fetchEntityContext = action({
  args: { 
    entityUuid: v.string(),
    groupId: v.optional(v.string())
  },
  handler: async (ctx, { entityUuid, groupId }) => {
    const type = `context:${entityUuid}`;
    
    // Check if group data is stale (if groupId provided)
    let isStale = true;
    if (groupId) {
      const staleCheck = await ctx.runAction(api.graphiti.isGroupStale, { 
        groupId, 
        type: "entities" 
      });
      isStale = staleCheck.isStale;
    }
    
    // Check cache age (5 minutes for entity context)
    const cached = await ctx.runQuery(api.graphiti.getCached, { 
      groupId: groupId || "global", 
      type 
    });
    
    const cacheAge = cached ? Date.now() - cached.lastFetched : Infinity;
    const cacheExpired = cacheAge > 300000; // 5 minutes
    
    if (!isStale && !cacheExpired && cached) {
      return { data: cached.data, fromCache: true };
    }
    
    // Fetch fresh context
    const response = await fetch(
      `${GRAPHITI_BASE_URL}/entities/${entityUuid}/context`
    );
    const data = await response.json();
    
    // Update cache
    await ctx.runMutation(api.graphiti.updateCache, {
      groupId: groupId || "global",
      type,
      cacheKey: `${entityUuid}:${Date.now()}`,
      data
    });
    
    return { data, fromCache: false };
  },
});
```

### 3. React Hook for Easy Usage

```typescript
// hooks/useGraphitiData.ts
import { useAction } from "convex/react";
import { api } from "../convex/_generated/api";
import { useEffect, useState } from "react";

export function useGraphitiEntities(groupId: string) {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fromCache, setFromCache] = useState(false);
  
  const fetchEntities = useAction(api.graphiti.fetchEntities);
  
  const loadData = async (forceRefresh = false) => {
    setLoading(true);
    try {
      const result = await fetchEntities({ groupId, forceRefresh });
      setEntities(result.data);
      setFromCache(result.fromCache);
    } catch (error) {
      console.error("Error loading entities:", error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    loadData();
  }, [groupId]);
  
  return {
    entities,
    loading,
    fromCache,
    refresh: () => loadData(true),
    reload: () => loadData(false)
  };
}

export function useEntityContext(entityUuid: string, groupId?: string) {
  const [context, setContext] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fromCache, setFromCache] = useState(false);
  
  const fetchContext = useAction(api.graphiti.fetchEntityContext);
  
  useEffect(() => {
    const loadContext = async () => {
      setLoading(true);
      try {
        const result = await fetchContext({ entityUuid, groupId });
        setContext(result.data);
        setFromCache(result.fromCache);
      } catch (error) {
        console.error("Error loading context:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadContext();
  }, [entityUuid, groupId]);
  
  return { context, loading, fromCache };
}
```

### 4. Simple React Component

```typescript
// components/EntityList.tsx
import { useGraphitiEntities } from "../hooks/useGraphitiData";

export function EntityList({ groupId }: { groupId: string }) {
  const { entities, loading, fromCache, refresh } = useGraphitiEntities(groupId);
  
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2>Entities ({entities.length})</h2>
        <div className="flex gap-2">
          <span className={`px-2 py-1 rounded text-sm ${
            fromCache ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
          }`}>
            {fromCache ? 'Cached' : 'Fresh'}
          </span>
          <button 
            onClick={refresh}
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
          >
            Refresh
          </button>
        </div>
      </div>
      
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="grid gap-4">
          {entities.map((entity) => (
            <div key={entity.uuid} className="p-4 border rounded">
              <h3 className="font-bold">{entity.name}</h3>
              <p className="text-gray-600">{entity.summary}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### 5. Periodic Cache Refresh (Optional)

```typescript
// convex/crons.ts
import { cronJobs } from "convex/server";
import { api } from "./_generated/api";

const crons = cronJobs();

// Check for stale data every 5 minutes
crons.interval(
  "refresh-stale-caches",
  { minutes: 5 },
  api.graphiti.refreshStaleCaches
);

export default crons;

// Add to graphiti.ts
export const refreshStaleCaches = action({
  args: {},
  handler: async (ctx) => {
    // Get all cached groups
    const allCaches = await ctx.runQuery(api.graphiti.getAllCaches);
    
    for (const cache of allCaches) {
      if (cache.type === "entities") {
        const staleCheck = await ctx.runAction(api.graphiti.isGroupStale, {
          groupId: cache.groupId,
          type: cache.type
        });
        
        if (staleCheck.isStale) {
          console.log(`Refreshing stale cache for group ${cache.groupId}`);
          await ctx.runAction(api.graphiti.fetchEntities, {
            groupId: cache.groupId,
            forceRefresh: true
          });
        }
      }
    }
  },
});

export const getAllCaches = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("graphitiCache").collect();
  },
});
```

## Key Benefits

1. **Simple**: Just 3 main functions (check stale, fetch, cache)
2. **Efficient**: Only fetches when data actually changes
3. **Flexible**: Works with any Graphiti endpoint
4. **Automatic**: Optional background refresh
5. **Transparent**: Shows cache status to users

## Usage Pattern

```typescript
// 1. Check if data is stale
const staleCheck = await isGroupStale({ groupId, type: "entities" });

// 2. If stale, fetch fresh data
if (staleCheck.isStale) {
  const freshData = await fetchFromGraphiti();
  await updateCache({ groupId, type, data: freshData });
}

// 3. Return cached data
return getCached({ groupId, type });
```

This approach gives you smart caching with minimal complexity! 🎯
