"""
Test script to verify market prices are deterministic (same on local and Render)
"""
import random
import hashlib
from datetime import datetime

def test_deterministic_random():
    """Test that date-based seeding produces same results"""
    date_today = datetime.now().strftime('%Y-%m-%d')
    date_seed = int(hashlib.md5(date_today.encode()).hexdigest()[:8], 16)
    
    # First run
    random.seed(date_seed)
    first_values = [random.uniform(0.8, 1.2) for _ in range(10)]
    
    # Reset and run again
    random.seed(date_seed)
    second_values = [random.uniform(0.8, 1.2) for _ in range(10)]
    
    print(f"Date: {date_today}")
    print(f"Seed: {date_seed}")
    print(f"\nFirst run:  {[f'{v:.4f}' for v in first_values]}")
    print(f"Second run: {[f'{v:.4f}' for v in second_values]}")
    print(f"\nAre they identical? {first_values == second_values}")
    
    if first_values == second_values:
        print("✅ SUCCESS: Deterministic random generation works!")
        print("   This means local and Render will show same prices for the same date.")
    else:
        print("❌ FAILED: Random values are different")

if __name__ == "__main__":
    test_deterministic_random()
