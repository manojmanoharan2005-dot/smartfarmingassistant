from flask import Blueprint, render_template, request, jsonify, session
from utils.auth import login_required
import google.generativeai as genai
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

resources_bp = Blueprint('resources', __name__, url_prefix='/resources')

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Error configuring Gemini API in resources: {e}")

@resources_bp.route('/calendar', methods=['GET', 'POST'])
@login_required
def regional_calendar():
    if request.method == 'GET':
        return render_template('regional_calendar.html',
                             user_name=session.get('user_name', 'Farmer'),
                             current_date=datetime.now().strftime('%B %d, %Y'))
    
    # Handle POST request for calendar generation
    try:
        data = request.get_json()
        state = data.get('state')
        district = data.get('district')
        soil_type = data.get('soil_type')
        previous_crops = data.get('previous_crops', '')
        
        if not all([state, district, soil_type]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Construct prompt for Gemini
        prompt = f"""
        Act as an expert agriculturalist. Create a detailed Regional Crop Calendar for a farmer in:
        Location: {district}, {state}, India.
        Soil Type: {soil_type}.
        Previous Crops: {previous_crops}.

        Task:
        1. Identify the 3 main agricultural seasons for this specific region (e.g., Kharif, Rabi, Summer/Zaid).
        2. Suggest 2-3 best suitable crops for each season based on the soil and location.
        3. Provide specific sowing and harvesting windows.
        4. Include brief fertilizer advice and water requirements.
        5. If the soil is not ideal, suggest amendments or alternative crops.

        CRITICAL: Output MUST be valid JSON only, with NO markdown formatting, NO backticks.
        Follow this exact JSON structure:
        {{
            "region": "{district}, {state}",
            "soil_type": "{soil_type}",
            "calendar": [
                {{
                    "season": "Season Name",
                    "months": "e.g., June - September",
                    "recommended_crops": [
                        {{
                            "crop_name": "Name",
                            "sowing_period": "Month Range",
                            "harvesting_period": "Month Range",
                            "fertilizer_advice": "Brief advice",
                            "water_requirement": "Low/Medium/High",
                            "yield_potential": "e.g., High",
                            "market_demand": "e.g., Stable"
                        }}
                    ],
                    "notes": "Specific tip for this season"
                }}
            ],
            "general_advice": "Overall crop rotation or soil health tip"
        }}
        """

        if GEMINI_API_KEY:
            try:
                # Using gemma-3-4b-it as requested for compatibility with the current API key
                model = genai.GenerativeModel('gemma-3-4b-it')
                response = model.generate_content(prompt)
                
                # Clean response text to ensure it's valid JSON
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                calendar_data = json.loads(response_text)
                return jsonify({'success': True, 'data': calendar_data})
                
            except Exception as ai_error:
                print(f"AI Generation Error: {ai_error}")
                # Fallback to manual if AI fails
                return jsonify({'success': True, 'data': get_fallback_data(state, district, soil_type)})
        else:
            # Fallback if no API key
            return jsonify({'success': True, 'data': get_fallback_data(state, district, soil_type)})

    except Exception as e:
        print(f"Calendar generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def get_fallback_data(state, district, soil_type):
    """Provides basic static data if AI service is unavailable"""
    return {
        "region": f"{district}, {state}",
        "soil_type": soil_type,
        "calendar": [
            {
                "season": "Kharif (Monsoon)",
                "months": "June - October",
                "recommended_crops": [
                    {
                        "crop_name": "Rice (Paddy)",
                        "sowing_period": "June - July",
                        "harvesting_period": "October - November",
                        "fertilizer_advice": "Urea in split doses, DAP at sowing",
                        "water_requirement": "High",
                        "yield_potential": "High",
                        "market_demand": "High"
                    },
                    {
                        "crop_name": "Maize",
                        "sowing_period": "June - July",
                        "harvesting_period": "September - October",
                        "fertilizer_advice": "NPK 120:60:40 kg/ha",
                        "water_requirement": "Medium",
                        "yield_potential": "Medium",
                        "market_demand": "Stable"
                    }
                ],
                "notes": "Ensure proper drainage during heavy rains."
            },
            {
                "season": "Rabi (Winter)",
                "months": "October - March",
                "recommended_crops": [
                    {
                        "crop_name": "Wheat",
                        "sowing_period": "November - December",
                        "harvesting_period": "March - April",
                        "fertilizer_advice": "DAP and Potash at sowing, Urea later",
                        "water_requirement": "Medium",
                        "yield_potential": "High",
                        "market_demand": "High"
                    },
                    {
                        "crop_name": "Mustard",
                        "sowing_period": "October - November",
                        "harvesting_period": "February - March",
                        "fertilizer_advice": "Sulphur containing fertilizers recommended",
                        "water_requirement": "Low",
                        "yield_potential": "Medium",
                        "market_demand": "High"
                    }
                ],
                "notes": "Ideal for cold-tolerant crops."
            }
        ],
        "general_advice": "Rotate legumes between cereal crops to restore soil nitrogen naturally."
    }
