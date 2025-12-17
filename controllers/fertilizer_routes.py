from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.auth import login_required
from datetime import datetime
import sys
import os

# Add path for ML model
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml_models'))

# Optional DB helper - safe import
try:
    from utils.db import save_fertilizer_recommendation
except Exception:
    save_fertilizer_recommendation = None

# Import ML predictor
try:
    from predict import FertilizerPredictor
    ml_predictor = FertilizerPredictor()
    print("✓ ML Fertilizer Predictor loaded successfully")
except Exception as e:
    print(f"✗ Warning: Could not load ML predictor: {e}")
    ml_predictor = None

fertilizer_bp = Blueprint('fertilizer', __name__, url_prefix='/fertilizer')

def generate_fertilizer_recommendations(crop_type, n, p, k, temperature, humidity, soil_moisture):
    """Simple rule-based fertilizer recommender"""
    recommendations = []

    # determine needs
    need_N = n < 70
    need_P = p < 50
    need_K = k < 40
    dry_soil = soil_moisture < 40

    candidates = [
        {'name': 'Urea', 'dosage': '20-30 kg/acre', 'usage': 'Split application during vegetative stage', 'note': 'High N source'},
        {'name': 'DAP (Di-Ammonium Phosphate)', 'dosage': '20-40 kg/acre', 'usage': 'At sowing/rooting', 'note': 'Provides P and some N'},
        {'name': 'MOP (Muriate of Potash)', 'dosage': '15-30 kg/acre', 'usage': 'At flowering/fructification', 'note': 'High K source'},
        {'name': 'NPK 10-26-26', 'dosage': '40-60 kg/acre', 'usage': 'Balanced feed during mid-season', 'note': 'Balanced NPK'},
        {'name': 'Lime (Dolomite)', 'dosage': '0.5-1 ton/acre', 'usage': 'If soil acidic', 'note': 'Corrects low pH'}
    ]

    # scoring
    for c in candidates:
        score = 0.0
        if c['name'] == 'Urea' and need_N:
            score += 0.5
        if c['name'] == 'DAP' and need_P:
            score += 0.5
        if c['name'] == 'MOP' and need_K:
            score += 0.5
        if c['name'] == 'NPK 10-26-26':
            score += 0.25 * (need_N + need_P + need_K)
        if c['name'].lower().startswith('lime') and n is not None:
            # suggest lime when pH low (approx): we don't have pH here — keep lower priority unless soil_moisture indicates problem
            if dry_soil:
                score += 0.15

        # environment adjustments
        if dry_soil and c['name'] == 'Urea':
            score -= 0.05  # lower immediate N if soil dry
        if humidity and humidity > 85 and c['name'] == 'NPK 10-26-26':
            score += 0.05

        final_score = max(0.0, min(score, 1.0))
        confidence = final_score * 100
        priority = 'High' if confidence >= 60 else 'Medium' if confidence >= 35 else 'Low'

        recommendations.append({
            'name': c['name'],
            'dosage': c['dosage'],
            'usage': c['usage'],
            'note': c['note'],
            'probability': final_score,
            'confidence_percentage': confidence,
            'priority': priority
        })

    # sort by score
    recommendations.sort(key=lambda x: x['probability'], reverse=True)
    return recommendations

