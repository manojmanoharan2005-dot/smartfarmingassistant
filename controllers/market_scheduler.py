from flask import Blueprint
import google.generativeai as genai
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json
import os
import random

scheduler_bp = Blueprint('scheduler', __name__)

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY_HERE')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Market price data file
MARKET_DATA_FILE = 'data/market_prices.json'

# All Indian states
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
]

# Crops by region (including vegetables and fruits)
CROPS_BY_REGION = {
    "North": ["Wheat", "Rice", "Potato", "Onion", "Tomato", "Cauliflower", "Cabbage", "Carrot", "Apple", "Mango", "Banana", "Sugarcane", "Mustard", "Cotton"],
    "South": ["Rice", "Coconut", "Banana", "Mango", "Papaya", "Tomato", "Brinjal", "Okra", "Drumstick", "Curry Leaves", "Groundnut", "Turmeric", "Coffee"],
    "East": ["Rice", "Potato", "Tomato", "Cabbage", "Cauliflower", "Brinjal", "Pumpkin", "Banana", "Papaya", "Litchi", "Tea", "Jute", "Mustard"],
    "West": ["Cotton", "Groundnut", "Onion", "Tomato", "Grapes", "Banana", "Mango", "Pomegranate", "Potato", "Brinjal", "Okra", "Sugarcane", "Wheat"],
    "Central": ["Wheat", "Soybean", "Potato", "Onion", "Tomato", "Brinjal", "Okra", "Mango", "Banana", "Orange", "Cotton", "Pulses", "Rice"]
}

# Major markets by state (5 main cities per state)
MARKETS_BY_STATE = {
    "Andhra Pradesh": ["Visakhapatnam - Maddilapalem", "Vijayawada - Rytu Bazaar", "Guntur - Rythu Bazaar", "Tirupati - Market", "Nellore - Vegetable Market"],
    "Bihar": ["Patna - Sabji Bagh", "Gaya - Rythu Bazaar", "Bhagalpur - Mandi", "Muzaffarpur - Market", "Darbhanga - Vegetable Market"],
    "Chhattisgarh": ["Raipur - Mandi", "Bhilai - Market", "Bilaspur - APMC", "Korba - Vegetable Market", "Durg - Market Yard"],
    "Gujarat": ["Ahmedabad - Khodiyar Market", "Surat - Kamela Darwaja", "Vadodara - Market Yard", "Rajkot - APMC Market", "Bhavnagar - Vegetable Market"],
    "Haryana": ["Faridabad - Mandi", "Gurugram - Market", "Panipat - Grain Market", "Ambala - Vegetable Market", "Karnal - Market Yard"],
    "Himachal Pradesh": ["Shimla - Sabzi Mandi", "Mandi - Fruit Market", "Solan - Market", "Kullu - Valley Market", "Dharamshala - Bazaar"],
    "Karnataka": ["Bangalore - KR Market", "Mysore - Devaraja Market", "Hubli - APMC Market", "Mangalore - Market Yard", "Belgaum - Vegetable Market"],
    "Kerala": ["Kochi - Market", "Thiruvananthapuram - Chalai", "Kozhikode - Mittayi Theruvu", "Thrissur - Market", "Kollam - Vegetable Market"],
    "Madhya Pradesh": ["Indore - Grain Market", "Bhopal - Mandi", "Jabalpur - Market Yard", "Gwalior - Vegetable Market", "Ujjain - Market"],
    "Maharashtra": ["Mumbai - Crawford Market", "Pune - Market Yard", "Nashik - APMC Market", "Nagpur - Vegetable Market", "Aurangabad - Market"],
    "Odisha": ["Bhubaneswar - Bapuji Nagar", "Cuttack - Choudwar", "Rourkela - Market", "Berhampur - Vegetable Market", "Sambalpur - Mandi"],
    "Punjab": ["Ludhiana - Grain Market", "Amritsar - Mandi", "Jalandhar - Market Yard", "Patiala - Vegetable Market", "Bathinda - Market"],
    "Rajasthan": ["Jaipur - Grain Market", "Jodhpur - Mandi", "Kota - Market Yard", "Udaipur - Vegetable Market", "Ajmer - Market"],
    "Tamil Nadu": ["Chennai - Koyambedu", "Coimbatore - Nethaji Market", "Madurai - Mattuthavani", "Salem - Market Yard", "Tiruchirappalli - Vegetable Market"],
    "Telangana": ["Hyderabad - Rythu Bazaar", "Warangal - Market", "Nizamabad - Grain Market", "Karimnagar - Vegetable Market", "Khammam - Market Yard"],
    "Uttar Pradesh": ["Lucknow - Yahiyaganj", "Kanpur - Mandi", "Ghaziabad - Market", "Agra - Vegetable Market", "Varanasi - Market Yard"],
    "Uttarakhand": ["Dehradun - Paltan Bazaar", "Haridwar - Mandi", "Haldwani - Market", "Roorkee - Vegetable Market", "Rishikesh - Market"],
    "West Bengal": ["Kolkata - Sealdah", "Howrah - Market", "Durgapur - Haat", "Siliguri - Vegetable Market", "Asansol - Market Yard"],
    "Assam": ["Guwahati - Fancy Bazaar", "Dibrugarh - Market", "Jorhat - Mandi", "Silchar - Vegetable Market", "Tezpur - Market"],
    "Jharkhand": ["Ranchi - Firayalal", "Jamshedpur - Sakchi", "Dhanbad - Market", "Bokaro - Vegetable Market", "Deoghar - Market Yard"],
    "Goa": ["Panaji - Market", "Margao - Municipal Market", "Vasco - Market", "Mapusa - Friday Market", "Ponda - Vegetable Market"],
    "Sikkim": ["Gangtok - Lal Market", "Namchi - Market", "Gyalshing - Bazaar", "Mangan - Market", "Rangpo - Vegetable Market"],
    "Arunachal Pradesh": ["Itanagar - Market", "Naharlagun - Main Market", "Pasighat - Bazaar", "Tawang - Market", "Bomdila - Vegetable Market"],
    "Manipur": ["Imphal - Ima Keithel", "Thoubal - Market", "Bishnupur - Bazaar", "Kakching - Market", "Churachandpur - Vegetable Market"],
    "Meghalaya": ["Shillong - Bara Bazaar", "Tura - Market", "Jowai - Market", "Nongstoin - Haat", "Nongpoh - Vegetable Market"],
    "Mizoram": ["Aizawl - Bara Bazar", "Lunglei - Market", "Champhai - Bazaar", "Serchhip - Market", "Kolasib - Vegetable Market"],
    "Nagaland": ["Kohima - New Market", "Dimapur - Market", "Mokokchung - Bazaar", "Wokha - Market", "Tuensang - Vegetable Market"],
    "Tripura": ["Agartala - Battala", "Udaipur - Market", "Dharmanagar - Bazaar", "Kailashahar - Market", "Ambassa - Vegetable Market"]
}

