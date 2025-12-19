import requests

API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
API_BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

print("Testing Data.gov.in API...")
print(f"API URL: {API_BASE_URL}")
print(f"API Key: {API_KEY[:20]}...")
print()

params = {
    'api-key': API_KEY,
    'format': 'json',
    'limit': 10,
    'offset': 0
}

try:
    response = requests.get(API_BASE_URL, params=params, timeout=10)
    print(f"Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total Records: {data.get('total', 'N/A')}")
        print(f"Records Returned: {len(data.get('records', []))}")
        print()
        
        records = data.get('records', [])
        
        if len(records) > 0:
            print("Sample Record:")
            print(records[0])
            print()
            
            # Check available states
            states = set()
            for record in records:
                state = record.get('state', '').strip()
                if state:
                    states.add(state)
            
            print(f"States found in first 10 records: {sorted(states)}")
            print()
            
            # Check for Gujarat
            gujarat_records = [r for r in records if r.get('state', '').strip() == 'Gujarat']
            print(f"Gujarat records in first 10: {len(gujarat_records)}")
            
            # Check for Tamil Nadu
            tn_records = [r for r in records if r.get('state', '').strip() == 'Tamil Nadu']
            print(f"Tamil Nadu records in first 10: {len(tn_records)}")
        else:
            print("No records returned!")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
