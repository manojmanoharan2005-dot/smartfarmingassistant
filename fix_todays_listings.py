"""
Fix orphaned listings created today to use the correct user ID
"""
import json
import os
from datetime import datetime

# File paths
users_file = 'data/users.json'
listings_file = 'data/crop_listings.json'

print("=" * 60)
print("FIXING TODAY'S ORPHANED LISTINGS")
print("=" * 60)

# Get the valid user
with open(users_file, 'r', encoding='utf-8') as f:
    users = json.load(f)

# Should be manoj kumar
valid_user_email = list(users.keys())[0]
valid_user = users[valid_user_email]
valid_user_id = valid_user['_id']
valid_user_name = valid_user['name']
valid_user_phone = valid_user['phone']

print(f"\n✅ Valid user found:")
print(f"   Name: {valid_user_name}")
print(f"   ID: {valid_user_id}")
print(f"   Phone: {valid_user_phone}")

# Load listings
with open(listings_file, 'r', encoding='utf-8') as f:
    listings = json.load(f)

# Find today's listings
today = datetime.now().strftime('%Y-%m-%d')
updated_count = 0

print(f"\n🔍 Looking for listings created today ({today})...")

for listing in listings:
    created_date = listing.get('created_at', '')[:10]
    # Fix any listing created today that has wrong farmer info
    if created_date == today and (listing.get('farmer_id') != valid_user_id or listing.get('farmer_name') == 'Unknown'):
        old_farmer_id = listing.get('farmer_id')
        old_farmer_name = listing.get('farmer_name')
        
        # Update with correct details
        listing['farmer_id'] = valid_user_id
        listing['farmer_name'] = valid_user_name
        listing['farmer_phone'] = valid_user_phone
        
        print(f"\n   ✅ Fixed: {listing.get('crop')} (Status: {listing.get('status')})")
        print(f"      Old ID: {old_farmer_id}")
        print(f"      New ID: {valid_user_id}")
        print(f"      Farmer: {old_farmer_name} → {valid_user_name}")
        
        updated_count += 1

# Save back
if updated_count > 0:
    with open(listings_file, 'w', encoding='utf-8') as f:
        json.dump(listings, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 60}")
    print(f"✅ Updated {updated_count} listing(s)")
    print(f"{'=' * 60}")
else:
    print(f"\nℹ️  No listings to update")
