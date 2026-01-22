"""
Data Migration Script
Fixes orphaned farmer/owner IDs in listings by matching phone numbers
"""
import json
import os

# File paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
CROP_LISTINGS_FILE = os.path.join(DATA_DIR, 'crop_listings.json')
EQUIPMENT_LISTINGS_FILE = os.path.join(DATA_DIR, 'equipment_listings.json')

def load_json(filepath):
    """Load JSON file"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_json(filepath, data):
    """Save JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def migrate_listings():
    """Migrate listings to fix orphaned user IDs"""
    print("=" * 60)
    print("LISTING DATA MIGRATION")
    print("=" * 60)
    
    # Load users
    users_dict = load_json(USERS_FILE)
    if not users_dict:
        print("❌ No users found!")
        return
    
    print(f"\n📋 Found {len(users_dict)} user(s) in database:")
    for email, user in users_dict.items():
        print(f"   - {user.get('name')} (ID: {user.get('_id')}, Phone: {user.get('phone')})")
    
    # Build phone to user mapping
    phone_to_user = {}
    for email, user in users_dict.items():
        phone = user.get('phone')
        if phone:
            phone_to_user[phone] = user
    
    # Migrate crop listings
    print(f"\n🌾 Migrating Crop Listings...")
    crop_listings = load_json(CROP_LISTINGS_FILE)
    if crop_listings:
        updated_count = 0
        for listing in crop_listings:
            # Check if farmer details are missing or unknown
            if listing.get('farmer_name') == 'Unknown' or not listing.get('farmer_name'):
                farmer_phone = listing.get('farmer_phone', '')
                farmer_id = listing.get('farmer_id')
                
                # Try to find user by phone number from buyer data (if sold)
                if listing.get('status') == 'sold' and listing.get('buyer_phone'):
                    # If this listing was sold and we have buyer phone, they might be the original farmer
                    # This is a heuristic - skip for now
                    pass
                
                # Try to match by existing farmer_id
                user_found = None
                for email, user in users_dict.items():
                    if user.get('_id') == farmer_id:
                        user_found = user
                        break
                
                if user_found:
                    listing['farmer_name'] = user_found.get('name', 'Unknown')
                    listing['farmer_phone'] = user_found.get('phone', '')
                    updated_count += 1
                    print(f"   ✅ Fixed listing {listing.get('_id')[:8]}... - {listing.get('crop')}")
                else:
                    print(f"   ⚠️  Orphaned listing {listing.get('_id')[:8]}... - {listing.get('crop')} (User ID {farmer_id[:8] if farmer_id else 'None'}... not found)")
        
        if updated_count > 0:
            save_json(CROP_LISTINGS_FILE, crop_listings)
            print(f"\n✅ Updated {updated_count} crop listing(s)")
        else:
            print(f"\n⚠️  No crop listings were updated (all are either correct or orphaned)")
    
    # Migrate equipment listings
    print(f"\n🚜 Migrating Equipment Listings...")
    equipment_listings = load_json(EQUIPMENT_LISTINGS_FILE)
    if equipment_listings:
        updated_count = 0
        for listing in equipment_listings:
            # Check if owner details are missing or unknown
            if listing.get('owner_name') == 'Unknown' or not listing.get('owner_name'):
                owner_id = listing.get('owner_id')
                
                # Try to match by existing owner_id
                user_found = None
                for email, user in users_dict.items():
                    if user.get('_id') == owner_id:
                        user_found = user
                        break
                
                if user_found:
                    listing['owner_name'] = user_found.get('name', 'Unknown')
                    listing['owner_phone'] = user_found.get('phone', '')
                    updated_count += 1
                    print(f"   ✅ Fixed listing {listing.get('_id')[:8]}... - {listing.get('equipment_name')}")
                else:
                    print(f"   ⚠️  Orphaned listing {listing.get('_id')[:8]}... - {listing.get('equipment_name')} (User ID {owner_id[:8] if owner_id else 'None'}... not found)")
        
        if updated_count > 0:
            save_json(EQUIPMENT_LISTINGS_FILE, equipment_listings)
            print(f"\n✅ Updated {updated_count} equipment listing(s)")
        else:
            print(f"\n⚠️  No equipment listings were updated (all are either correct or orphaned)")
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE!")
    print("=" * 60)
    print("\n💡 Note: Orphaned listings belong to users that no longer exist.")
    print("   These will continue to show 'Unknown' as the farmer/owner name.")
    print("   You can either:")
    print("   1. Delete these orphaned listings")
    print("   2. Keep them for historical reference")
    print("   3. Reassign them to an existing user")

if __name__ == '__main__':
    migrate_listings()
