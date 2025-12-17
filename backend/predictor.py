import joblib
import numpy as np
import pandas as pd
import os

class FertilizerPredictor:
    def __init__(self, model_dir='../models'):
        """Initialize predictor with trained model"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = os.path.join(base_dir, model_dir)
        self.model = None
        self.label_encoders = None
        self.target_encoder = None
        self.scaler = None
        self.load_model()
    
    def load_model(self):
        """Load trained model and encoders"""
        try:
            self.model = joblib.load(f'{self.model_dir}/fertilizer_model.pkl')
            self.label_encoders = joblib.load(f'{self.model_dir}/label_encoders.pkl')
            self.target_encoder = joblib.load(f'{self.model_dir}/target_encoder.pkl')
            self.scaler = joblib.load(f'{self.model_dir}/scaler.pkl')
            print("✓ Fertilizer model loaded successfully!")
        except Exception as e:
            print(f"✗ Error loading model: {str(e)}")
            raise
    
    def predict(self, temperature, moisture, rainfall, ph, nitrogen, 
                phosphorous, potassium, carbon, soil, crop):
        """Predict fertilizer recommendation"""
        try:
            # Prepare input data
            input_data = pd.DataFrame({
                'Temperature': [float(temperature)],
                'Moisture': [float(moisture)],
                'Rainfall': [float(rainfall)],
                'PH': [float(ph)],
                'Nitrogen': [float(nitrogen)],
                'Phosphorous': [float(phosphorous)],
                'Potassium': [float(potassium)],
                'Carbon': [float(carbon)],
                'Soil': [soil],
                'Crop': [crop]
            })
            
            # Encode categorical features
            for col in ['Soil', 'Crop']:
                if col in self.label_encoders:
                    input_data[col] = self.label_encoders[col].transform(input_data[col])
            
            # Scale numerical features
            numerical_cols = ['Temperature', 'Moisture', 'Rainfall', 'PH', 
                              'Nitrogen', 'Phosphorous', 'Potassium', 'Carbon']
            input_data[numerical_cols] = self.scaler.transform(input_data[numerical_cols])
            
            # Make prediction
            prediction = self.model.predict(input_data)
            fertilizer = self.target_encoder.inverse_transform(prediction)[0]
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba(input_data)[0]
            confidence = float(probabilities[self.target_encoder.transform([fertilizer])[0]] * 100)
            
            # Get top 5 recommendations
            top_5_idx = np.argsort(probabilities)[-5:][::-1]
            top_5_fertilizers = self.target_encoder.inverse_transform(top_5_idx)
            top_5_probs = probabilities[top_5_idx]
            
            # Prepare detailed fertilizer information
            fertilizer_details = self._get_fertilizer_details_map()
            
            recommendations = []
            for i, (fert, prob) in enumerate(zip(top_5_fertilizers, top_5_probs)):
                details = fertilizer_details.get(fert, {})
                conf_pct = float(prob * 100)
                
                # Determine priority based on confidence
                if conf_pct >= 60:
                    priority = "High"
                elif conf_pct >= 30:
                    priority = "Medium"
                else:
                    priority = "Low"
                
                recommendations.append({
                    'name': fert,
                    'confidence': conf_pct,
                    'priority': priority,
                    'dosage': details.get('dosage', '20-40 kg/acre'),
                    'usage': details.get('usage', 'Follow manufacturer instructions'),
                    'note': details.get('note', 'General purpose fertilizer'),
                    'rank': i + 1
                })
            
            # Determine confidence level
            if confidence >= 80:
                confidence_level = "High"
                confidence_message = "Strong recommendation based on soil and crop conditions"
            elif confidence >= 60:
                confidence_level = "Medium"
                confidence_message = "Good match for your conditions"
            else:
                confidence_level = "Low"
                confidence_message = "Consider consulting an agronomist for verification"
            
            return {
                'success': True,
                'recommended_fertilizer': fertilizer,
                'confidence': confidence,
                'confidence_level': confidence_level,
                'confidence_message': confidence_message,
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_fertilizer_details_map(self):
        """Get detailed information for various fertilizers"""
        return {
            'Urea': {
                'dosage': '20-30 kg/acre',
                'usage': 'Split application during vegetative stage',
                'note': 'High nitrogen source (46% N), promotes leaf growth'
            },
            'DAP': {
                'dosage': '15-25 kg/acre',
                'usage': 'Apply at sowing or planting time',
                'note': 'Di-Ammonium Phosphate (18-46-0), excellent for root development'
            },
            'NPK': {
                'dosage': '40-60 kg/acre',
                'usage': 'Apply during mid-season for balanced nutrition',
                'note': 'Balanced NPK fertilizer for all-round crop growth'
            },
            'Balanced NPK Fertilizer': {
                'dosage': '40-60 kg/acre',
                'usage': 'Apply throughout growing season',
                'note': 'Complete nutrition with balanced N-P-K ratio'
            },
            'MOP': {
                'dosage': '15-30 kg/acre',
                'usage': 'Apply during flowering and fruiting stage',
                'note': 'Muriate of Potash (60% K2O), enhances fruit quality'
            },
            'Muriate of Potash': {
                'dosage': '15-30 kg/acre',
                'usage': 'Apply during reproductive stage',
                'note': 'High potassium source, improves disease resistance'
            },
            'SSP': {
                'dosage': '30-50 kg/acre',
                'usage': 'Apply as basal dose before sowing',
                'note': 'Single Super Phosphate, provides P and S'
            },
            'Compost': {
                'dosage': '2-3 ton/acre',
                'usage': 'Apply 2-3 weeks before planting',
                'note': 'Organic matter, improves soil structure and fertility'
            },
            'Organic Fertilizer': {
                'dosage': '1-2 ton/acre',
                'usage': 'Mix with soil before planting',
                'note': 'Slow-release nutrients, improves soil health'
            },
            'Lime': {
                'dosage': '0.5-1 ton/acre',
                'usage': 'Apply 2-3 months before planting',
                'note': 'Corrects soil acidity, provides calcium'
            },
            'Gypsum': {
                'dosage': '0.3-0.5 ton/acre',
                'usage': 'Apply before land preparation',
                'note': 'Provides calcium and sulfur, improves soil structure'
            },
            'Water Retaining Fertilizer': {
                'dosage': '10-20 kg/acre',
                'usage': 'Mix with soil or apply near root zone',
                'note': 'Helps retain moisture in dry conditions'
            },
            'Ammonium Sulphate': {
                'dosage': '25-35 kg/acre',
                'usage': 'Apply in split doses during growth',
                'note': 'Provides nitrogen and sulfur (21-0-0-24S)'
            },
            'Potassium Nitrate': {
                'dosage': '10-15 kg/acre',
                'usage': 'Apply through fertigation or foliar spray',
                'note': 'Water-soluble, provides both N and K'
            }
        }
    
    def get_available_soils(self):
        """Get list of available soil types"""
        return list(self.label_encoders['Soil'].classes_)
    
    def get_available_crops(self):
        """Get list of available crops"""
        return list(self.label_encoders['Crop'].classes_)

# Global predictor instance
predictor = None

def get_predictor():
    """Get or create predictor instance"""
    global predictor
    if predictor is None:
        predictor = FertilizerPredictor()
    return predictor
