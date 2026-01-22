"""
Clean up orphaned listings
Deletes all listings where the farmer/owner no longer exists
"""
import json
import os

# File paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
CROP_LISTINGS_FILE = os.path.join(DATA_DIR, 'crop_listings.json')
EQUIPMENT_LISTINGS_FILE = os.path.join(DATA_DIR, 'equipment_listings.json')

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def cleanup_orphaned_listings():
    print("=" * 60)
    print("ORPHANED LISTING CLEANUP")
    print("=" * 60)
    
    # Load users to get valid user IDs
    users_dict = load_json(USERS_FILE)
    if not users_dict:
        print("❌ No users found!")
        return
    
    valid_user_ids = set()
    for email, user in users_dict.items():
        user_id = user.get('_id')
        if user_id:
            valid_user_ids.add(user_id)
    
    print(f"\n📋 Valid users: {len(valid_user_ids)}")
    for user_id in valid_user_ids:
        for email, user in users_dict.items():
            if user.get('_id') == user_id:
                print(f"   - {user.get('name')} ({user_id[:8]}...)")
    
    # Clean crop listings
    print(f"\n🌾 Cleaning Crop Listings...")
    crop_listings = load_json(CROP_LISTINGS_FILE)
    if crop_listings:
        original_count = len(crop_listings)
        
        # Keep only listings with valid farmer IDs OR those already sold/cancelled
        cleaned_listings = []
        deleted_count = 0
        
        for listing in crop_listings:
            farmer_id = listing.get('farmer_id')
            status = listing.get('status', '')
            
            # Keep if farmer exists OR if already sold (historical record)
            if farmer_id in valid_user_ids or status == 'sold':
                cleaned_listings.append(listing)
            else:
                print(f"   🗑️  Deleting: {listing.get('crop')} - {listing.get('_id')[:8]}... (Farmer {farmer_id[:8] if farmer_id else 'None'}... not found, status: {status})")
                deleted_count += 1
        
        if deleted_count > 0:
            save_json(CROP_LISTINGS_FILE, cleaned_listings)
            print(f"\n   ✅ Deleted {deleted_count} orphaned crop listing(s)")
            print(f"   ✅ Kept {len(cleaned_listings)} valid listing(s)")
        else:
            print(f"   ℹ️  No orphaned crop listings to delete")
    
    # Clean equipment listings
    print(f"\n🚜 Cleaning Equipment Listings...")
    equipment_listings = load_json(EQUIPMENT_LISTINGS_FILE)
    if equipment_listings:
        original_count = len(equipment_listings)
        
        # Keep only listings with valid owner IDs OR those already booked/completed
        cleaned_listings = []
        deleted_count = 0
        
        for listing in equipment_listings:
            owner_id = listing.get('owner_id')
            status = listing.get('status', '')
            
            # Keep if owner exists OR if already booked/completed (historical record)
            if owner_id in valid_user_ids or status in ['booked', 'completed']:
                cleaned_listings.append(listing)
            else:
                print(f"   🗑️  Deleting: {listing.get('equipment_name')} - {listing.get('_id')[:8]}... (Owner {owner_id[:8] if owner_id else 'None'}... not found, status: {status})")
                deleted_count += 1
        
        if deleted_count > 0:
            save_json(EQUIPMENT_LISTINGS_FILE, cleaned_listings)
            print(f"\n   ✅ Deleted {deleted_count} orphaned equipment listing(s)")
            print(f"   ✅ Kept {len(cleaned_listings)} valid listing(s)")
        else:
            print(f"   ℹ️  No orphaned equipment listings to delete")
    
    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE!")
    print("=" * 60)

if __name__ == '__main__':
    print("\n⚠️  WARNING: This will permanently delete orphaned listings!")
    print("   (Listings where the farmer/owner no longer exists)")
    print("   Sold/booked listings will be kept for historical records.")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        cleanup_orphaned_listings()
    else:
        print("\n❌ Cleanup cancelled.")
