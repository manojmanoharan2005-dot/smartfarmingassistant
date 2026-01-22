"""
Check marketplace listings for issues
"""
import json
from datetime import datetime

# Check crop listings
print("=" * 60)
print("CHECKING CROP MARKETPLACE LISTINGS")
print("=" * 60)

with open('data/crop_listings.json', 'r', encoding='utf-8') as f:
    listings = json.load(f)

# Get available listings
available = [l for l in listings if l.get('status') == 'available']

print(f"\nTotal available listings: {len(available)}\n")

user_id = "cb57cdef-86cf-4079-9d30-372067f41777"  # manoj kumar

for listing in available:
    farmer_id = listing.get('farmer_id')
    farmer_name = listing.get('farmer_name', 'Unknown')
    is_own = (farmer_id == user_id)
    
    print(f"Crop: {listing.get('crop')}")
    print(f"  ID: {listing.get('_id')}")
    print(f"  Farmer: {farmer_name} ({farmer_id[:8] if farmer_id else 'None'}...)")
    print(f"  Own Listing: {'YES' if is_own else 'NO'}")
    print(f"  Status: {listing.get('status')}")
    print(f"  Created: {listing.get('created_at', '')[:10]}")
    
    # Check if farmer exists
    if farmer_name == 'Unknown' or not farmer_name:
        print(f"  ⚠️ WARNING: Farmer name is Unknown!")
    
    print()

# Also check for old cancelled/sold listings that might be showing
print("\n" + "=" * 60)
print("NON-AVAILABLE LISTINGS (should not show in marketplace)")
print("=" * 60)

non_available = [l for l in listings if l.get('status') != 'available']
print(f"\nTotal: {len(non_available)}")
for listing in non_available:
    print(f"  {listing.get('crop')} - Status: {listing.get('status')} - Created: {listing.get('created_at', '')[:10]}")
