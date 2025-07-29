# Restrictive Entity Extraction

## Overview

This document describes the implementation of restrictive entity extraction in Graphiti, designed to extract only concrete, business-relevant entities that would be valuable to track in traditional database systems (CRM, KMS, IMS).

## Problem Statement

Previously, entity extraction was too broad and would extract:
- Hypothetical or placeholder references ("Speaker A", "Speaker B")
- Generic roles without names ("the manager", "a customer", "the developer")
- Abstract concepts and technical terms
- Pronouns and indefinite references

This resulted in a graph populated with entities that had no real business value and made the system less useful for practical applications.

## Solution

We implemented restrictive entity extraction by updating all entity extraction prompts to focus exclusively on concrete, named entities with clear business value.

## Changes Made

### 1. Updated System Prompts

All entity extraction system prompts now emphasize:
- "concrete, business-relevant entity nodes"
- "extremely restrictive - only extract entities with specific names that have clear business value"
- Focus on "traditional database system (CRM, KMS, IMS)" value

### 2. Added Critical Restrictions

All extraction prompts now include a "CRITICAL RESTRICTIONS" section that requires entities to be:
1. **Concrete and specific** - Real people, companies, projects, products, etc. with actual names
2. **Business-relevant** - Would be tracked in a CRM, project management, or knowledge management system
3. **Explicitly named** - Has a proper name, not just a role or placeholder reference

### 3. Specific Exclusions

Added comprehensive "Strict Exclusions" lists that explicitly exclude:
- Hypothetical or placeholder references ("Speaker A", "Person B", "someone", "they")
- Generic roles without names ("the manager", "a customer", "the developer")
- Abstract concepts ("the weather", "the situation", "the problem")
- Technical terms ("the system", "the API", "the database")
- Temporal references ("today", "yesterday", "next week")
- Locations used only as context ("in the office", "at home")
- Pronouns and indefinite references ("he", "she", "it", "this", "that")
- Actions or relationships ("meeting", "discussion", "collaboration")
- Attributes or properties ("red", "large", "important")

### 4. Speaker Extraction Rules

For conversational content, added specific rules:
- ONLY extract the speaker if they are a real, named person (e.g., "John Smith:", "Sarah Johnson:")
- DO NOT extract generic speakers like "Speaker A", "Speaker B", "User", "Assistant", "Person 1", etc.
- DO NOT extract role-based speakers like "Manager:", "Customer:", "Developer:" unless they have actual names

### 5. Updated Reflexion Logic

The reflexion prompt (which suggests missed entities) now:
- Only suggests concrete, business-relevant entities
- Includes the same critical restrictions as extraction prompts
- Won't suggest hypothetical or generic entities that were correctly excluded

### 6. Enhanced Classification

The entity classification prompt now:
- Can reject inappropriate extractions by setting type to None
- Specifically mentions that hypothetical, generic, or abstract entities should be classified as None

## Files Modified

- `graphiti_core/prompts/extract_nodes.py` - All extraction, reflexion, and classification prompts
- `tests/test_prompt_restrictions.py` - Tests to verify restrictive language
- `tests/test_restrictive_entity_extraction.py` - Integration tests (requires Neo4j)
- `examples/restrictive_entity_extraction_demo.py` - Demonstration of changes

## Examples

### Before (Would Extract)
- "Speaker A" and "Speaker B" from transcripts
- "the manager" and "the developer" from business discussions
- "the system" and "the API" from technical conversations

### After (Will Extract)
- "John Smith" and "Sarah Johnson" (named people)
- "Acme Corporation" and "Microsoft" (named companies)
- "Project Alpha" and "Q4 Initiative" (named projects)

### After (Will NOT Extract)
- Hypothetical speakers or placeholders
- Generic roles without specific names
- Abstract concepts or technical terms
- Pronouns or indefinite references

## Benefits

1. **Cleaner Graph**: Only meaningful, actionable entities are stored
2. **Better User Experience**: Users see entities they actually care about
3. **Improved Performance**: Fewer irrelevant entities to process and search
4. **Business Focus**: Aligns with CRM/KMS/IMS use cases
5. **Reduced Noise**: Eliminates confusing or meaningless entity references

## Testing

The implementation includes comprehensive tests:
- Unit tests for prompt content verification
- Integration tests for end-to-end extraction behavior
- Demo scripts showing before/after examples

## Future Considerations

- Monitor extraction quality to ensure important entities aren't being missed
- Consider adding entity type-specific extraction rules
- Evaluate user feedback on entity relevance and completeness
- Potentially add confidence scoring for extracted entities

## Configuration

The restrictive approach is now the default behavior. No configuration changes are needed to benefit from these improvements.
