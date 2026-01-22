"""
Fix the Brinjal listing with orphaned farmer_id
"""
import json

# Read listings
with open('data/crop_listings.json', 'r', encoding='utf-8') as f:
    listings = json.load(f)

# Manoj kumar's ID
manoj_id = "cb57cdef-86cf-4079-9d30-372067f41777"

# Fix the Brinjal listing
fixed_count = 0
for listing in listings:
    if listing.get('_id') == '5b1737b0-f853-476b-bd66-c2a6b988219b':
        old_farmer_id = listing.get('farmer_id')
        listing['farmer_id'] = manoj_id
        listing['farmer_name'] = 'manoj kumar'
        listing['farmer_phone'] = '6382801974'
        print(f"Fixed Brinjal listing:")
        print(f"  Old farmer_id: {old_farmer_id}")
        print(f"  New farmer_id: {manoj_id}")
        print(f"  Farmer name: manoj kumar")
        fixed_count += 1

# Save back
with open('data/crop_listings.json', 'w', encoding='utf-8') as f:
    json.dump(listings, f, indent=2, ensure_ascii=False)

print(f"\nFixed {fixed_count} listing(s)")
