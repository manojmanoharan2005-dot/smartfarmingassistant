import joblib
import numpy as np
import pandas as pd
import os
import sys

# Add parent directory to path to import from other modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_model_components(model_dir='d:/p/smartfarming/models'):
    """Load trained model and encoders"""
    print(f"Loading model from: {model_dir}")
    model = joblib.load(f'{model_dir}/fertilizer_model.pkl')
    label_encoders = joblib.load(f'{model_dir}/label_encoders.pkl')
    target_encoder = joblib.load(f'{model_dir}/target_encoder.pkl')
    scaler = joblib.load(f'{model_dir}/scaler.pkl')
    
    print("✓ Model loaded successfully!")
    return model, label_encoders, target_encoder, scaler

def predict_fertilizer(temperature, moisture, rainfall, ph, nitrogen, 
                       phosphorous, potassium, carbon, soil, crop):
    """Predict fertilizer recommendation for given inputs"""
    
    # Load model components
    model, label_encoders, target_encoder, scaler = load_model_components()
    
    # Prepare input data
    input_data = pd.DataFrame({
        'Temperature': [temperature],
        'Moisture': [moisture],
        'Rainfall': [rainfall],
        'PH': [ph],
        'Nitrogen': [nitrogen],
        'Phosphorous': [phosphorous],
        'Potassium': [potassium],
        'Carbon': [carbon],
        'Soil': [soil],
        'Crop': [crop]
    })
    
    # Encode categorical features
    for col in ['Soil', 'Crop']:
        if col in label_encoders:
            input_data[col] = label_encoders[col].transform(input_data[col])
    
    # Scale numerical features
    numerical_cols = ['Temperature', 'Moisture', 'Rainfall', 'PH', 
                      'Nitrogen', 'Phosphorous', 'Potassium', 'Carbon']
    input_data[numerical_cols] = scaler.transform(input_data[numerical_cols])
    
    # Make prediction
    prediction = model.predict(input_data)
    fertilizer = target_encoder.inverse_transform(prediction)[0]
    
    # Get prediction probabilities
    probabilities = model.predict_proba(input_data)[0]
    top_3_idx = np.argsort(probabilities)[-3:][::-1]
    top_3_fertilizers = target_encoder.inverse_transform(top_3_idx)
    top_3_probs = probabilities[top_3_idx]
    
    return fertilizer, top_3_fertilizers, top_3_probs

def main():
    print("="*60)
    print("FERTILIZER RECOMMENDATION SYSTEM - TEST")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            'name': 'Rice in Loamy Soil',
            'temperature': 25.5,
            'moisture': 0.7,
            'rainfall': 200,
            'ph': 6.5,
            'nitrogen': 70,
            'phosphorous': 80,
            'potassium': 100,
            'carbon': 1.5,
            'soil': 'Loamy Soil',
            'crop': 'rice'
        },
        {
            'name': 'Wheat in Neutral Soil',
            'temperature': 22,
            'moisture': 0.5,
            'rainfall': 100,
            'ph': 6.8,
            'nitrogen': 60,
            'phosphorous': 70,
            'potassium': 80,
            'carbon': 1.2,
            'soil': 'Neutral Soil',
            'crop': 'wheat'
        },
        {
            'name': 'Maize in Acidic Soil',
            'temperature': 24,
            'moisture': 0.6,
            'rainfall': 85,
            'ph': 5.8,
            'nitrogen': 55,
            'phosphorous': 50,
            'potassium': 52,
            'carbon': 1.8,
            'soil': 'Acidic Soil',
            'crop': 'maize'
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"Test Case: {test['name']}")
        print(f"{'='*60}")
        print(f"\nInput Parameters:")
        print(f"  Temperature: {test['temperature']}°C")
        print(f"  Moisture: {test['moisture']}")
        print(f"  Rainfall: {test['rainfall']} mm")
        print(f"  pH: {test['ph']}")
        print(f"  Nitrogen: {test['nitrogen']} kg/ha")
        print(f"  Phosphorous: {test['phosphorous']} kg/ha")
        print(f"  Potassium: {test['potassium']} kg/ha")
        print(f"  Carbon: {test['carbon']} %")
        print(f"  Soil Type: {test['soil']}")
        print(f"  Crop: {test['crop']}")
        
        try:
            fertilizer, top_3, probs = predict_fertilizer(
                test['temperature'], test['moisture'], test['rainfall'],
                test['ph'], test['nitrogen'], test['phosphorous'],
                test['potassium'], test['carbon'], test['soil'], test['crop']
            )
            
            print(f"\n✓ Recommended Fertilizer: {fertilizer}")
            print(f"\nTop 3 Recommendations:")
            for i, (fert, prob) in enumerate(zip(top_3, probs), 1):
                print(f"  {i}. {fert}: {prob*100:.2f}%")
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
    
    print(f"\n{'='*60}")
    print("Testing completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
