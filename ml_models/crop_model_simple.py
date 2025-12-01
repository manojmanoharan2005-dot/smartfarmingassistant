"""
Simplified crop model that works without sklearn
Uses rule-based recommendations when ML packages are not available
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

class SimpleCropRecommendationModel:
    def __init__(self):
        self.crop_rules = {
            'rice': {
                'N': (80, 100), 'P': (35, 60), 'K': (35, 45),
                'temperature': (20, 27), 'humidity': (80, 85), 
                'ph': (5.5, 7.0), 'rainfall': (150, 300)
            },
            'maize': {
                'N': (70, 100), 'P': (40, 60), 'K': (15, 25),
                'temperature': (18, 27), 'humidity': (55, 75), 
                'ph': (5.5, 7.0), 'rainfall': (60, 110)
            },
            'wheat': {
                'N': (70, 90), 'P': (40, 55), 'K': (35, 45),
                'temperature': (12, 25), 'humidity': (55, 70), 
                'ph': (6.0, 7.5), 'rainfall': (75, 180)
            },
            'cotton': {
                'N': (100, 140), 'P': (35, 60), 'K': (15, 25),
                'temperature': (21, 30), 'humidity': (75, 85), 
                'ph': (5.8, 8.0), 'rainfall': (60, 100)
            },
            'jute': {
                'N': (60, 100), 'P': (35, 60), 'K': (35, 45),
                'temperature': (24, 37), 'humidity': (70, 90), 
                'ph': (6.0, 7.5), 'rainfall': (150, 200)
            },
            'banana': {
                'N': (80, 120), 'P': (70, 95), 'K': (45, 55),
                'temperature': (26, 30), 'humidity': (75, 85), 
                'ph': (6.0, 7.5), 'rainfall': (75, 120)
            }
        }
    
    def calculate_suitability(self, crop_name, n, p, k, temp, humidity, ph, rainfall):
        """Calculate suitability score for a crop based on input parameters"""
        if crop_name not in self.crop_rules:
            return 0.0
        
        rules = self.crop_rules[crop_name]
        score = 0.0
        total_factors = 7
        
        # Check each parameter
        factors = [
            ('N', n), ('P', p), ('K', k), ('temperature', temp),
            ('humidity', humidity), ('ph', ph), ('rainfall', rainfall)
        ]
        
        for factor_name, value in factors:
            min_val, max_val = rules[factor_name]
            if min_val <= value <= max_val:
                score += 1.0  # Perfect match
            else:
                # Calculate partial score based on distance from range
                if value < min_val:
                    distance = min_val - value
                    tolerance = min_val * 0.2  # 20% tolerance
                elif value > max_val:
                    distance = value - max_val
                    tolerance = max_val * 0.2  # 20% tolerance
                
                partial_score = max(0, 1 - (distance / tolerance))
                score += partial_score
        
        return min(score / total_factors, 1.0)
    
    def predict_crop_recommendation(self, nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall):
        """Predict crop recommendations using rule-based system"""
        recommendations = []
        
        for crop_name in self.crop_rules.keys():
            suitability = self.calculate_suitability(
                crop_name, nitrogen, phosphorus, potassium, 
                temperature, humidity, ph, rainfall
            )
            
            # Determine priority based on suitability score
            if suitability >= 0.8:
                priority = 'High'
            elif suitability >= 0.6:
                priority = 'Medium'
            else:
                priority = 'Low'
            
            recommendations.append({
                'name': crop_name.capitalize(),
                'probability': suitability,
                'confidence_percentage': suitability * 100,
                'priority': priority
            })
        
        # Sort by probability (descending)
        recommendations.sort(key=lambda x: x['probability'], reverse=True)
        
        return {
            'recommended_crop': recommendations[0]['name'] if recommendations else 'Rice',
            'top_recommendations': recommendations[:6],
            'input_parameters': {
                'nitrogen': nitrogen,
                'phosphorus': phosphorus,
                'potassium': potassium,
                'temperature': temperature,
                'humidity': humidity,
                'ph': ph,
                'rainfall': rainfall
            }
        }

# Global simple predictor instance
simple_crop_predictor = SimpleCropRecommendationModel()

def train_simple_model():
    """Simple training function that sets up the rule-based model"""
    print("🌾 SIMPLE CROP RECOMMENDATION SYSTEM")
    print("=" * 50)
    print("✅ Rule-based model initialized successfully!")
    print("📋 Available crops: Rice, Maize, Wheat, Cotton, Jute, Banana")
    
    # Test prediction
    test_result = simple_crop_predictor.predict_crop_recommendation(
        nitrogen=90, phosphorus=42, potassium=43, 
        temperature=20.8, humidity=82.0, ph=6.5, rainfall=202.9
    )
    
    print(f"\n🔮 TEST PREDICTION:")
    print(f"   Best Crop: {test_result['recommended_crop']}")
    print(f"   Top 3 Recommendations:")
    for i, crop in enumerate(test_result['top_recommendations'][:3], 1):
        print(f"     {i}. {crop['name']}: {crop['confidence_percentage']:.1f}% ({crop['priority']} Priority)")
    
    print(f"\n🎉 Simple model ready for use!")
    return True

if __name__ == "__main__":
    train_simple_model()
