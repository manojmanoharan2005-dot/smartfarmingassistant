"""
Generate comprehensive market price data for all states and districts in India
Creates 10,000+ records covering all major commodities across all regions
"""
import json
import random
from datetime import datetime, timedelta

# Load states and districts
with open('states_districts.json', 'r', encoding='utf-8') as f:
    states_districts = json.load(f)

# Common commodities traded in mandis across India
VEGETABLES = [
    "Potato", "Tomato", "Onion", "Carrot", "Cabbage", "Cauliflower",
    "Spinach", "Brinjal (Eggplant)", "Lady's Finger (Okra)", "Beetroot",
    "Radish", "Capsicum", "Pumpkin", "Bottle Gourd", "Bitter Gourd",
    "Ridge Gourd", "Green Peas", "Beans", "Mushroom", "Corn"
]

FRUITS = [
    "Apple", "Banana", "Mango", "Orange", "Grapes", "Papaya",
    "Pineapple", "Guava", "Watermelon", "Muskmelon", "Pomegranate",
    "Strawberry", "Cherry", "Kiwi", "Lemon", "Pear", "Peach",
    "Plum", "Coconut", "Custard Apple"
]

# Combine all commodities
COMMODITIES = VEGETABLES + FRUITS

# Real market names for each district (especially Tamil Nadu and major cities)
DISTRICT_MARKETS = {
    # Tamil Nadu - Real market names
    "Ariyalur": ["Ariyalur Market Committee"],
    "Chengalpattu": ["Chengalpattu Vegetable Market", "Maraimalai Nagar Market"],
    "Chennai": ["Koyambedu Wholesale Market", "Kothawalchavadi Market", "Madhavaram Market", "Thiruvanmiyur Market"],
    "Coimbatore": ["Coimbatore Town Hall Market", "Uppilipalayam Market", "Gandhipuram Market", "Mettupalayam Market"],
    "Cuddalore": ["Cuddalore Main Market", "Virudhachalam Market"],
    "Dharmapuri": ["Dharmapuri Regulated Market", "Palacode Market"],
    "Dindigul": ["Oddanchatram Market", "Oddanchatram Vegetable Market", "Palani Market"],
    "Erode": ["Erode Regulated Market", "Gobichettipalayam Market", "Perundurai Market", "Bhavani Market"],
    "Kallakurichi": ["Kallakurichi Agricultural Market"],
    "Kanchipuram": ["Kanchipuram Vegetable Market", "Chengalpattu Market"],
    "Kanyakumari": ["Nagercoil Vegetable Market", "Marthandam Market"],
    "Karur": ["Karur Main Market", "Kulithalai Market"],
    "Krishnagiri": ["Krishnagiri Regulated Market", "Hosur Market"],
    "Madurai": ["Madurai Mattuthavani Market", "Paravai Market", "Anna Nagar Market"],
    "Mayiladuthurai": ["Mayiladuthurai Market"],
    "Nagapattinam": ["Nagapattinam Market", "Karaikal Market"],
    "Namakkal": ["Namakkal Market", "Tiruchengode Market"],
    "Nilgiris": ["Ooty Vegetable Market", "Coonoor Market"],
    "Perambalur": ["Perambalur Market"],
    "Pudukkottai": ["Pudukkottai Market"],
    "Ramanathapuram": ["Ramanathapuram Market", "Paramakudi Market"],
    "Ranipet": ["Ranipet Market", "Arcot Market"],
    "Salem": ["Salem Main Market", "Omalur Market", "Mettur Market"],
    "Sivaganga": ["Sivaganga Market", "Karaikudi Market"],
    "Tenkasi": ["Tenkasi Market", "Sankarankovil Market"],
    "Thanjavur": ["Thanjavur Market", "Kumbakonam Market"],
    "Theni": ["Theni Market", "Periyakulam Market", "Uthamapalayam Market"],
    "Thoothukudi": ["Thoothukudi (Tuticorin) Market"],
    "Tiruchirappalli": ["Trichy Gandhi Market", "Srirangam Market", "Lalgudi Market"],
    "Tirunelveli": ["Tirunelveli Palayamkottai Market", "Thisayanvilai Market"],
    "Tirupathur": ["Tirupathur Market", "Ambur Market"],
    "Tiruppur": ["Tiruppur Market", "Avinashi Market"],
    "Tiruvallur": ["Tiruvallur Market", "Poonamallee Market"],
    "Tiruvannamalai": ["Tiruvannamalai Market", "Arani Market"],
    "Tiruvarur": ["Tiruvarur Market", "Mannargudi Market"],
    "Vellore": ["Vellore Market", "Katpadi Market"],
    "Viluppuram": ["Viluppuram Market", "Tindivanam Market"],
    "Virudhunagar": ["Virudhunagar Market", "Sivakasi Market", "Srivilliputtur Market"],
}

def get_market_name(district, state):
    """Get real market name for the district"""
    # Check if we have specific markets for this district
    if district in DISTRICT_MARKETS:
        return random.choice(DISTRICT_MARKETS[district])
    
    # Tamil Nadu uses specific naming patterns
    if state == "Tamil Nadu":
        market_types = [
            f"{district} Regulated Market",
            f"{district} Uzhavar Sandhai",
            f"{district} Agricultural Market"
        ]
    # Most states use these patterns
    else:
        market_types = [
            f"{district} APMC Yard",
            f"{district} Mandi",
            f"{district} Krishi Upaj Mandi",
            f"{district} Agricultural Market"
        ]
    
    return random.choice(market_types)

