"""
Demo showing how the restrictive entity extraction works.

This example shows the difference between what would be extracted before and after
the restrictive changes to entity extraction prompts.
"""

from graphiti_core_falkordb.prompts.extract_nodes import extract_message, extract_text


def demo_restrictive_extraction():
    """Demonstrate the restrictive entity extraction prompts."""
    
    print("🔍 RESTRICTIVE ENTITY EXTRACTION DEMO")
    print("=" * 50)
    
    # Example 1: Hypothetical speakers (should NOT be extracted)
    print("\n📝 Example 1: Hypothetical Speakers")
    print("Input: 'Speaker A: I think we should hire John Smith. Speaker B: Yes, from Microsoft.'")
    
    context = {
        'previous_episodes': [],
        'episode_content': 'Speaker A: I think we should hire John Smith. Speaker B: Yes, from Microsoft.',
        'entity_types': [
            {'entity_type_id': 0, 'entity_type_name': 'Entity', 'entity_type_description': 'Default entity'},
            {'entity_type_id': 1, 'entity_type_name': 'Person', 'entity_type_description': 'A person'},
            {'entity_type_id': 2, 'entity_type_name': 'Company', 'entity_type_description': 'A company'}
        ],
        'custom_prompt': ''
    }
    
    messages = extract_message(context)
    prompt = messages[1].content
    
    print("\n✅ SHOULD extract: John Smith (concrete person), Microsoft (concrete company)")
    print("❌ SHOULD NOT extract: Speaker A, Speaker B (hypothetical placeholders)")
    print("\n📋 Key prompt restrictions:")
    print("- 'DO NOT extract generic speakers like \"Speaker A\", \"Speaker B\"'")
    print("- 'ONLY extract the speaker if they are a real, named person'")
    
    # Example 2: Generic roles (should NOT be extracted)
    print("\n" + "=" * 50)
    print("📝 Example 2: Generic Roles")
    print("Input: 'The manager discussed the project with the developer and a customer.'")
    
    context = {
        'episode_content': 'The manager discussed the project with the developer and a customer.',
        'entity_types': [
            {'entity_type_id': 0, 'entity_type_name': 'Entity', 'entity_type_description': 'Default entity'},
            {'entity_type_id': 1, 'entity_type_name': 'Person', 'entity_type_description': 'A person'}
        ],
        'custom_prompt': ''
    }
    
    messages = extract_text(context)
    prompt = messages[1].content
    
    print("\n✅ SHOULD extract: (none - no concrete named entities)")
    print("❌ SHOULD NOT extract: manager, developer, customer (generic roles without names)")
    print("\n📋 Key prompt restrictions:")
    print("- 'Generic roles without names (\"the manager\", \"a customer\", \"the developer\")'")
    print("- 'Only extract entities with specific names that have clear business value'")
    
    # Example 3: Concrete entities (SHOULD be extracted)
    print("\n" + "=" * 50)
    print("📝 Example 3: Concrete Business Entities")
    print("Input: 'Sarah Johnson from Acme Corp called about Project Alpha.'")
    
    context = {
        'episode_content': 'Sarah Johnson from Acme Corp called about Project Alpha.',
        'entity_types': [
            {'entity_type_id': 0, 'entity_type_name': 'Entity', 'entity_type_description': 'Default entity'},
            {'entity_type_id': 1, 'entity_type_name': 'Person', 'entity_type_description': 'A person'},
            {'entity_type_id': 2, 'entity_type_name': 'Company', 'entity_type_description': 'A company'},
            {'entity_type_id': 3, 'entity_type_name': 'Project', 'entity_type_description': 'A project'}
        ],
        'custom_prompt': ''
    }
    
    messages = extract_text(context)
    prompt = messages[1].content
    
    print("\n✅ SHOULD extract: Sarah Johnson (Person), Acme Corp (Company), Project Alpha (Project)")
    print("❌ SHOULD NOT extract: (none - all entities are concrete and business-relevant)")
    print("\n📋 Key prompt requirements:")
    print("- 'Concrete and specific - Real people, companies, projects, products, etc. with actual names'")
    print("- 'Business-relevant - Would be tracked in a CRM, project management, or knowledge management system'")
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY OF RESTRICTIVE CHANGES")
    print("=" * 50)
    print("✅ WILL extract:")
    print("  • Named people (John Smith, Sarah Johnson)")
    print("  • Named companies (Microsoft, Acme Corp)")
    print("  • Named projects (Project Alpha)")
    print("  • Named products/services with business value")
    print("  • Concrete entities that would appear in traditional databases")
    
    print("\n❌ WILL NOT extract:")
    print("  • Hypothetical speakers (Speaker A, Speaker B)")
    print("  • Generic roles (the manager, a customer, the developer)")
    print("  • Abstract concepts (the weather, the situation)")
    print("  • Technical terms (the system, the API)")
    print("  • Pronouns (he, she, it, this, that)")
    print("  • Temporal references (today, yesterday)")
    print("  • Actions/relationships (meeting, discussion)")
    
    print("\n🔧 IMPLEMENTATION:")
    print("  • Updated system prompts to emphasize 'concrete, business-relevant entities'")
    print("  • Added 'CRITICAL RESTRICTIONS' section with specific exclusions")
    print("  • Focused on 'traditional database system (CRM, KMS, IMS)' value")
    print("  • Required 'explicit names' and 'high confidence' for extraction")


if __name__ == "__main__":
    demo_restrictive_extraction()
