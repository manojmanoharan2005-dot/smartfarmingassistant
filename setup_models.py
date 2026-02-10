#!/usr/bin/env python3
"""
Setup script for Smart Farming Assistant ML Models
This script creates the necessary model directory structure and placeholder files.
"""

import os
import sys

def create_model_structure():
    """Create the model directory structure"""
    
    # Console colors
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    print(f"\n{BLUE}{BOLD}🔧 Smart Farming Assistant - Model Setup{ENDC}")
    print("=" * 50)
    
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(current_dir, 'models')
    
    print(f"{BLUE}📁 Creating models directory at: {models_dir}{ENDC}")
    
    # Create models directory
    os.makedirs(models_dir, exist_ok=True)
    
    # Create placeholder files for fertilizer model
    model_files = [
        'fertilizer_model.pkl',
        'label_encoders.pkl', 
        'target_encoder.pkl',
        'scaler.pkl'
    ]
    
    for file_name in model_files:
        file_path = os.path.join(models_dir, file_name)
        if not os.path.exists(file_path):
            # Create empty placeholder file
            with open(file_path, 'w') as f:
                f.write("# Placeholder for ML model file\n")
                f.write(f"# This file should contain the trained {file_name}\n")
            print(f"{GREEN}✅ Created placeholder: {file_name}{ENDC}")
        else:
            print(f"{YELLOW}⚠️  File already exists: {file_name}{ENDC}")
    
    # Create README in models directory
    readme_content = """# ML Models Directory

This directory contains the trained machine learning models for the Smart Farming Assistant.

## Required Files:

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

## Notes:
- Model files are not included in version control due to size
- Contact the development team for pre-trained models
- Ensure models are compatible with the current scikit-learn version
"""
    
    readme_path = os.path.join(models_dir, 'README.md')
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"{GREEN}✅ Created README.md{ENDC}")
    print(f"\n{GREEN}🎉 Model directory setup complete!{ENDC}")
    print(f"{YELLOW}📝 Note: Replace placeholder files with actual trained models{ENDC}")
    print(f"{BLUE}💡 The app will now find the models directory and run without errors{ENDC}\n")

if __name__ == "__main__":
    create_model_structure()