def generate_price(commodity):
    """Generate realistic price based on commodity type"""
    # Base prices per quintal for vegetables and fruits
    # All prices are for per quintal (100 kg)
    
    # Vegetables - typically ₹1000-3500 per quintal (₹10-35 per kg)
    vegetable_prices = {
        "Potato": (1200, 2000),
        "Tomato": (1500, 3500),
        "Onion": (1800, 3200),
        "Carrot": (1600, 2800),
        "Cabbage": (1000, 2200),
        "Cauliflower": (1500, 3000),
        "Spinach": (800, 1800),
        "Brinjal (Eggplant)": (1200, 2500),
        "Lady's Finger (Okra)": (2000, 4000),
        "Beetroot": (1500, 2800),
        "Radish": (1000, 2000),
        "Capsicum": (2500, 5000),
        "Pumpkin": (800, 1600),
        "Bottle Gourd": (1000, 2200),
        "Bitter Gourd": (2000, 3800),
        "Ridge Gourd": (1500, 3000),
        "Green Peas": (2500, 4500),
        "Beans": (2000, 3500),
        "Mushroom": (8000, 15000),
        "Corn": (1200, 2500)
    }
    
    # Fruits - typically ₹2000-8000 per quintal (₹20-80 per kg)
    fruit_prices = {
        "Apple": (8000, 15000),
        "Banana": (2000, 4000),
        "Mango": (3500, 8000),
        "Orange": (3000, 6000),
        "Grapes": (4000, 10000),
        "Papaya": (1500, 3500),
        "Pineapple": (2500, 5000),
        "Guava": (2000, 4500),
        "Watermelon": (1000, 2500),
        "Muskmelon": (1500, 3500),
        "Pomegranate": (5000, 12000),
        "Strawberry": (15000, 30000),
        "Cherry": (20000, 40000),
        "Kiwi": (12000, 25000),
        "Lemon": (2500, 5000),
        "Pear": (6000, 12000),
        "Peach": (8000, 15000),
        "Plum": (10000, 18000),
        "Coconut": (3000, 6000),
        "Custard Apple": (4000, 8000)
    }
    
    # Get price range for the commodity
    if commodity in vegetable_prices:
        min_base, max_base = vegetable_prices[commodity]
    elif commodity in fruit_prices:
        min_base, max_base = fruit_prices[commodity]
    else:
        min_base, max_base = (1500, 3500)  # Default
    
    # Generate modal price
    modal_price = random.randint(min_base, max_base)
    
    # Generate min and max prices (±15% variation)
    variation = int(modal_price * 0.15)
    min_price = modal_price - random.randint(0, variation)
    max_price = modal_price + random.randint(0, variation)
    
    return min_price, max_price, modal_price

def generate_market_records():
    """Generate comprehensive market data for all India"""
    records = []
    
    print(f"Generating ALL 40 commodities for each district in each state\n")
    
    # Generate data for each state
    for state, districts in states_districts.items():
        print(f"Generating data for {state}...")
        
        state_records = 0
        
        # For each district in the state
        for district in districts:
            # Generate authentic market name for this district
            mandi_name = get_market_name(district, state)
            
            # Generate price records for ALL 40 commodities (20 veg + 20 fruits)
            for commodity in COMMODITIES:
                min_price, max_price, modal_price = generate_price(commodity)
                
                # Generate arrival quantity (in quintals)
                arrival_qty = random.randint(50, 1000)
                
                # Random date within last 7 days
                days_ago = random.randint(0, 7)
                price_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                
                record = {
                    "commodity": commodity,
                    "variety": random.choice(["Grade A", "Grade B", "Local", "Hybrid", "Premium"]),
                    "market": mandi_name,
                    "state": state,
                    "district": district,
                    "min_price": min_price,
                    "max_price": max_price,
                    "modal_price": modal_price,
                    "price_date": price_date,
                    "arrival": f"{arrival_qty} quintals",
                    "unit": "Quintal"
                }
                
                records.append(record)
                state_records += 1
        
        print(f"   ✓ Generated {state_records} records for {state} ({len(districts)} districts × 40 commodities)")
    
    return records

# Generate the data
print("🌾 Starting market data generation...")
print(f"📊 Generating: 40 commodities (20 vegetables + 20 fruits)")
print(f"🗺️ Coverage: All {len(states_districts)} states and ALL districts")
print(f"💡 Each district will have prices for all 40 items")
print()

market_data = generate_market_records()

# Create the final data structure
output = {
    "last_updated": datetime.now().isoformat(),
    "data": market_data
}

# Save to file
output_file = 'data/market_prices.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ Successfully generated {len(market_data)} market price records!")
print(f"📁 Saved to: {output_file}")
print(f"📊 File size: {len(json.dumps(output)) / 1024 / 1024:.2f} MB")

# Print statistics
states_covered = len(set(record['state'] for record in market_data))
districts_covered = len(set(f"{record['state']}-{record['district']}" for record in market_data))
commodities_covered = len(set(record['commodity'] for record in market_data))

print(f"\n📈 Coverage Statistics:")
print(f"   States covered: {states_covered}")
print(f"   Districts covered: {districts_covered}")
print(f"   Unique commodities: {commodities_covered}")
print(f"   Total records: {len(market_data)}")
print(f"   Records per district: {len(market_data) // districts_covered if districts_covered > 0 else 0}")
print(f"\n✨ Market data generation complete!")
print(f"🎯 Every district now has all 40 vegetables and fruits!")
