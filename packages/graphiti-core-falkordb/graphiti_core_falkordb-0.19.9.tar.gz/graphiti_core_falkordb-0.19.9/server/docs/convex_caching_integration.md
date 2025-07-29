# Convex Integration with Smart Caching

This document explains how to integrate Graphiti with Convex using intelligent caching that only fetches data when groups have changed.

## Overview

The caching strategy uses:
1. **Change Detection**: Track last modification time per group
2. **Cache Keys**: Unique identifiers based on group + timestamp
3. **Incremental Updates**: Only fetch data when changes are detected
4. **Efficient Polling**: Lightweight checks for changes

## Architecture

```
Convex Functions → Cache Check → Graphiti API → Update Cache
     ↓               ↓              ↓              ↓
  User Query → Check Cache Key → Fetch if Changed → Return Data
```

## Convex Schema

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Cache for group data
  groupCache: defineTable({
    groupId: v.string(),
    cacheKey: v.string(),
    lastModified: v.string(),
    entities: v.array(v.any()),
    relationships: v.array(v.any()),
    lastFetched: v.number(),
    dataHash: v.optional(v.string()),
  }).index("by_group_id", ["groupId"]),

  // Cache for entity context
  entityContextCache: defineTable({
    entityUuid: v.string(),
    groupId: v.string(),
    cacheKey: v.string(),
    context: v.string(),
    navigationLinks: v.any(),
    lastFetched: v.number(),
  }).index("by_entity", ["entityUuid"])
    .index("by_group", ["groupId"]),

  // Track polling status
  groupPollStatus: defineTable({
    groupId: v.string(),
    lastChecked: v.number(),
    isPolling: v.boolean(),
    pollInterval: v.number(), // milliseconds
  }).index("by_group_id", ["groupId"]),
});
```

## Convex Functions

### 1. Change Detection Function

```typescript
// convex/graphiti.ts
import { v } from "convex/values";
import { mutation, query, action } from "./_generated/server";
import { api } from "./_generated/api";

// Check if group has changed
export const checkGroupChanges = action({
  args: { 
    groupId: v.string(),
    graphitiBaseUrl: v.optional(v.string())
  },
  handler: async (ctx, { groupId, graphitiBaseUrl = "http://localhost:8000" }) => {
    try {
      // Get current cache info
      const cached = await ctx.runQuery(api.graphiti.getCachedGroupInfo, { groupId });
      
      // Check last modified from Graphiti API
      const response = await fetch(`${graphitiBaseUrl}/groups/${groupId}/last-modified`);
      const lastModifiedData = await response.json();
      
      const hasChanged = !cached || cached.cacheKey !== lastModifiedData.cache_key;
      
      return {
        hasChanged,
        currentCacheKey: cached?.cacheKey,
        newCacheKey: lastModifiedData.cache_key,
        lastModified: lastModifiedData.last_modified,
        groupId
      };
    } catch (error) {
      console.error("Error checking group changes:", error);
      return {
        hasChanged: true, // Assume changed on error
        error: error.message
      };
    }
  },
});

