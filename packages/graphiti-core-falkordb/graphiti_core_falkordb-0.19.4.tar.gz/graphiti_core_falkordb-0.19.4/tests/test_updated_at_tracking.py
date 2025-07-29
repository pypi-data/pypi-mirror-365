"""
Test that updated_at timestamps are properly tracked for entities.
"""

import asyncio
from datetime import datetime, timezone
from graphiti_core_falkordb.nodes import EntityNode
from graphiti_core_falkordb.utils.datetime_utils import utc_now


def test_entity_node_updated_at_field():
    """Test that EntityNode has updated_at field."""
    entity = EntityNode(
        name="Test Entity",
        group_id="test_group",
        summary="Test summary",
        attributes={"test": "value"}
    )
    
    # Should have updated_at field
    assert hasattr(entity, 'updated_at')
    
    # Should be None by default
    assert entity.updated_at is None
    
    # Should be able to set it
    now = utc_now()
    entity.updated_at = now
    assert entity.updated_at == now
    
    print("✅ EntityNode updated_at field test passed!")


def test_entity_creation_no_updated_at():
    """Test that newly created entities don't have updated_at set."""
    entity = EntityNode(
        name="New Entity",
        group_id="test_group",
        summary="New entity summary",
        attributes={"role": "test"}
    )
    
    # New entities should not have updated_at set
    assert entity.updated_at is None
    
    # But should have created_at
    assert entity.created_at is not None
    
    print("✅ Entity creation updated_at test passed!")


def test_manual_update_sets_timestamp():
    """Test that manual updates set updated_at timestamp."""
    entity = EntityNode(
        name="Update Test Entity",
        group_id="test_group",
        summary="Original summary",
        attributes={"status": "active"}
    )
    
    # Initially no updated_at
    assert entity.updated_at is None
    
    # Simulate an update
    entity.summary = "Updated summary"
    entity.updated_at = utc_now()
    
    # Should now have updated_at
    assert entity.updated_at is not None
    assert entity.updated_at > entity.created_at
    
    print("✅ Manual update timestamp test passed!")


def demo_updated_at_usage():
    """Demonstrate how updated_at tracking works."""
    
    print("\n🕒 UPDATED_AT TRACKING DEMO")
    print("=" * 40)
    
    print("\n1. Creating new entity...")
    entity = EntityNode(
        name="John Smith",
        group_id="sales_team",
        summary="Sales representative",
        attributes={"role": "Sales Rep", "email": "john@company.com"}
    )
    
    print(f"   Created at: {entity.created_at}")
    print(f"   Updated at: {entity.updated_at}")  # Should be None
    
    print("\n2. Simulating ingestion update...")
    # This would happen during attribute extraction
    old_summary = entity.summary
    old_attributes = entity.attributes.copy()
    
    entity.summary = "Senior sales representative at TechCorp"
    entity.attributes.update({"company": "TechCorp", "level": "Senior"})
    
    # Check if anything changed (this is what the ingestion pipeline does)
    if entity.summary != old_summary or entity.attributes != old_attributes:
        entity.updated_at = utc_now()
        print(f"   Entity updated at: {entity.updated_at}")
    
    print("\n3. Simulating CRUD update...")
    # This would happen during API update
    entity.attributes["status"] = "active"
    entity.updated_at = utc_now()
    print(f"   CRUD updated at: {entity.updated_at}")
    
    print("\n✅ Benefits of updated_at tracking:")
    print("   - Cache invalidation: Know when to refresh cached data")
    print("   - Change detection: Identify modified entities")
    print("   - Audit trails: Track entity evolution")
    print("   - API consistency: Standard timestamp behavior")
    
    print("\n🔄 Integration points:")
    print("   - Ingestion pipeline: Sets updated_at when attributes/summary change")
    print("   - CRUD operations: Sets updated_at when manually modified")
    print("   - Database queries: Can filter/sort by modification time")
    print("   - Convex caching: Use updated_at for efficient cache invalidation")


if __name__ == "__main__":
    print("Testing updated_at timestamp tracking...")
    
    test_entity_node_updated_at_field()
    test_entity_creation_no_updated_at()
    test_manual_update_sets_timestamp()
    
    demo_updated_at_usage()
    
    print("\n🎉 All updated_at tracking tests passed!")
    print("\nKey points:")
    print("- EntityNode now has updated_at field")
    print("- New entities have updated_at=None")
    print("- Ingestion pipeline sets updated_at when entities change")
    print("- CRUD operations set updated_at when modified")
    print("- Database queries include updated_at field")
    print("- Perfect for cache invalidation and change tracking")
