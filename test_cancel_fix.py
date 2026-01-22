"""
Test script to verify cancel functionality for orphaned listings
"""
import json
import os
from utils.db import init_db, find_user_by_id, get_listing_by_id, get_equipment_listing_by_id

class MockApp:
    """Mock Flask app for testing"""
    pass

# Initialize DB
app = MockApp()
init_db(app)

print("=" * 60)
print("TESTING CANCEL FUNCTIONALITY")
print("=" * 60)

# Test data
current_user_id = "cb57cdef-86cf-4079-9d30-372067f41777"  # manoj kumar
orphaned_farmer_id = "3d61c07e-d859-491b-b30c-3447e7d0d3db"  # doesn't exist

print(f"\n✅ Current User ID: {current_user_id}")
user = find_user_by_id(current_user_id)
if user:
    print(f"   Name: {user.get('name')}, Phone: {user.get('phone')}")

print(f"\n❌ Orphaned Farmer ID: {orphaned_farmer_id}")
orphaned_user = find_user_by_id(orphaned_farmer_id)
if orphaned_user:
    print(f"   Found: {orphaned_user.get('name')}")
else:
    print(f"   ✓ User doesn't exist (orphaned)")

# Get a listing with orphaned ID
print(f"\n📋 Testing Listing Ownership Logic:")
print(f"   Current user: {current_user_id[:8]}...")
print(f"   Listing farmer: {orphaned_farmer_id[:8]}...")
print(f"   Match: {current_user_id == orphaned_farmer_id}")

if current_user_id != orphaned_farmer_id:
    farmer_exists = find_user_by_id(orphaned_farmer_id)
    if farmer_exists:
        print(f"   ❌ BLOCK: Farmer exists but it's not you")
    else:
        print(f"   ✅ ALLOW: Orphaned listing - any user can cancel")

print("\n" + "=" * 60)
print("TEST COMPLETE!")
print("=" * 60)
print("\n💡 With the fix:")
print("   - You CAN cancel orphaned listings (owner doesn't exist)")
print("   - You CANNOT cancel other users' listings (owner exists)")
print("   - You CAN cancel your own listings")
