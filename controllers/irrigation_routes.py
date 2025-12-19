from flask import Blueprint, render_template, session, request, jsonify
from utils.auth import login_required
from datetime import datetime
import random

irrigation_bp = Blueprint('irrigation', __name__)

@irrigation_bp.route('/smart-irrigation')
@login_required
def smart_irrigation():
    user_name = session.get('user_name', 'Guest')
    user_state = session.get('user_state', 'Unknown')
    user_district = session.get('user_district', 'Unknown')
    
    # Simulated soil moisture (can be enhanced with weather API data)
    soil_moisture = random.randint(30, 75)
    pump_status = session.get('pump_status', 'OFF')
    
    # Format current date
    current_date = datetime.now().strftime('%B %d, %Y')
    
    return render_template('smart_irrigation.html',
                         user_name=user_name,
                         user_state=user_state,
                         user_district=user_district,
                         soil_moisture=soil_moisture,
                         pump_status=pump_status,
                         current_date=current_date)

@irrigation_bp.route('/toggle-pump', methods=['POST'])
@login_required
def toggle_pump():
    data = request.json
    new_status = data.get('status', 'OFF')
    session['pump_status'] = new_status
    
    return jsonify({
        'success': True,
        'status': new_status,
        'message': f'Water pump turned {new_status}'
    })

@irrigation_bp.route('/get-moisture', methods=['GET'])
@login_required
def get_moisture():
    # Simulate moisture reading (could integrate with weather API)
    moisture = random.randint(30, 75)
    
    recommendation = ''
    if moisture < 40:
        recommendation = 'Low moisture detected. Irrigation recommended.'
    elif moisture < 60:
        recommendation = 'Moderate moisture. Monitor closely.'
    else:
        recommendation = 'Good moisture level. No irrigation needed.'
    
    return jsonify({
        'moisture': moisture,
        'recommendation': recommendation
    })