@fertilizer_bp.route('/recommend', methods=['GET', 'POST'])
@login_required
def fertilizer_recommend():
    if request.method == 'GET':
        # Get available options from ML model
        available_soils = []
        available_crops = []
        if ml_predictor:
            try:
                available_soils = ml_predictor.get_available_soils()
                available_crops = ml_predictor.get_available_crops()
            except:
                pass
        
        return render_template('fertilizer_recommend.html',
                               user_name=session.get('user_name', 'Farmer'),
                               current_date=datetime.now().strftime('%B %d, %Y'),
                               available_soils=available_soils,
                               available_crops=available_crops)

    # POST: Get ML-based recommendations
    try:
        # Get form data - support both old and new format
        temperature = float(request.form.get('temperature', 0))
        moisture = float(request.form.get('moisture', request.form.get('humidity', 0))) / 100.0 if 'humidity' in request.form else float(request.form.get('moisture', 0))
        rainfall = float(request.form.get('rainfall', 200))
        ph = float(request.form.get('ph', 7))
        nitrogen = float(request.form.get('nitrogen', 0))
        phosphorous = float(request.form.get('phosphorous', 0))
        potassium = float(request.form.get('potassium', 0))
        carbon = float(request.form.get('carbon', 1.5))
        soil = request.form.get('soil', 'Loamy Soil')
        crop = request.form.get('crop_type', request.form.get('crop', 'rice'))

        # Use ML model if available
        if ml_predictor:
            result = ml_predictor.predict(
                temperature=temperature,
                moisture=moisture,
                rainfall=rainfall,
                ph=ph,
                nitrogen=nitrogen,
                phosphorous=phosphorous,
                potassium=potassium,
                carbon=carbon,
                soil=soil,
                crop=crop
            )
            
            if result.get('success'):
                # Format recommendations for template
                recommendations = result.get('top_recommendations', [])
                
                # Convert to old format for compatibility
                formatted_recs = []
                for rec in recommendations:
                    formatted_recs.append({
                        'name': rec['fertilizer'],
                        'dosage': rec['dosage'],
                        'usage': rec['use'],
                        'note': rec['notes'],
                        'confidence_percentage': rec['confidence'],
                        'priority': 'High' if rec['confidence'] >= 60 else 'Medium' if rec['confidence'] >= 30 else 'Low',
                        'probability': rec['confidence'] / 100.0
                    })
                
                input_data = {
                    'crop_type': crop,
                    'nitrogen': nitrogen,
                    'phosphorous': phosphorous,
                    'potassium': potassium,
                    'temperature': temperature,
                    'humidity': moisture * 100,
                    'soil_moisture': moisture * 100
                }
                
                flash('🧪 AI-powered fertilizer recommendations generated successfully!', 'success')
                return render_template('fertilizer_recommend.html',
                                       recommendations=formatted_recs,
                                       input_data=input_data,
                                       user_name=session.get('user_name', 'Farmer'),
                                       current_date=datetime.now().strftime('%B %d, %Y'),
                                       available_soils=ml_predictor.get_available_soils() if ml_predictor else [],
                                       available_crops=ml_predictor.get_available_crops() if ml_predictor else [])
            else:
                flash(f'ML Model Error: {result.get("error")}', 'error')
        else:
            # Fallback to rule-based if ML not available
            recommendations = generate_fertilizer_recommendations(
                crop, nitrogen, phosphorous, potassium, temperature, moisture * 100, moisture * 100
            )
            
            input_data = {
                'crop_type': crop,
                'nitrogen': nitrogen,
                'phosphorous': phosphorous,
                'potassium': potassium,
                'temperature': temperature,
                'humidity': moisture * 100,
                'soil_moisture': moisture * 100
            }

            flash('🔍 Rule-based fertilizer recommendations (ML model not available)', 'info')
            return render_template('fertilizer_recommend.html',
                                   recommendations=recommendations,
                                   input_data=input_data,
                                   user_name=session.get('user_name', 'Farmer'),
                                   current_date=datetime.now().strftime('%B %d, %Y'))

    except ValueError as e:
        flash(f'❌ Please provide valid numeric inputs: {e}', 'error')
        return redirect(url_for('fertilizer.fertilizer_recommend'))
    except Exception as e:
        flash(f'❌ Unexpected error: {e}', 'error')
        return redirect(url_for('fertilizer.fertilizer_recommend'))

@fertilizer_bp.route('/save', methods=['POST'])
@login_required
def save_fertilizer():
    user_id = session.get('user_id')
    try:
        fertilizer_data = {
            'name': request.form.get('fertilizer_name'),
            'crop_type': request.form.get('crop_type'),
            'priority': request.form.get('priority'),
            'details': {
                'description': request.form.get('description', ''),
                'application_rate': request.form.get('application_rate', ''),
            },
            'saved_at': datetime.now()
        }

        if save_fertilizer_recommendation:
            save_fertilizer_recommendation(user_id, fertilizer_data)
            flash('Fertilizer recommendation saved!', 'success')
        else:
            # fallback: store in session (simple)
            session.setdefault('saved_fertilizers', []).append(fertilizer_data)
            flash('Saved locally (DB not configured).', 'info')

    except Exception as e:
        flash(f'Error saving recommendation: {e}', 'error')

    return redirect(url_for('fertilizer.fertilizer_recommend'))
