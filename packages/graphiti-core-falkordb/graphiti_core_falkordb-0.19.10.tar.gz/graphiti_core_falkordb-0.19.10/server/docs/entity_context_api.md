# Entity Context API - Maximum Nuance for LLM Prompting

This document describes the comprehensive entity context endpoint that provides maximum nuance and clickable navigation for LLM-powered entity exploration.

## Overview

The Entity Context API endpoint (`GET /entities/{uuid}/context`) is designed to provide rich, comprehensive context about any entity in your knowledge graph. It's optimized for:

- **LLM Prompting**: Rich, formatted context ready for AI analysis
- **Maximum Nuance**: Multi-hop relationships, episodes, communities, and detailed attributes
- **Clickable Navigation**: UUID-based links for exploring related entities
- **Deep Exploration**: 2-hop relationship traversal for extended network analysis

## Endpoint

**GET** `/entities/{uuid}/context`

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `uuid` | string | The UUID of the entity to get context for |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_relationships` | integer | 50 | Maximum number of relationships to include (1-100) |
| `relationship_depth` | integer | 2 | Depth of relationship traversal (1-3) |
| `include_episodes` | boolean | true | Include related episodes/conversations |
| `include_communities` | boolean | true | Include community memberships |
| `min_score` | float | 0.4 | Minimum relevance score (0.0-1.0, lower = more inclusive) |
| `use_cross_encoder` | boolean | true | Use cross-encoder reranking for better quality |

### Response Format

```json
{
  "entity_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "entity_name": "John Doe",
  "context": "=== ENTITY PROFILE ===\nName: John Doe\nType: Person\n...",
  "navigation_links": {
    "direct_entities": [
      {
        "uuid": "company-uuid-123",
        "name": "Tech Corp",
        "type": "Company",
        "relationship": "John Doe works at Tech Corp as Senior Engineer"
      }
    ],
    "extended_entities": [
      {
        "uuid": "location-uuid-456", 
        "name": "San Francisco",
        "type": "Location",
        "path": "John Doe -> Tech Corp -> San Francisco"
      }
    ],
    "episodes": [
      {
        "uuid": "episode-uuid-789",
        "name": "Team Meeting Notes",
        "type": "episode"
      }
    ],
    "communities": [
      {
        "uuid": "community-uuid-101",
        "name": "Engineering Team",
        "type": "community"
      }
    ]
  },
  "raw_data": {
    "entity": { /* Full entity data */ },
    "relationships": { /* Relationship details */ },
    "episodes": [ /* Episode data */ ],
    "communities": [ /* Community data */ ]
  }
}
```

## Context Format

The `context` field provides a rich, structured format perfect for LLM consumption:

### Sections Included

1. **Entity Profile**: Name, type, UUID, summary, creation date, labels
2. **Attributes**: All entity attributes with key-value pairs
3. **Direct Relationships (Outgoing)**: 1-hop relationships where this entity is the source
4. **Direct Relationships (Incoming)**: 1-hop relationships where this entity is the target
5. **Extended Network**: 2-hop relationships showing indirect connections
6. **Episodic Context**: Related episodes/conversations mentioning this entity
7. **Community Memberships**: Communities this entity belongs to
8. **Navigation Instructions**: Guidelines for the LLM on how to reference other entities

### Example Context Output

```
=== ENTITY PROFILE ===
Name: John Doe
Type: Person
UUID: 550e8400-e29b-41d4-a716-446655440000
Summary: Senior software engineer specializing in cloud architecture
Created: 2024-01-15T10:30:00Z
Labels: Entity, Person, Employee

=== ATTRIBUTES ===
email: john.doe@techcorp.com
phone: +1-555-0123
department: Engineering
title: Senior Software Engineer
hire_date: 2022-03-15
skills: Python, AWS, Kubernetes

=== DIRECT RELATIONSHIPS (OUTGOING) ===
• John Doe works at Tech Corp as a senior software engineer
  → Links to: Tech Corp (UUID: company-uuid-123, Type: Company)
  → Target Summary: Leading technology company specializing in cloud solutions
  → Relationship Type: works_at
  → Valid: 2022-03-15T00:00:00Z to ongoing
  → Key Attributes: {industry: Technology, size: 500, location: San Francisco}

• John Doe leads the CloudSync project for data management solutions
  → Links to: CloudSync (UUID: project-uuid-456, Type: Project)
  → Target Summary: Enterprise data synchronization platform
  → Relationship Type: leads
  → Valid: 2023-06-01T00:00:00Z to ongoing

=== DIRECT RELATIONSHIPS (INCOMING) ===
• Tech Corp employs John Doe in the engineering department
  ← Links from: Tech Corp (UUID: company-uuid-123, Type: Company)
  ← Source Summary: Leading technology company specializing in cloud solutions
  ← Relationship Type: employs
  ← Valid: 2022-03-15T00:00:00Z to ongoing

=== EXTENDED NETWORK (2-HOP RELATIONSHIPS) ===
• Tech Corp is headquartered in San Francisco for strategic market access
  → Connection Path: John Doe -> Tech Corp -> San Francisco
  → Final Target: San Francisco (UUID: location-uuid-789, Type: Location)
  → Via: Tech Corp (UUID: company-uuid-123)
  → Target Summary: Major technology hub on the US West Coast

