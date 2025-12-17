# How to Run the Fertilizer Recommendation System

## Overview
The fertilizer recommendation system has two components:
1. **Backend API** (FastAPI) - Handles ML model predictions
2. **Frontend** (Flask) - User interface

## Setup Instructions

### 1. Start the Backend API Server

Open a terminal in the `smartfarming` directory and run:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at: `http://localhost:8000`

You can test it by visiting: `http://localhost:8000/docs` (Swagger UI)

### 2. Start the Frontend Flask Server

Open another terminal in the `smartfarming` directory and run:

```bash
python app.py
```

The frontend will be available at: `http://localhost:5000`

### 3. Using the Fertilizer Recommendation Feature

1. Navigate to the fertilizer recommendation page
2. Fill in all the required fields:
   - **Temperature** (°C): e.g., 25.5
   - **Moisture** (0-1): e.g., 0.7
   - **Rainfall** (mm): e.g., 200
   - **pH Level**: e.g., 6.5
   - **Nitrogen** (kg/ha): e.g., 70
   - **Phosphorous** (kg/ha): e.g., 80
   - **Potassium** (kg/ha): e.g., 100
   - **Carbon** (%): e.g., 1.5
   - **Soil Type**: Select from dropdown
   - **Crop Type**: Select from dropdown

3. Click **"Get AI Recommendation"** button

4. The system will display:
   - Main recommended fertilizer with confidence level
   - Top 5 fertilizer recommendations with:
     - Confidence percentage
     - Priority level (High/Medium/Low)
     - Recommended dosage
     - Usage instructions
     - Important notes
   - Application guidelines

## Features

✅ **ML-Powered Predictions**: Uses a trained Random Forest model
✅ **Multiple Recommendations**: Shows top 5 fertilizers ranked by confidence
✅ **Detailed Information**: Includes dosage, usage timing, and notes for each fertilizer
✅ **Visual Confidence Indicators**: Color-coded priority levels and progress bars
✅ **Responsive Design**: Works on desktop, tablet, and mobile devices

## Troubleshooting

### Backend Not Starting
- Ensure all required packages are installed: `pip install -r backend/requirements.txt`
- Check if port 8000 is already in use
- Verify the ML model files exist in the `models` directory

### Frontend Not Connecting to Backend
- Make sure the backend is running on `http://localhost:8000`
- Check the `API_BASE` URL in `fertilizer_recommendation.html`
- Verify CORS settings in `backend/main.py`

### Model Loading Errors
- The system requires these files in the `models` directory:
  - `fertilizer_model.pkl`
  - `label_encoders.pkl`
  - `target_encoder.pkl`
  - `scaler.pkl`
- If missing, run: `python ml_models/train_fertilizer_model.py`

## Testing the API

Use the test script to verify everything is working:

```bash
python test_fertilizer_api.py
```

This will:
- Load the predictor
- Show available soil types and crops
- Make a test prediction
- Display the results with multiple fertilizer recommendations

## Example API Request

```python
import requests

data = {
    "temperature": 25.5,
    "moisture": 0.7,
    "rainfall": 200,
    "ph": 6.5,
    "nitrogen": 70,
    "phosphorous": 80,
    "potassium": 100,
    "carbon": 1.5,
    "soil": "Loamy Soil",
    "crop": "rice"
}

response = requests.post("http://localhost:8000/api/fertilizer/predict", json=data)
result = response.json()
print(result)
```

## Notes

- The system provides AI-powered recommendations based on soil and crop conditions
- For low confidence predictions (< 60%), professional consultation is recommended
- Dosage recommendations are general guidelines - always follow local agricultural extension advice
- The model has been trained on diverse agricultural datasets for multiple crops and soil types
