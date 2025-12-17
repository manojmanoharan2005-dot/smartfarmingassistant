import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from predictor import get_predictor
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fertilizer prediction models
class FertilizerRequest(BaseModel):
    temperature: float
    moisture: float
    rainfall: float
    ph: float
    nitrogen: float
    phosphorous: float
    potassium: float
    carbon: float
    soil: str
    crop: str

@app.post("/api/fertilizer/predict")
async def predict_fertilizer(request: FertilizerRequest):
    """Predict fertilizer recommendation using ML model"""
    try:
        predictor = get_predictor()
        result = predictor.predict(
            temperature=request.temperature,
            moisture=request.moisture,
            rainfall=request.rainfall,
            ph=request.ph,
            nitrogen=request.nitrogen,
            phosphorous=request.phosphorous,
            potassium=request.potassium,
            carbon=request.carbon,
            soil=request.soil,
            crop=request.crop
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/fertilizer/options")
async def get_fertilizer_options():
    """Get available soil types and crops"""
    try:
        predictor = get_predictor()
        return {
            "success": True,
            "soils": predictor.get_available_soils(),
            "crops": predictor.get_available_crops()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Smart Farming API", "status": "running"}