from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.auth import login_required
from utils.db import save_disease_detection, get_user_diseases
from werkzeug.utils import secure_filename
import os
import json
from PIL import Image
import numpy as np

disease_bp = Blueprint('disease', __name__)

# Load disease labels with fallback
try:
    with open(os.path.join(os.path.dirname(__file__), '..', 'datasets', 'disease_labels.json'), 'r') as f:
        disease_labels = json.load(f)
except FileNotFoundError:
    # Fallback disease labels
    disease_labels = {
        "0": "Apple___Apple_scab",
        "1": "Apple___Black_rot", 
        "2": "Corn_(maize)___Common_rust",
        "3": "Tomato___Late_blight",
        "4": "Potato___Early_blight"
    }
    print("Using fallback disease labels")

@disease_bp.route('/disease/detection', methods=['GET', 'POST'])
@login_required
def disease_detection():
    if request.method == 'POST':
        if 'disease_image' not in request.files:
            flash('Please select an image file', 'error')
            return redirect(request.url)
        
        file = request.files['disease_image']
        if file.filename == '':
            flash('Please select an image file', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Ensure uploads directory exists
            os.makedirs('static/uploads', exist_ok=True)
            filepath = os.path.join('static/uploads', filename)
            file.save(filepath)
            
            # Mock disease detection (replace with actual model prediction)
            detected_disease = {
                'disease_name': 'Tomato Late Blight',
                'confidence': 0.87,
                'plant_type': 'Tomato',
                'severity': 'Moderate',
                'remedies': [
                    'Remove affected leaves immediately',
                    'Apply copper-based fungicide', 
                    'Improve air circulation around plants',
                    'Avoid overhead watering'
                ],
                'prevention': [
                    'Use disease-resistant varieties',
                    'Rotate crops annually',
                    'Maintain proper plant spacing',
                    'Monitor weather conditions'
                ],
                'image_path': filepath
            }
            
            # Save to database
            user_id = session['user_id']
            save_disease_detection(user_id, detected_disease)
            
            return render_template('disease_result.html', 
                                 disease=detected_disease,
                                 image_path=filepath)
    
    return render_template('disease_detection.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
