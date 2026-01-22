"""
Test script to verify user lookup functionality
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.db import find_user_by_id, init_db

# Initialize DB (file-based mode)
class MockApp:
    pass

app = MockApp()
init_db(app)

# Test with actual user ID from the listings
test_user_ids = [
    "3d61c07e-d859-491b-b30c-3447e7d0d3db",
    "a3cad6d8-20da-4983-8390-f464a0512437",
    "aa224240-b3ae-4051-bbfc-1f84797b2439",
    "e948a9c5-9dee-489e-9c69-411d97680cb9",
    "41040df2-29e9-45ac-979a-b9d866618590",
    "cb57cdef-86cf-4079-9d30-372067f41777"  # manoj kumar
]

print("Testing user lookup functionality...")
print("=" * 60)

for user_id in test_user_ids:
    print(f"\nLooking up user ID: {user_id}")
    user = find_user_by_id(user_id)
    if user:
        print(f"  ✅ Found: {user.get('name')} - {user.get('phone')}")
        print(f"     Email: {user.get('email')}")
    else:
        print(f"  ❌ Not found")

print("\n" + "=" * 60)
print("Test complete!")
