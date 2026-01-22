"""
Debug script to check user session and listing creation
"""
from utils.db import init_db, find_user_by_id, find_user_by_email
import json
import os

class MockApp:
    pass

# Initialize
app = MockApp()
init_db(app)

print("=" * 60)
print("USER SESSION DEBUG")
print("=" * 60)

# Check users.json
users_file = 'data/users.json'
print(f"\n📋 Checking {users_file}...")
if os.path.exists(users_file):
    with open(users_file, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    print(f"   Total users: {len(users)}")
    for email, user in users.items():
        print(f"\n   Email: {email}")
        print(f"   Name: {user.get('name')}")
        print(f"   _id: {user.get('_id')}")
        print(f"   Phone: {user.get('phone')}")
        print(f"   District: {user.get('district')}")
        
        # Test lookup by ID
        print(f"\n   Testing find_user_by_id('{user.get('_id')}')...")
        found_user = find_user_by_id(user.get('_id'))
        if found_user:
            print(f"   ✅ SUCCESS: Found {found_user.get('name')}")
        else:
            print(f"   ❌ FAILED: User not found!")
        
        # Test lookup by email
        print(f"\n   Testing find_user_by_email('{email}')...")
        found_by_email = find_user_by_email(email)
        if found_by_email:
            print(f"   ✅ SUCCESS: Found {found_by_email.get('name')}")
        else:
            print(f"   ❌ FAILED: User not found!")

# Check recent listings
print(f"\n\n{'=' * 60}")
print("RECENT LISTINGS CHECK")
print("=" * 60)

listings_file = 'data/crop_listings.json'
if os.path.exists(listings_file):
    with open(listings_file, 'r', encoding='utf-8') as f:
        listings = json.load(f)
    
    # Get today's listings
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    today_listings = [l for l in listings if l.get('created_at', '').startswith(today)]
    print(f"\n📦 Listings created today ({today}): {len(today_listings)}")
    
    for listing in today_listings:
        print(f"\n   Crop: {listing.get('crop')}")
        print(f"   Farmer ID: {listing.get('farmer_id')}")
        print(f"   Farmer Name: {listing.get('farmer_name')}")
        print(f"   Farmer Phone: {listing.get('farmer_phone')}")
        print(f"   Created: {listing.get('created_at')}")
        
        # Check if farmer exists
        farmer_id = listing.get('farmer_id')
        if farmer_id:
            farmer = find_user_by_id(farmer_id)
            if farmer:
                print(f"   ✅ Farmer exists: {farmer.get('name')}")
            else:
                print(f"   ❌ Farmer NOT found in database!")

print("\n" + "=" * 60)
