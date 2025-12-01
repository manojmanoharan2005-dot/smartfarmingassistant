from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.auth import login_required
from datetime import datetime

# Optional DB helper - safe import
try:
    from utils.db import save_fertilizer_recommendation
except Exception:
    save_fertilizer_recommendation = None

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
        return render_template('fertilizer_recommend.html',
                               user_name=session.get('user_name', 'Farmer'),
                               current_date=datetime.now().strftime('%B %d, %Y'))

    # POST: compute recommendations
    try:
        crop_type = request.form.get('crop_type', '')
        nitrogen = float(request.form.get('nitrogen', 0))
        phosphorous = float(request.form.get('phosphorous', 0))
        potassium = float(request.form.get('potassium', 0))
        temperature = float(request.form.get('temperature', 0))
        humidity = float(request.form.get('humidity', 0))
        soil_moisture = float(request.form.get('soil_moisture', 0))

        recommendations = generate_fertilizer_recommendations(
            crop_type, nitrogen, phosphorous, potassium, temperature, humidity, soil_moisture
        )

        input_data = {
            'crop_type': crop_type,
            'nitrogen': nitrogen,
            'phosphorous': phosphorous,
            'potassium': potassium,
            'temperature': temperature,
            'humidity': humidity,
            'soil_moisture': soil_moisture
        }

        flash('🔍 Fertilizer recommendations generated', 'success')
        return render_template('fertilizer_recommend.html',
                               recommendations=recommendations,
                               input_data=input_data,
                               user_name=session.get('user_name', 'Farmer'),
                               current_date=datetime.now().strftime('%B %d, %Y'))

    except ValueError:
        flash('Please provide valid numeric inputs', 'error')
        return redirect(url_for('fertilizer.fertilizer_recommend'))
    except Exception as e:
        flash(f'Unexpected error: {e}', 'error')
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