def get_state_region(state):
    """Determine region for a state"""
    north = ["Punjab", "Haryana", "Himachal Pradesh", "Uttarakhand", "Uttar Pradesh"]
    south = ["Tamil Nadu", "Kerala", "Karnataka", "Andhra Pradesh", "Telangana"]
    east = ["West Bengal", "Odisha", "Bihar", "Jharkhand", "Assam", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Tripura", "Arunachal Pradesh", "Sikkim"]
    west = ["Gujarat", "Maharashtra", "Goa", "Rajasthan"]
    central = ["Madhya Pradesh", "Chhattisgarh"]
    
    if state in north: return "North"
    if state in south: return "South"
    if state in east: return "East"
    if state in west: return "West"
    if state in central: return "Central"
    return "Central"

def generate_realistic_prices_with_ai():
    """Use Gemini AI to generate realistic market prices for all Indian states"""
    try:
        prompt = f"""Generate realistic current agricultural market prices for major Indian states as of {datetime.now().strftime('%Y-%m-%d')}.

Generate data for ALL major Indian states including: Punjab, Haryana, Uttar Pradesh, Bihar, West Bengal, Maharashtra, Gujarat, Karnataka, Tamil Nadu, Andhra Pradesh, Telangana, Madhya Pradesh, Rajasthan, Odisha, Kerala, Chhattisgarh, Assam, Jharkhand, and others.

For each state, include their major crops:
- North: Wheat, Rice, Sugarcane, Mustard, Potato, Onion, Cotton
- South: Rice, Paddy, Coconut, Banana, Groundnut, Turmeric, Coffee
- East: Rice, Jute, Tea, Potato, Maize, Vegetables
- West: Cotton, Groundnut, Sugarcane, Wheat, Bajra, Soybean
- Central: Wheat, Soybean, Cotton, Pulses, Rice

Provide realistic prices in ₹/quintal:
- Modal Price (average market price)
- Minimum Price
- Maximum Price

Format as JSON array. Generate at least 50 records covering all major states. Example:
[{{"commodity":"Wheat","variety":"Sharbati","market":"Ludhiana - Grain Market","state":"Punjab","district":"Ludhiana","min_price":2300,"max_price":2700,"modal_price":2500,"price_date":"{datetime.now().strftime('%Y-%m-%d')}","arrival":"250 quintals","unit":"Quintal"}}]

Keep prices realistic for December 2025."""

        response = model.generate_content(prompt)
        response_text = response.text
        
        # Extract JSON from response
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_text = response_text[start_idx:end_idx]
            market_data = json.loads(json_text)
            print(f"✅ AI generated {len(market_data)} market records for all India")
            return market_data
        else:
            print("Could not extract JSON from AI response, using fallback data")
            return generate_fallback_prices()
            
    except Exception as e:
        print(f"Error generating prices with AI: {str(e)}")
        return generate_fallback_prices()

def generate_fallback_prices():
    """Fallback realistic prices - ALL vegetables and fruits for EACH district"""
    # Base prices (in ₹/quintal)
    base_prices = {
        # Vegetables (₹/quintal) - 20 types
        "Potato": (1200, 2000), "Onion": (1500, 3000), "Tomato": (1000, 2500),
        "Cabbage": (800, 1500), "Cauliflower": (1000, 1800), "Carrot": (1200, 2000),
        "Brinjal": (1500, 2500), "Okra": (2000, 3500), "Pumpkin": (600, 1200),
        "Drumstick": (2500, 4000), "Beans": (1800, 3000), "Green Peas": (2000, 3500),
        "Capsicum": (2500, 4500), "Green Chilli": (3000, 6000), "Cucumber": (800, 1500),
        "Bitter Gourd": (1500, 2500), "Bottle Gourd": (800, 1500), "Ridge Gourd": (1200, 2000),
        "Radish": (800, 1400), "Coriander": (2000, 4000),
        # Fruits (₹/quintal) - 10 types
        "Mango": (3000, 6000), "Banana": (1500, 3000), "Apple": (6000, 10000),
        "Grapes": (4000, 8000), "Papaya": (1000, 2000), "Orange": (2500, 4500),
        "Litchi": (4000, 7000), "Pomegranate": (5000, 9000), "Watermelon": (800, 1500),
        "Guava": (1500, 2500)
    }
    
    # All vegetables and fruits - EVERY district will have ALL of these (30 total)
    all_vegetables = ["Potato", "Onion", "Tomato", "Cabbage", "Cauliflower", "Carrot", "Brinjal", "Okra", "Pumpkin", "Drumstick", 
                     "Beans", "Green Peas", "Capsicum", "Green Chilli", "Cucumber", "Bitter Gourd", "Bottle Gourd", "Ridge Gourd", "Radish", "Coriander"]
    all_fruits = ["Mango", "Banana", "Apple", "Grapes", "Papaya", "Orange", "Litchi", "Pomegranate", "Watermelon", "Guava"]
    all_commodities = all_vegetables + all_fruits
    
    market_data = []
    date_today = datetime.now().strftime('%Y-%m-%d')
    
    # Generate data for all states - EACH DISTRICT gets ALL vegetables and fruits
    for state in INDIAN_STATES:
        markets = MARKETS_BY_STATE.get(state, [f"{state} - Main Market"])
        
        # For each market/district in the state
        for i in range(5):  # 5 markets per state
            market = markets[i] if i < len(markets) else markets[0]
            district = market.split(' - ')[0]
            
            # Generate ALL 30 commodities for this district
            for commodity in all_commodities:
                min_base, max_base = base_prices[commodity]
                min_price = int(min_base * random.uniform(0.90, 1.10))
                max_price = int(max_base * random.uniform(0.90, 1.10))
                modal_price = int((min_price + max_price) / 2)
                
                market_data.append({
                    "commodity": commodity,
                    "variety": "Grade A",
                    "market": market,
                    "state": state,
                    "district": district,
                    "min_price": min_price,
                    "max_price": max_price,
                    "modal_price": modal_price,
                    "price_date": date_today,
                    "arrival": f"{random.randint(50, 800)} quintals",
                    "unit": "Quintal"
                })
    
    print(f"✅ Fallback data: {len(market_data)} records covering ALL vegetables and fruits for all India")
    return market_data

def save_market_data(data):
    """Save market data to JSON file"""
    try:
        os.makedirs('data', exist_ok=True)
        with open(MARKET_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'last_updated': datetime.now().isoformat(),
                'data': data
            }, f, indent=2, ensure_ascii=False)
        print(f"✅ Market data saved: {len(data)} records")
        return True
    except Exception as e:
        print(f"Error saving market data: {str(e)}")
        return False

