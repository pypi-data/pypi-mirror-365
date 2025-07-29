#!/usr/bin/env python3
"""
Test script for Entity CRUD operations.
Run this to test the new entity endpoints.
"""

import asyncio
import json
import httpx
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

async def test_entity_crud():
    """Test the entity CRUD operations."""
    
    async with httpx.AsyncClient() as client:
        print("🧪 Testing Entity CRUD Operations")
        print("=" * 50)
        
        # Test 1: Create a Customer entity
        print("\n1. Creating a Customer entity...")
        customer_data = {
            "group_id": "test-group-123",
            "name": "John Doe",
            "entity_type": "Customer",
            "summary": "A potential customer from the tech industry",
            "attributes": {
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-0123",
                "company": "Tech Corp",
                "status": "warm_lead",
                "source": "website",
                "value": "50000",
                "territory": "North America",
                "profile_image_url": "https://example.com/john.jpg",
                "linkedin_url": "https://linkedin.com/in/johndoe"
            }
        }
        
        try:
            response = await client.post(f"{BASE_URL}/entities/", json=customer_data)
            if response.status_code == 201:
                customer = response.json()
                customer_uuid = customer["uuid"]
                print(f"✅ Customer created successfully!")
                print(f"   UUID: {customer_uuid}")
                print(f"   Name: {customer['name']}")
                print(f"   Type: {customer['labels']}")
            else:
                print(f"❌ Failed to create customer: {response.status_code}")
                print(f"   Response: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error creating customer: {e}")
            return
        
        # Test 2: Get the created entity
        print(f"\n2. Retrieving customer {customer_uuid}...")
        try:
            response = await client.get(f"{BASE_URL}/entities/{customer_uuid}")
            if response.status_code == 200:
                retrieved_customer = response.json()
                print("✅ Customer retrieved successfully!")
                print(f"   Name: {retrieved_customer['name']}")
                print(f"   Email: {retrieved_customer['attributes'].get('email', 'N/A')}")
                print(f"   Status: {retrieved_customer['attributes'].get('status', 'N/A')}")
            else:
                print(f"❌ Failed to retrieve customer: {response.status_code}")
        except Exception as e:
            print(f"❌ Error retrieving customer: {e}")
        
        # Test 3: Update the entity
        print(f"\n3. Updating customer {customer_uuid}...")
        update_data = {
            "summary": "Updated: A high-value customer from the tech industry",
            "attributes": {
                "status": "hot_lead",
                "value": "75000",
                "notes": "Very interested in our enterprise solution"
            }
        }
        
        try:
            response = await client.put(f"{BASE_URL}/entities/{customer_uuid}", json=update_data)
            if response.status_code == 200:
                updated_customer = response.json()
                print("✅ Customer updated successfully!")
                print(f"   Status: {updated_customer['attributes'].get('status', 'N/A')}")
                print(f"   Value: {updated_customer['attributes'].get('value', 'N/A')}")
                print(f"   Notes: {updated_customer['attributes'].get('notes', 'N/A')}")
            else:
                print(f"❌ Failed to update customer: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error updating customer: {e}")
        
        # Test 4: Validate the entity
        print(f"\n4. Validating customer {customer_uuid}...")
        try:
            response = await client.get(f"{BASE_URL}/entities/{customer_uuid}/validate")
            if response.status_code == 200:
                validation = response.json()
                print(f"✅ Validation completed!")
                print(f"   Valid: {validation['valid']}")
                print(f"   Entity Type: {validation['entity_type']}")
                if validation['violations']:
                    print(f"   Violations: {validation['violations']}")
            else:
                print(f"❌ Failed to validate customer: {response.status_code}")
        except Exception as e:
            print(f"❌ Error validating customer: {e}")
        
        # Test 5: Create a Project entity
        print("\n5. Creating a Project entity...")
        project_data = {
            "group_id": "test-group-123",
            "name": "Website Redesign",
            "entity_type": "Project",
            "summary": "Complete redesign of the company website",
            "attributes": {
                "name": "Website Redesign",
                "description": "Complete redesign of the company website with modern UI/UX",
                "status": "planning",
                "priority": "high",
                "deadline": "2024-06-30",
                "start_date": "2024-01-15",
                "budget": "100000",
                "owner": "Jane Smith",
                "client": "Tech Corp",
                "project_url": "https://project.example.com/website-redesign"
            }
        }
        
        try:
            response = await client.post(f"{BASE_URL}/entities/", json=project_data)
            if response.status_code == 201:
                project = response.json()
                project_uuid = project["uuid"]
                print(f"✅ Project created successfully!")
                print(f"   UUID: {project_uuid}")
                print(f"   Name: {project['name']}")
                print(f"   Status: {project['attributes'].get('status', 'N/A')}")
            else:
                print(f"❌ Failed to create project: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error creating project: {e}")
        
        # Test 6: List entities (using existing endpoint)
        print(f"\n6. Listing entities in group test-group-123...")
        try:
            response = await client.get(f"{BASE_URL}/entities/test-group-123")
            if response.status_code == 200:
                entities_data = response.json()
                entities = entities_data.get("entities", [])
                print(f"✅ Found {len(entities)} entities:")
                for entity in entities:
                    print(f"   - {entity['name']} ({entity['labels']})")
            else:
                print(f"❌ Failed to list entities: {response.status_code}")
        except Exception as e:
            print(f"❌ Error listing entities: {e}")
        
        # Test 7: Delete the customer entity
        print(f"\n7. Deleting customer {customer_uuid}...")
        try:
            response = await client.delete(f"{BASE_URL}/entities/{customer_uuid}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Customer deleted successfully!")
                print(f"   Message: {result['message']}")
            else:
                print(f"❌ Failed to delete customer: {response.status_code}")
        except Exception as e:
            print(f"❌ Error deleting customer: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Entity CRUD testing completed!")
        print("\nTo run this test:")
        print("1. Make sure the server is running: uvicorn graph_service.main:app --reload")
        print("2. Run this script: python test_entity_crud.py")


if __name__ == "__main__":
    asyncio.run(test_entity_crud())
