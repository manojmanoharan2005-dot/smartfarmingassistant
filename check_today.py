"""
Check all listings created today
"""
import json

with open('data/crop_listings.json', 'r', encoding='utf-8') as f:
    listings = json.load(f)

today_listings = [l for l in listings if '2026-01-22' in l.get('created_at', '')]

print(f"Total listings created today: {len(today_listings)}\n")

for listing in today_listings:
    print(f"Crop: {listing.get('crop')}")
    print(f"  Farmer: {listing.get('farmer_name')}")
    print(f"  Farmer ID: {listing.get('farmer_id')}")
    print(f"  Status: {listing.get('status')}")
    print(f"  Created: {listing.get('created_at')[:19]}")
    print()
