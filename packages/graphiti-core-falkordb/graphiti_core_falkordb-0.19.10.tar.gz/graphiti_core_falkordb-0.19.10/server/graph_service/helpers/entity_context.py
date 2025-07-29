"""
Helper functions for formatting comprehensive entity context for LLM prompting.
"""

from typing import Dict, List, Any, Optional
from graphiti_core_falkordb.nodes import EntityNode
from graph_service.dto import NavigationLink, NavigationLinks


def format_comprehensive_context(data: Dict[str, Any]) -> str:
    """Format all entity data into rich, nuanced context for LLM."""
    entity = data["entity"]
    relationships = data["relationships"]
    episodes = data.get("episodes", [])
    communities = data.get("communities", [])
    
    # Entity type (primary label)
    entity_type = next((label for label in entity.labels if label != 'Entity'), 'Entity')
    
    context_parts = [
        f"=== ENTITY PROFILE ===",
        f"Name: {entity.name}",
        f"Type: {entity_type}",
        f"UUID: {entity.uuid}",
        f"Summary: {entity.summary}",
        f"Created: {entity.created_at}",
        f"Labels: {', '.join(entity.labels)}"
    ]
    
    # Detailed attributes
    if entity.attributes:
        context_parts.append("\n=== ATTRIBUTES ===")
        for key, value in entity.attributes.items():
            context_parts.append(f"{key}: {value}")
    
    # Direct relationships (1-hop outgoing) - sorted by relevance
    if relationships.get('outgoing_1hop'):
        context_parts.append("\n=== DIRECT RELATIONSHIPS (OUTGOING) ===")
        # Sort by relevance score if available, otherwise by creation date
        sorted_outgoing = sorted(
            relationships['outgoing_1hop'],
            key=lambda x: (x.get('relevance_score', 0.5), x.get('created_at', '')),
            reverse=True
        )
        for rel in sorted_outgoing:
            # Safely get target labels with fallback
            target_labels = rel.get('target_labels', [])
            target_type = next((label for label in target_labels if label != 'Entity'), 'Entity') if target_labels else 'Entity'
            relevance_indicator = "🔥" if rel.get('relevance_score', 0.5) >= 0.9 else "⭐" if rel.get('relevance_score', 0.5) >= 0.7 else ""
            context_parts.append(
                f"• {relevance_indicator} {rel['fact']}"
                f"\n  → Links to: {rel['target_name']} (UUID: {rel['target_uuid']}, Type: {target_type})"
                f"\n  → Target Summary: {rel['target_summary']}"
                f"\n  → Relationship Type: {rel['relationship_type']}"
                f"\n  → Valid: {rel['valid_at']} to {rel['invalid_at'] or 'ongoing'}"
            )
            if rel.get('relevance_score'):
                context_parts.append(f"  → Relevance: {rel['relevance_score']:.2f}")
            target_attributes = rel.get('target_attributes', {})
            if target_attributes:
                key_attrs = {k: v for k, v in target_attributes.items()
                           if k in ['email', 'phone', 'company', 'title', 'status', 'role', 'department']}
                if key_attrs:
                    context_parts.append(f"  → Key Attributes: {key_attrs}")
            context_parts.append("")
    
    # Direct relationships (1-hop incoming) - sorted by relevance
    if relationships.get('incoming_1hop'):
        context_parts.append("=== DIRECT RELATIONSHIPS (INCOMING) ===")
        # Sort by relevance score if available, otherwise by creation date
        sorted_incoming = sorted(
            relationships['incoming_1hop'],
            key=lambda x: (x.get('relevance_score', 0.5), x.get('created_at', '')),
            reverse=True
        )
        for rel in sorted_incoming:
            # Safely get source labels with fallback
            source_labels = rel.get('source_labels', [])
            source_type = next((label for label in source_labels if label != 'Entity'), 'Entity') if source_labels else 'Entity'
            relevance_indicator = "🔥" if rel.get('relevance_score', 0.5) >= 0.9 else "⭐" if rel.get('relevance_score', 0.5) >= 0.7 else ""
            context_parts.append(
                f"• {relevance_indicator} {rel['fact']}"
                f"\n  ← Links from: {rel['source_name']} (UUID: {rel['source_uuid']}, Type: {source_type})"
                f"\n  ← Source Summary: {rel['source_summary']}"
                f"\n  ← Relationship Type: {rel['relationship_type']}"
                f"\n  ← Valid: {rel['valid_at']} to {rel['invalid_at'] or 'ongoing'}"
            )
            if rel.get('relevance_score'):
                context_parts.append(f"  ← Relevance: {rel['relevance_score']:.2f}")
            source_attributes = rel.get('source_attributes', {})
            if source_attributes:
                key_attrs = {k: v for k, v in source_attributes.items()
                           if k in ['email', 'phone', 'company', 'title', 'status', 'role', 'department']}
                if key_attrs:
                    context_parts.append(f"  ← Key Attributes: {key_attrs}")
            context_parts.append("")
    
    # Second-hop relationships - sorted by relevance
    if relationships.get('outgoing_2hop'):
        context_parts.append("=== EXTENDED NETWORK (2-HOP RELATIONSHIPS) ===")
        # Sort by relevance score if available, otherwise by creation date
        sorted_2hop = sorted(
            relationships['outgoing_2hop'],
            key=lambda x: (x.get('relevance_score', 0.5), x.get('created_at', '')),
            reverse=True
        )
        for rel in sorted_2hop:
            # Safely get target labels with fallback
            target_labels = rel.get('target_labels', [])
            target_type = next((label for label in target_labels if label != 'Entity'), 'Entity') if target_labels else 'Entity'
            relevance_indicator = "🔥" if rel.get('relevance_score', 0.5) >= 0.8 else "⭐" if rel.get('relevance_score', 0.5) >= 0.6 else "💡"
            context_parts.append(
                f"• {relevance_indicator} {rel['fact']}"
                f"\n  → Connection Path: {rel['path']}"
                f"\n  → Final Target: {rel['target_name']} (UUID: {rel['target_uuid']}, Type: {target_type})"
                f"\n  → Via: {rel['intermediate_entity']} (UUID: {rel['intermediate_uuid']})"
                f"\n  → Target Summary: {rel['target_summary']}"
            )
            if rel.get('relevance_score'):
                context_parts.append(f"  → Relevance: {rel['relevance_score']:.2f}")
            context_parts.append("")
    
    # Episodic context - sorted by relevance and recency
    if episodes:
        context_parts.append("=== EPISODIC CONTEXT ===")
        # Sort by relevance score if available, otherwise by creation date
        sorted_episodes = sorted(
            episodes,
            key=lambda x: (x.get('relevance_score', 0.5), x.get('created_at', '')),
            reverse=True
        )
        for episode in sorted_episodes:
            relevance_indicator = "🔥" if episode.get('relevance_score', 0.5) >= 0.9 else "⭐" if episode.get('relevance_score', 0.5) >= 0.7 else ""
            context_parts.append(
                f"• {relevance_indicator} Episode: {episode['episode_name']} (UUID: {episode['episode_uuid']})"
                f"\n  Type: {episode['episode_type']}"
                f"\n  Created: {episode['created_at']}"
                f"\n  Content Preview: {episode['episode_content']}..."
            )
            if episode.get('relevance_score'):
                context_parts.append(f"  Relevance: {episode['relevance_score']:.2f}")
            context_parts.append("")
    
    # Community context
    if communities:
        context_parts.append("=== COMMUNITY MEMBERSHIPS ===")
        for community in communities:
            context_parts.append(
                f"• Community: {community['community_name']} (UUID: {community['community_uuid']})"
                f"\n  Level: {community['community_level']}"
                f"\n  Summary: {community['community_summary']}"
            )
            context_parts.append("")
    
    context_parts.append("=== NAVIGATION INSTRUCTIONS ===")
    context_parts.append("When referencing other entities, always include their UUID in format: [Entity Name](UUID: entity-uuid)")
    context_parts.append("This allows the user to click through to explore related entities in detail.")
    context_parts.append("Suggest the most relevant entities to explore next based on the analysis.")
    context_parts.append("")
    context_parts.append("RELEVANCE INDICATORS:")
    context_parts.append("🔥 = High relevance (recent, active, or strongly connected)")
    context_parts.append("⭐ = Medium relevance (important but less recent)")
    context_parts.append("💡 = Extended network (2-hop connections worth exploring)")
    context_parts.append("")
    context_parts.append("OPTIMIZATION NOTES:")
    context_parts.append("- Results are sorted by relevance score and recency")
    context_parts.append("- Recent relationships (last 30 days) are prioritized")
    context_parts.append("- 2-hop relationships show extended network opportunities")
    context_parts.append("- Focus on high-relevance entities for most valuable insights")
    
    return "\n".join(context_parts)