// Get cached group info
export const getCachedGroupInfo = query({
  args: { groupId: v.string() },
  handler: async (ctx, { groupId }) => {
    const cached = await ctx.db
      .query("groupCache")
      .withIndex("by_group_id", (q) => q.eq("groupId", groupId))
      .first();
    
    return cached;
  },
});
```

### 2. Smart Data Fetching

```typescript
// Fetch group data only if changed
export const fetchGroupDataIfChanged = action({
  args: { 
    groupId: v.string(),
    forceRefresh: v.optional(v.boolean()),
    graphitiBaseUrl: v.optional(v.string())
  },
  handler: async (ctx, { groupId, forceRefresh = false, graphitiBaseUrl = "http://localhost:8000" }) => {
    // Check for changes first
    const changeCheck = await ctx.runAction(api.graphiti.checkGroupChanges, { 
      groupId, 
      graphitiBaseUrl 
    });
    
    if (!changeCheck.hasChanged && !forceRefresh) {
      // Return cached data
      const cached = await ctx.runQuery(api.graphiti.getCachedGroupInfo, { groupId });
      return {
        fromCache: true,
        data: cached,
        cacheKey: cached?.cacheKey
      };
    }
    
    // Fetch fresh data
    console.log(`Fetching fresh data for group ${groupId}`);
    
    try {
      // Fetch entities
      const entitiesResponse = await fetch(
        `${graphitiBaseUrl}/entities?group_ids=${groupId}&limit=1000`
      );
      const entitiesData = await entitiesResponse.json();
      
      // Fetch relationships/facts
      const factsResponse = await fetch(`${graphitiBaseUrl}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: "*",
          group_ids: [groupId],
          max_facts: 1000
        })
      });
      const factsData = await factsResponse.json();
      
      // Update cache
      await ctx.runMutation(api.graphiti.updateGroupCache, {
        groupId,
        cacheKey: changeCheck.newCacheKey,
        lastModified: changeCheck.lastModified,
        entities: entitiesData.entities || [],
        relationships: factsData.facts || []
      });
      
      return {
        fromCache: false,
        data: {
          entities: entitiesData.entities || [],
          relationships: factsData.facts || []
        },
        cacheKey: changeCheck.newCacheKey
      };
      
    } catch (error) {
      console.error("Error fetching group data:", error);
      throw new Error(`Failed to fetch data for group ${groupId}: ${error.message}`);
    }
  },
});

// Update group cache
export const updateGroupCache = mutation({
  args: {
    groupId: v.string(),
    cacheKey: v.string(),
    lastModified: v.string(),
    entities: v.array(v.any()),
    relationships: v.array(v.any())
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("groupCache")
      .withIndex("by_group_id", (q) => q.eq("groupId", args.groupId))
      .first();
    
    const now = Date.now();
    
    if (existing) {
      await ctx.db.patch(existing._id, {
        cacheKey: args.cacheKey,
        lastModified: args.lastModified,
        entities: args.entities,
        relationships: args.relationships,
        lastFetched: now
      });
    } else {
      await ctx.db.insert("groupCache", {
        groupId: args.groupId,
        cacheKey: args.cacheKey,
        lastModified: args.lastModified,
        entities: args.entities,
        relationships: args.relationships,
        lastFetched: now
      });
    }
  },
});
```

### 3. Entity Context Caching

```typescript
// Fetch entity context with caching
export const getEntityContext = action({
  args: { 
    entityUuid: v.string(),
    groupId: v.optional(v.string()),
    maxRelationships: v.optional(v.number()),
    graphitiBaseUrl: v.optional(v.string())
  },
  handler: async (ctx, { 
    entityUuid, 
    groupId, 
    maxRelationships = 50,
    graphitiBaseUrl = "http://localhost:8000" 
  }) => {
    // Check if we have cached context
    const cached = await ctx.runQuery(api.graphiti.getCachedEntityContext, { entityUuid });
    
    // If we have a group ID, check if group has changed
    let groupChanged = false;
    if (groupId) {
      const changeCheck = await ctx.runAction(api.graphiti.checkGroupChanges, { 
        groupId, 
        graphitiBaseUrl 
      });
      groupChanged = changeCheck.hasChanged;
    }
    
    // Use cache if available and group hasn't changed
    if (cached && !groupChanged && (Date.now() - cached.lastFetched) < 300000) { // 5 min cache
      return {
        fromCache: true,
        ...cached
      };
    }
    
    // Fetch fresh context
    const url = new URL(`${graphitiBaseUrl}/entities/${entityUuid}/context`);
    url.searchParams.set('max_relationships', maxRelationships.toString());
    
    const response = await fetch(url.toString());
    const contextData = await response.json();
    
    // Cache the result
    await ctx.runMutation(api.graphiti.updateEntityContextCache, {
      entityUuid,
      groupId: groupId || "unknown",
      context: contextData.context,
      navigationLinks: contextData.navigation_links,
      cacheKey: `${entityUuid}:${Date.now()}`
    });
    
    return {
      fromCache: false,
      ...contextData
    };
  },
});

export const getCachedEntityContext = query({
  args: { entityUuid: v.string() },
  handler: async (ctx, { entityUuid }) => {
    return await ctx.db
      .query("entityContextCache")
      .withIndex("by_entity", (q) => q.eq("entityUuid", entityUuid))
      .first();
  },
});

export const updateEntityContextCache = mutation({
  args: {
    entityUuid: v.string(),
    groupId: v.string(),
    context: v.string(),
    navigationLinks: v.any(),
    cacheKey: v.string()
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("entityContextCache")
      .withIndex("by_entity", (q) => q.eq("entityUuid", args.entityUuid))
      .first();
    
    const now = Date.now();
    
    if (existing) {
      await ctx.db.patch(existing._id, {
        ...args,
        lastFetched: now
      });
    } else {
      await ctx.db.insert("entityContextCache", {
        ...args,
        lastFetched: now
      });
    }
  },
});
```

### 4. Polling Management

```typescript
// Start polling for a group
export const startGroupPolling = mutation({
  args: { 
    groupId: v.string(),
    pollInterval: v.optional(v.number()) // milliseconds
  },
  handler: async (ctx, { groupId, pollInterval = 30000 }) => { // 30 seconds default
    const existing = await ctx.db
      .query("groupPollStatus")
      .withIndex("by_group_id", (q) => q.eq("groupId", groupId))
      .first();
    
    const now = Date.now();
    
    if (existing) {
      await ctx.db.patch(existing._id, {
        isPolling: true,
        pollInterval,
        lastChecked: now
      });
    } else {
      await ctx.db.insert("groupPollStatus", {
        groupId,
        isPolling: true,
        pollInterval,
        lastChecked: now
      });
    }
  },
});

// Stop polling for a group
export const stopGroupPolling = mutation({
  args: { groupId: v.string() },
  handler: async (ctx, { groupId }) => {
    const existing = await ctx.db
      .query("groupPollStatus")
      .withIndex("by_group_id", (q) => q.eq("groupId", groupId))
      .first();
    
    if (existing) {
      await ctx.db.patch(existing._id, {
        isPolling: false
      });
    }
  },
});

// Scheduled function to check for updates
export const pollForUpdates = action({
  args: {},
  handler: async (ctx) => {
    const activePolls = await ctx.runQuery(api.graphiti.getActivePolls);
    
    for (const poll of activePolls) {
      const timeSinceLastCheck = Date.now() - poll.lastChecked;
      
      if (timeSinceLastCheck >= poll.pollInterval) {
        // Check for changes and update if needed
        await ctx.runAction(api.graphiti.fetchGroupDataIfChanged, {
          groupId: poll.groupId
        });
        
        // Update last checked time
        await ctx.runMutation(api.graphiti.updateLastChecked, {
          groupId: poll.groupId
        });
      }
    }
  },
});

export const getActivePolls = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("groupPollStatus")
      .filter((q) => q.eq(q.field("isPolling"), true))
      .collect();
  },
});

export const updateLastChecked = mutation({
  args: { groupId: v.string() },
  handler: async (ctx, { groupId }) => {
    const existing = await ctx.db
      .query("groupPollStatus")
      .withIndex("by_group_id", (q) => q.eq("groupId", groupId))
      .first();
    
    if (existing) {
      await ctx.db.patch(existing._id, {
        lastChecked: Date.now()
      });
    }
  },
});
```

## Usage Examples

### React Component

```typescript
// components/EntityExplorer.tsx
import { useAction, useQuery } from "convex/react";
import { api } from "../convex/_generated/api";
import { useEffect, useState } from "react";

export function EntityExplorer({ groupId }: { groupId: string }) {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const fetchGroupData = useAction(api.graphiti.fetchGroupDataIfChanged);
  const startPolling = useMutation(api.graphiti.startGroupPolling);
  const stopPolling = useMutation(api.graphiti.stopGroupPolling);
  
  useEffect(() => {
    // Start polling for this group
    startPolling({ groupId, pollInterval: 30000 }); // 30 seconds
    
    // Initial data fetch
    loadData();
    
    return () => {
      // Stop polling when component unmounts
      stopPolling({ groupId });
    };
  }, [groupId]);
  
  const loadData = async () => {
    setLoading(true);
    try {
      const result = await fetchGroupData({ groupId });
      setEntities(result.data.entities);
      console.log(result.fromCache ? "Loaded from cache" : "Fetched fresh data");
    } catch (error) {
      console.error("Error loading data:", error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <h2>Entities for Group: {groupId}</h2>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div>
          {entities.map((entity) => (
            <EntityCard key={entity.uuid} entity={entity} />
          ))}
        </div>
      )}
      <button onClick={loadData}>Refresh</button>
    </div>
  );
}
```

This caching system provides:
- **Efficient polling** with change detection
- **Automatic cache invalidation** when data changes
- **Configurable poll intervals** per group
- **Entity-level caching** for detailed views
- **Fallback mechanisms** for error handling

The system only fetches data when actually needed, dramatically reducing API calls and improving performance! 🚀