def load_market_data():
    """Load market data from JSON file"""
    try:
        if os.path.exists(MARKET_DATA_FILE):
            with open(MARKET_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('data', []), data.get('last_updated')
        return [], None
    except Exception as e:
        print(f"Error loading market data: {str(e)}")
        return [], None

def update_market_prices_job():
    """Background job to update market prices daily"""
    print(f"🔄 Running daily market price update for ALL INDIA at {datetime.now()}")
    try:
        # Use fallback method for reliable all-India coverage
        new_prices = generate_fallback_prices()
        if new_prices:
            save_market_data(new_prices)
            print(f"✅ All India prices updated! Total: {len(new_prices)} records for {len(INDIAN_STATES)} states")
    except Exception as e:
        print(f"❌ Error in update job: {str(e)}")

def init_scheduler(app):
    """Initialize scheduler for daily updates at 9:00 AM"""
    scheduler = BackgroundScheduler()
    
    scheduler.add_job(
        func=update_market_prices_job,
        trigger='cron',
        hour=9,
        minute=0,
        id='daily_market_update',
        name='Update All India Market Prices',
        replace_existing=True
    )
    
    # Run at startup if no data
    data, last_updated = load_market_data()
    if not data:
        print("📊 Generating initial market data for all India...")
        update_market_prices_job()
    else:
        print(f"📊 Loaded {len(data)} records for all India, updated: {last_updated}")
    
    scheduler.start()
    print("⏰ Scheduler started - Updates ALL INDIA prices daily at 9:00 AM")
    return scheduler