def extract_navigation_links(data: Dict[str, Any]) -> NavigationLinks:
    """Extract all clickable entity UUIDs for frontend navigation."""
    relationships = data["relationships"]
    episodes = data.get("episodes", [])
    communities = data.get("communities", [])
    
    direct_entities = []
    extended_entities = []
    
    # Direct relationship entities (outgoing)
    if relationships.get('outgoing_1hop'):
        for rel in relationships['outgoing_1hop']:
            target_labels = rel.get('target_labels', [])
            target_type = next((label for label in target_labels if label != 'Entity'), 'Entity') if target_labels else 'Entity'
            # Only add if we have valid data
            target_uuid = rel.get('target_uuid')
            target_name = rel.get('target_name')
            if target_uuid and target_name:
                direct_entities.append(NavigationLink(
                    uuid=target_uuid,
                    name=target_name,
                    type=target_type,
                    relationship=rel.get('fact', '')
                ))
    
    # Direct relationship entities (incoming)
    if relationships.get('incoming_1hop'):
        for rel in relationships['incoming_1hop']:
            source_labels = rel.get('source_labels', [])
            source_type = next((label for label in source_labels if label != 'Entity'), 'Entity') if source_labels else 'Entity'
            # Only add if we have valid data
            source_uuid = rel.get('source_uuid')
            source_name = rel.get('source_name')
            if source_uuid and source_name:
                direct_entities.append(NavigationLink(
                    uuid=source_uuid,
                    name=source_name,
                    type=source_type,
                    relationship=rel.get('fact', '')
                ))
    
    # Extended network entities (2-hop)
    if relationships.get('outgoing_2hop'):
        for rel in relationships['outgoing_2hop']:
            # Add intermediate entity if valid
            intermediate_uuid = rel.get('intermediate_uuid')
            intermediate_name = rel.get('intermediate_entity')
            if intermediate_uuid and intermediate_name:
                extended_entities.append(NavigationLink(
                    uuid=intermediate_uuid,
                    name=intermediate_name,
                    type="intermediate",
                    path=rel.get('path', '')
                ))

            # Add final target entity if valid
            target_uuid = rel.get('target_uuid')
            target_name = rel.get('target_name')
            if target_uuid and target_name:
                target_labels = rel.get('target_labels', [])
                target_type = next((label for label in target_labels if label != 'Entity'), 'Entity') if target_labels else 'Entity'
                extended_entities.append(NavigationLink(
                    uuid=target_uuid,
                    name=target_name,
                    type=target_type,
                    path=rel.get('path', '')
                ))
    
    # Episodes
    episode_links = [
        NavigationLink(
            uuid=ep.get('episode_uuid', ''),
            name=ep.get('episode_name', 'Unknown Episode'),
            type="episode"
        )
        for ep in episodes if ep.get('episode_uuid')
    ]

    # Communities
    community_links = [
        NavigationLink(
            uuid=comm.get('community_uuid', ''),
            name=comm.get('community_name', 'Unknown Community'),
            type="community"
        )
        for comm in communities if comm.get('community_uuid')
    ]
    
    return NavigationLinks(
        direct_entities=direct_entities,
        extended_entities=extended_entities,
        episodes=episode_links,
        communities=community_links
    )


def get_primary_entity_type(labels: List[str]) -> str:
    """Get the primary entity type from labels."""
    entity_labels = [label for label in labels if label != 'Entity']
    return entity_labels[0] if entity_labels else 'Entity'


def truncate_content(content: str, max_length: int = 500) -> str:
    """Truncate content with ellipsis if too long."""
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


def extract_key_attributes(attributes: Dict[str, Any], priority_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """Extract key attributes for display."""
    if priority_keys is None:
        priority_keys = ['email', 'phone', 'company', 'title', 'status', 'role', 'department', 'type', 'category']
    
    key_attrs = {}
    for key in priority_keys:
        if key in attributes:
            key_attrs[key] = attributes[key]
    
    return key_attrs
