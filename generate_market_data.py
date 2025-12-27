import json
import random
from datetime import datetime, timedelta

# Load states and districts
with open('states_districts.json', 'r') as f:
    states_districts = json.load(f)

# Define commodities with realistic price ranges (per quintal in INR)
VEGETABLES = {
    "Potato": {"min": 800, "max": 2000, "varieties": ["Local", "Hybrid", "Imported"]},
    "Tomato": {"min": 1000, "max": 4000, "varieties": ["Local", "Hybrid", "Cherry"]},
    "Onion": {"min": 1200, "max": 3500, "varieties": ["Red", "White", "Pink"]},
    "Carrot": {"min": 1500, "max": 3000, "varieties": ["Local", "Hybrid", "Ooty"]},
    "Cabbage": {"min": 800, "max": 2000, "varieties": ["Green", "Red", "Grade A"]},
    "Cauliflower": {"min": 1000, "max": 2500, "varieties": ["Local", "Grade A", "Premium"]},
    "Spinach": {"min": 1000, "max": 2500, "varieties": ["Local", "Organic", "Premium"]},
    "Brinjal (Eggplant)": {"min": 1200, "max": 3000, "varieties": ["Long", "Round", "Green"]},
    "Lady's Finger (Okra)": {"min": 1500, "max": 3500, "varieties": ["Local", "Hybrid", "Premium"]},
    "Beetroot": {"min": 1200, "max": 2800, "varieties": ["Local", "Organic", "Grade A"]},
    "Radish": {"min": 800, "max": 2000, "varieties": ["White", "Red", "Local"]},
    "Capsicum": {"min": 2000, "max": 5000, "varieties": ["Green", "Red", "Yellow"]},
    "Pumpkin": {"min": 600, "max": 1500, "varieties": ["Local", "Sweet", "Yellow"]},
    "Bottle Gourd": {"min": 800, "max": 2000, "varieties": ["Local", "Long", "Round"]},
    "Bitter Gourd": {"min": 1500, "max": 3500, "varieties": ["Local", "Green", "White"]},
    "Ridge Gourd": {"min": 1200, "max": 2800, "varieties": ["Local", "Long", "Short"]},
    "Green Peas": {"min": 3000, "max": 6000, "varieties": ["Local", "Frozen", "Premium"]},
    "Beans": {"min": 2000, "max": 4500, "varieties": ["French", "Cluster", "Local"]},
    "Mushroom": {"min": 8000, "max": 15000, "varieties": ["Button", "Oyster", "Shiitake"]},
    "Corn": {"min": 1500, "max": 3000, "varieties": ["Sweet", "Baby", "Local"]}
}

FRUITS = {
    "Apple": {"min": 5000, "max": 12000, "varieties": ["Shimla", "Kashmiri", "Imported"]},
    "Banana": {"min": 1500, "max": 3500, "varieties": ["Robusta", "Yelakki", "Nendran"]},
    "Mango": {"min": 3000, "max": 10000, "varieties": ["Alphonso", "Kesar", "Langra"]},
    "Orange": {"min": 2500, "max": 5000, "varieties": ["Nagpur", "Kinnow", "Mandarin"]},
    "Grapes": {"min": 4000, "max": 10000, "varieties": ["Green", "Black", "Red"]},
    "Papaya": {"min": 1500, "max": 3500, "varieties": ["Local", "Taiwan", "Hybrid"]},
    "Pineapple": {"min": 2000, "max": 4500, "varieties": ["Queen", "Giant Kew", "Mauritius"]},
    "Guava": {"min": 2000, "max": 4000, "varieties": ["Allahabad", "Pink", "White"]},
    "Watermelon": {"min": 800, "max": 2000, "varieties": ["Striped", "Black", "Seedless"]},
    "Muskmelon": {"min": 1500, "max": 3500, "varieties": ["Local", "Netted", "Honeydew"]},
    "Pomegranate": {"min": 5000, "max": 12000, "varieties": ["Bhagwa", "Arakta", "Ganesh"]},
    "Strawberry": {"min": 10000, "max": 25000, "varieties": ["Camarosa", "Chandler", "Local"]},
    "Cherry": {"min": 15000, "max": 35000, "varieties": ["Kashmiri", "Imported", "Bing"]},
    "Kiwi": {"min": 12000, "max": 25000, "varieties": ["Green", "Golden", "Imported"]},
    "Lemon": {"min": 2000, "max": 5000, "varieties": ["Kagzi", "Galgal", "Sweet"]},
    "Pear": {"min": 4000, "max": 8000, "varieties": ["Kashmir", "Chinese", "Bartlett"]},
    "Peach": {"min": 5000, "max": 10000, "varieties": ["Local", "Imported", "Yellow"]},
    "Plum": {"min": 4000, "max": 9000, "varieties": ["Black", "Red", "Yellow"]},
    "Coconut": {"min": 1500, "max": 3500, "varieties": ["Tender", "Dry", "Hybrid"]},
    "Custard Apple": {"min": 3000, "max": 7000, "varieties": ["Local", "Balanagar", "Arka Sahan"]}
}

def generate_price_entry(commodity, info, state, district):
    """Generate a single price entry for a commodity in a district"""
    base_min = info["min"]
    base_max = info["max"]
    
    # Add some regional variation (±20%)
    regional_factor = random.uniform(0.8, 1.2)
    
    min_price = int(base_min * regional_factor * random.uniform(0.9, 1.0))
    max_price = int(base_max * regional_factor * random.uniform(1.0, 1.1))
    modal_price = int((min_price + max_price) / 2 * random.uniform(0.95, 1.05))
    
    # Random date within last 7 days
    days_ago = random.randint(0, 6)
    price_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    
    # Random arrival quantity
    arrival = f"{random.randint(50, 1000)} quintals"
    
    return {
        "commodity": commodity,
        "variety": random.choice(info["varieties"]),
        "market": f"{district} Mandi",
        "state": state,
        "district": district,
        "min_price": min_price,
        "max_price": max_price,
        "modal_price": modal_price,
        "price_date": price_date,
        "arrival": arrival,
        "unit": "Quintal"
    }

def main():
    all_commodities = {**VEGETABLES, **FRUITS}
    market_data = []
    
    print(f"Generating market data for {len(states_districts)} states...")
    print(f"Total commodities: {len(all_commodities)}")
    
    total_districts = 0
    for state, districts in states_districts.items():
        total_districts += len(districts)
        for district in districts:
            for commodity, info in all_commodities.items():
                entry = generate_price_entry(commodity, info, state, district)
                market_data.append(entry)
    
    print(f"Total districts: {total_districts}")
    print(f"Total entries generated: {len(market_data)}")
    
    # Create the final JSON structure
    output = {
        "last_updated": datetime.now().isoformat(),
        "data": market_data
    }
    
    # Save to file
    with open('data/market_prices.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Market data saved to data/market_prices.json")
    print(f"File contains {len(market_data)} entries for all states and districts")

if __name__ == "__main__":
    main()
