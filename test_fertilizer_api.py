"""
Test script to verify fertilizer API functionality
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from predictor import get_predictor
    
    print("=" * 60)
    print("Testing Fertilizer Prediction API")
    print("=" * 60)
    
    # Initialize predictor
    print("\n1. Loading predictor...")
    predictor = get_predictor()
    print("✓ Predictor loaded successfully!")
    
    # Get available options
    print("\n2. Getting available options...")
    soils = predictor.get_available_soils()
    crops = predictor.get_available_crops()
    print(f"✓ Available soils: {len(soils)} types")
    print(f"  {soils[:5]}...")
    print(f"✓ Available crops: {len(crops)} types")
    print(f"  {crops[:5]}...")
    
    # Test prediction with sample data
    print("\n3. Testing prediction...")
    test_data = {
        'temperature': 25.5,
        'moisture': 0.7,
        'rainfall': 200,
        'ph': 6.5,
        'nitrogen': 70,
        'phosphorous': 80,
        'potassium': 100,
        'carbon': 1.5,
        'soil': soils[0] if soils else 'Loamy',
        'crop': crops[0] if crops else 'rice'
    }
    
    print(f"\nTest input:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    result = predictor.predict(**test_data)
    
    if result['success']:
        print(f"\n✓ Prediction successful!")
        print(f"\nMain Recommendation:")
        print(f"  Fertilizer: {result['recommended_fertilizer']}")
        print(f"  Confidence: {result['confidence']:.2f}%")
        print(f"  Level: {result['confidence_level']}")
        
        if 'recommendations' in result and result['recommendations']:
            print(f"\nTop {len(result['recommendations'])} Recommendations:")
            for i, rec in enumerate(result['recommendations'][:3], 1):
                print(f"\n  {i}. {rec['name']}")
                print(f"     - Confidence: {rec['confidence']:.1f}%")
                print(f"     - Priority: {rec['priority']}")
                print(f"     - Dosage: {rec['dosage']}")
                print(f"     - Usage: {rec['usage']}")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
    else:
        print(f"\n✗ Prediction failed: {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
