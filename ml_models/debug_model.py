import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from predict import get_predictor
import pandas as pd

def test_model_variety():
    """Test if model gives different predictions for different inputs"""
    
    predictor = get_predictor()
    
    print("="*80)
    print("MODEL VARIETY TEST")
    print("="*80)
    
    test_cases = [
        {
            'name': 'Rice - High Nitrogen',
            'params': {
                'temperature': 26, 'moisture': 0.75, 'rainfall': 220,
                'ph': 6.5, 'nitrogen': 85, 'phosphorous': 70, 
                'potassium': 100, 'carbon': 1.8, 
                'soil': 'Loamy Soil', 'crop': 'rice'
            }
        },
        {
            'name': 'Rice - Low Nitrogen',
            'params': {
                'temperature': 26, 'moisture': 0.75, 'rainfall': 220,
                'ph': 6.5, 'nitrogen': 35, 'phosphorous': 70,
                'potassium': 100, 'carbon': 1.8,
                'soil': 'Loamy Soil', 'crop': 'rice'
            }
        },
        {
            'name': 'Wheat - Acidic Soil',
            'params': {
                'temperature': 22, 'moisture': 0.5, 'rainfall': 100,
                'ph': 5.5, 'nitrogen': 60, 'phosphorous': 50,
                'potassium': 55, 'carbon': 1.2,
                'soil': 'Acidic Soil', 'crop': 'wheat'
            }
        },
        {
            'name': 'Wheat - Neutral Soil',
            'params': {
                'temperature': 22, 'moisture': 0.5, 'rainfall': 100,
                'ph': 7.0, 'nitrogen': 60, 'phosphorous': 50,
                'potassium': 55, 'carbon': 1.2,
                'soil': 'Neutral Soil', 'crop': 'wheat'
            }
        },
        {
            'name': 'Maize - Low Phosphorous',
            'params': {
                'temperature': 24, 'moisture': 0.6, 'rainfall': 85,
                'ph': 6.2, 'nitrogen': 55, 'phosphorous': 30,
                'potassium': 52, 'carbon': 1.5,
                'soil': 'Acidic Soil', 'crop': 'maize'
            }
        }
    ]
    
    results = []
    for test in test_cases:
        result = predictor.predict(**test['params'])
        results.append({
            'test': test['name'],
            'fertilizer': result['recommended_fertilizer'],
            'confidence': result['confidence']
        })
        
        print(f"\n{test['name']}:")
        print(f"  → {result['recommended_fertilizer']} ({result['confidence']:.1f}%)")
    
    # Check if all predictions are the same
    unique_fertilizers = set([r['fertilizer'] for r in results])
    
    print("\n" + "="*80)
    print(f"Total unique recommendations: {len(unique_fertilizers)}")
    print(f"Unique fertilizers: {unique_fertilizers}")
    
    if len(unique_fertilizers) == 1:
        print("\n⚠️  WARNING: Model is giving same prediction for all inputs!")
        print("This indicates a problem with the model or data.")
        diagnose_model(predictor)
    else:
        print("\n✓ Model is working correctly - giving varied predictions")
    
    return results

def diagnose_model(predictor):
    """Diagnose model issues"""
    print("\n" + "="*80)
    print("MODEL DIAGNOSTICS")
    print("="*80)
    
    # Check feature importances
    print("\nFeature Importances:")
    feature_names = ['Temperature', 'Moisture', 'Rainfall', 'PH', 
                     'Nitrogen', 'Phosphorous', 'Potassium', 'Carbon', 
                     'Soil', 'Crop']
    
    importances = predictor.model.feature_importances_
    for name, imp in sorted(zip(feature_names, importances), 
                           key=lambda x: x[1], reverse=True):
        print(f"  {name}: {imp:.4f}")
    
    # Check number of classes
    print(f"\nNumber of fertilizer types: {len(predictor.target_encoder.classes_)}")
    print(f"Fertilizer types: {predictor.target_encoder.classes_[:10]}...")
    
    # Check if model is too simple
    print(f"\nModel parameters:")
    print(f"  n_estimators: {predictor.model.n_estimators}")
    print(f"  max_depth: {predictor.model.max_depth}")
    print(f"  min_samples_split: {predictor.model.min_samples_split}")

if __name__ == "__main__":
    test_model_variety()
