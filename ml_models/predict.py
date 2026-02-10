import joblib
import numpy as np
import pandas as pd
import os
from get_fertilizer_details import get_fertilizer_details

# Console colors for consistent logging
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

def log_success(msg): print(f"{Colors.GREEN}✅ [SUCCESS]{Colors.ENDC} {msg}")
def log_warning(msg): print(f"{Colors.YELLOW}⚠️  [WARNING]{Colors.ENDC} {msg}")
def log_error(msg): print(f"{Colors.RED}❌ [ERROR]{Colors.ENDC} {msg}")
def log_info(msg): print(f"{Colors.BLUE}ℹ️  [INFO]{Colors.ENDC} {msg}")

class FertilizerPredictor:
    def __init__(self, model_dir=None):
        """Initialize predictor with trained model"""
        if model_dir is None:
            # Try finding the 'models' directory in multiple common locations
            current_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                os.path.join(os.path.dirname(current_dir), 'models'),  # ../models (Local & Render standard)
                os.path.join(current_dir, 'models'),                     # ./models
                os.path.join(current_dir, '..', 'models'),               # Explicit relative
                '/opt/render/project/src/smartfarmingassitant/models'    # Render absolute
            ]
            
            for path in possible_paths:
                if os.path.exists(path) and os.path.exists(os.path.join(path, 'fertilizer_model.pkl')):
                    model_dir = path
                    log_info(f"Found model directory at: {model_dir}")
                    break
            
            if model_dir is None:
                log_warning(f"Model directory not found. Checked: {possible_paths}")
                # Fallback to default to attempt load (which might fail)
                model_dir = os.path.join(os.path.dirname(current_dir), 'models')
        
        # Fix: Assign model_dir to instance variable
        self.model_dir = model_dir
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
            log_success("Fertilizer ML model loaded successfully!")
            log_info(f"Model loaded from: {self.model_dir}")
        except Exception as e:
            log_error(f"Error loading model: {str(e)}")
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
            top_n_idx = np.argsort(probabilities)[-6:][::-1]
            top_n_fertilizers = self.target_encoder.inverse_transform(top_n_idx)
            top_n_probs = probabilities[top_n_idx]
            
            # Get detailed information
            fertilizer_details_db = get_fertilizer_details()
            
            # Format results with details
            recommendations = []
            for i, (fert, prob) in enumerate(zip(top_n_fertilizers, top_n_probs)):
                details = fertilizer_details_db.get_details(fert)
                recommendations.append({
                    'fertilizer': fert,
                    'confidence': float(prob * 100),
                    'rank': i + 1,
                    'effectiveness': details.get('effectiveness', 'Medium'),
                    'dosage': details.get('dosage', '20-40 kg/acre'),
                    'use': details.get('use_case', 'General use'),
                    'notes': details.get('remark', '')
                })
            
            main_details = fertilizer_details_db.get_details(fertilizer)
            
            return {
                'success': True,
                'recommended_fertilizer': fertilizer,
                'confidence': float(probabilities[self.target_encoder.transform([fertilizer])[0]] * 100),
                'effectiveness': main_details.get('effectiveness', 'Medium'),
                'dosage': main_details.get('dosage', '20-40 kg/acre'),
                'notes': main_details.get('remark', ''),
                'top_recommendations': recommendations
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
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