=== EPISODIC CONTEXT ===
• Episode: Q4 Performance Review (UUID: episode-uuid-101)
  Type: meeting
  Created: 2024-01-10T14:00:00Z
  Content Preview: John demonstrated exceptional leadership in the CloudSync project, delivering ahead of schedule and mentoring junior developers...

=== COMMUNITY MEMBERSHIPS ===
• Community: Engineering Leadership (UUID: community-uuid-201)
  Level: 2
  Summary: Senior engineers and technical leads within the organization

=== NAVIGATION INSTRUCTIONS ===
When referencing other entities, always include their UUID in format: [Entity Name](UUID: entity-uuid)
This allows the user to click through to explore related entities in detail.
Suggest the most relevant entities to explore next based on the analysis.
```

## Usage Examples

### Basic API Call

```bash
curl "http://localhost:8000/entities/550e8400-e29b-41d4-a716-446655440000/context"
```

### Advanced Configuration

```bash
curl "http://localhost:8000/entities/550e8400-e29b-41d4-a716-446655440000/context?max_relationships=100&relationship_depth=3&include_episodes=true&include_communities=true"
```

### LLM Integration

```python
import httpx

async def analyze_entity_with_llm(entity_uuid: str, question: str):
    # Get comprehensive context
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/entities/{entity_uuid}/context",
            params={
                "max_relationships": 50,
                "relationship_depth": 2,
                "include_episodes": True,
                "include_communities": True
            }
        )
        context_data = response.json()
    
    # Create LLM prompt
    prompt = f"""
    Analyze this entity and provide insights:

    {context_data['context']}

    Question: {question}

    Please:
    1. Provide a comprehensive analysis
    2. Identify key relationships and patterns
    3. Suggest related entities to explore next (use UUID format: [Entity Name](UUID: entity-uuid))
    4. Highlight any opportunities or concerns

    Analysis:
    """
    
    # Send to LLM (example with OpenAI)
    llm_response = await openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return {
        "analysis": llm_response.choices[0].message.content,
        "navigation_links": context_data['navigation_links'],
        "entity_name": context_data['entity_name']
    }
```

### Frontend Integration

```typescript
interface EntityContextData {
  entity_uuid: string;
  entity_name: string;
  context: string;
  navigation_links: NavigationLinks;
  raw_data: any;
}

const EntityExplorer = ({ initialEntityUuid }: { initialEntityUuid: string }) => {
  const [currentEntity, setCurrentEntity] = useState<string>(initialEntityUuid);
  const [contextData, setContextData] = useState<EntityContextData | null>(null);
  const [llmAnalysis, setLlmAnalysis] = useState<string>("");

  const loadEntityContext = async (entityUuid: string) => {
    const response = await fetch(`/api/entities/${entityUuid}/context`);
    const data = await response.json();
    setContextData(data);
    
    // Get LLM analysis
    const analysisResponse = await fetch('/api/analyze-entity', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        context: data.context,
        question: "Provide key insights and suggest next entities to explore"
      })
    });
    const analysis = await analysisResponse.text();
    setLlmAnalysis(analysis);
  };

  const handleEntityClick = (uuid: string) => {
    setCurrentEntity(uuid);
    loadEntityContext(uuid);
  };

  const renderAnalysisWithLinks = (analysis: string) => {
    // Replace UUID references with clickable links
    return analysis.replace(
      /\[([^\]]+)\]\(UUID: ([^)]+)\)/g,
      '<span class="entity-link cursor-pointer text-blue-600 underline" onClick={() => handleEntityClick("$2")}>$1</span>'
    );
  };

  return (
    <div className="entity-explorer">
      <div className="entity-context">
        <h2>{contextData?.entity_name}</h2>
        <pre className="context-display">{contextData?.context}</pre>
      </div>
      
      <div className="llm-analysis">
        <h3>AI Analysis</h3>
        <div dangerouslySetInnerHTML={{ 
          __html: renderAnalysisWithLinks(llmAnalysis) 
        }} />
      </div>
      
      <div className="quick-navigation">
        <h4>Quick Navigation</h4>
        {contextData?.navigation_links.direct_entities.map(link => (
          <button 
            key={link.uuid}
            onClick={() => handleEntityClick(link.uuid)}
            className="nav-button"
          >
            {link.name} ({link.type})
          </button>
        ))}
      </div>
    </div>
  );
};
```

## Best Practices

1. **Start with Default Parameters**: The defaults provide good balance of detail vs. performance
2. **Use Relationship Depth Wisely**: Depth 2 is usually sufficient; depth 3 can be overwhelming
3. **Cache Results**: Entity context can be cached since it changes infrequently
4. **Parse UUID References**: Extract UUIDs from LLM responses for navigation
5. **Handle Large Contexts**: Consider truncating very large contexts for LLM token limits
6. **Progressive Loading**: Load basic context first, then extended relationships on demand

## Performance Considerations

- **Query Complexity**: Higher relationship depth and max_relationships increase query time
- **Memory Usage**: Large contexts consume more memory; adjust limits based on your needs
- **Database Load**: Consider caching for frequently accessed entities
- **LLM Token Limits**: Very comprehensive contexts may exceed token limits for some models

This endpoint provides the richest possible context for entity exploration and LLM-powered analysis, enabling sophisticated knowledge graph navigation and insights.
