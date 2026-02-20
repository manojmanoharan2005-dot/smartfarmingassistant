# ML Models Directory

This directory contains the trained machine learning models for the Smart Farming Assistant.

## Current Files:

### Fertilizer Recommendation Model:
- `fertilizer_model.pkl` - Trained fertilizer recommendation model
- `label_encoders.pkl` - Label encoders for categorical features  
- `target_encoder.pkl` - Target encoder for fertilizer types
- `scaler.pkl` - Feature scaler for numerical features

### Crop Recommendation Model:
The crop recommendation models (crop_recommendation_model.joblib, feature_scaler.joblib) 
are located in the ml_models/ directory.

## Training:
To train new models, use the datasets in the datasets/ directory and follow the 
training scripts in ml_models/.