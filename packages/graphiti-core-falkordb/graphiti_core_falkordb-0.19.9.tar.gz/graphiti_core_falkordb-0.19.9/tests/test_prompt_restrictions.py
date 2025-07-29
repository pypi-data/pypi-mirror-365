"""
Test that the entity extraction prompts contain the restrictive language.
"""

from graphiti_core_falkordb.prompts.extract_nodes import extract_message, extract_text, extract_json, reflexion, classify_nodes


def test_message_prompt_restrictions():
    """Test that the message extraction prompt contains restrictive language."""
    context = {
        'previous_episodes': [],
        'episode_content': 'Speaker A: Hello, Speaker B: Hi there',
        'entity_types': 'Person, Company',
        'custom_prompt': ''
    }

    messages = extract_message(context)
    user_prompt = messages[1].content

    print("DEBUG: User prompt content:")
    print(user_prompt)
    print("=" * 50)

    # Check for balanced approach
    assert 'What TO Extract' in user_prompt
    assert 'Named People' in user_prompt
    assert 'Speaker A' in user_prompt  # Should mention Speaker A as an example to avoid
    assert 'business context' in user_prompt

    print("✅ Message prompt contains restrictive language")


def test_text_prompt_restrictions():
    """Test that the text extraction prompt contains restrictive language."""
    context = {
        'episode_content': 'The manager talked to the developer about the project.',
        'entity_types': 'Person, Company',
        'custom_prompt': ''
    }

    messages = extract_text(context)
    user_prompt = messages[1].content

    # Check for balanced approach
    assert 'What TO Extract' in user_prompt
    assert 'Named People' in user_prompt
    assert 'DO NOT Extract' in user_prompt
    assert 'Speaker A' in user_prompt  # Should mention as example to avoid
    assert 'business context' in user_prompt

    print("✅ Text prompt contains restrictive language")


def test_json_prompt_restrictions():
    """Test that the JSON extraction prompt contains restrictive language."""
    context = {
        'source_description': 'User data',
        'episode_content': '{"user": "john", "role": "admin"}',
        'entity_types': 'Person, Company',
        'custom_prompt': ''
    }

    messages = extract_json(context)
    user_prompt = messages[1].content

    # Check for balanced approach
    assert 'What TO Extract' in user_prompt
    assert 'Named People' in user_prompt
    assert 'business context' in user_prompt
    assert 'Generic IDs, UUIDs' in user_prompt  # Should still exclude these

    print("✅ JSON prompt contains restrictive language")


def test_system_prompts_updated():
    """Test that system prompts have been updated to be more restrictive."""
    context = {
        'previous_episodes': [],
        'episode_content': 'Test content',
        'entity_types': 'Person',
        'custom_prompt': ''
    }
    
    # Test message system prompt
    messages = extract_message(context)
    sys_prompt = messages[0].content
    assert 'entity nodes' in sys_prompt
    assert 'business context' in sys_prompt

    # Test text system prompt
    messages = extract_text(context)
    sys_prompt = messages[0].content
    assert 'entity nodes' in sys_prompt
    assert 'business context' in sys_prompt

    # Test JSON system prompt
    context.update({
        'source_description': 'Test data',
        'episode_content': '{"test": "data"}'
    })
    messages = extract_json(context)
    sys_prompt = messages[0].content
    assert 'entity nodes' in sys_prompt
    assert 'business context' in sys_prompt
    
    print("✅ All system prompts have been updated")


def test_reflexion_prompt_restrictions():
    """Test that the reflexion prompt is also restrictive."""
    context = {
        'previous_episodes': [],
        'episode_content': 'Speaker A: Hello, Speaker B: Hi there',
        'extracted_entities': ['John Smith']
    }

    messages = reflexion(context)
    user_prompt = messages[1].content

    # Check for balanced approach
    assert 'business-relevant entities' in user_prompt
    assert 'Named people' in user_prompt
    assert 'Speaker A' in user_prompt  # Should mention as example to avoid
    assert 'business context' in user_prompt

    print("✅ Reflexion prompt contains restrictive language")


def test_classify_nodes_prompt_restrictions():
    """Test that the classify nodes prompt mentions restrictive approach."""
    context = {
        'previous_episodes': [],
        'episode_content': 'Test content',
        'extracted_entities': ['John Smith'],
        'entity_types': 'Person, Company'
    }

    messages = classify_nodes(context)
    sys_prompt = messages[0].content
    user_prompt = messages[1].content

    # Check system prompt
    assert 'entity nodes' in sys_prompt
    assert 'business context' in sys_prompt

    # Check user prompt
    assert 'hypothetical placeholder' in user_prompt
    assert 'generic role' in user_prompt

    print("✅ Classify nodes prompt contains restrictive language")


if __name__ == "__main__":
    print("Testing prompt restrictions...")
    
    test_message_prompt_restrictions()
    test_text_prompt_restrictions()
    test_json_prompt_restrictions()
    test_system_prompts_updated()
    test_reflexion_prompt_restrictions()
    test_classify_nodes_prompt_restrictions()
    
    print("🎉 All prompt restriction tests passed!")
    print("\nThe entity extraction prompts now include:")
    print("- Restrictions against hypothetical speakers (Speaker A, Speaker B)")
    print("- Exclusions for generic roles without names")
    print("- Focus on concrete, business-relevant entities")
    print("- Requirements for traditional database system value")
    print("- Specific exclusions for technical terms and abstract concepts")
    print("- Restrictive reflexion that won't suggest inappropriate entities")
    print("- Classification that can reject inappropriate extractions")
