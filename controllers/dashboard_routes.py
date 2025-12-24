from flask import Blueprint, render_template, session, redirect, url_for
from utils.auth import login_required
from utils.db import get_user_crops, get_user_fertilizers, find_user_by_id, get_dashboard_notifications, get_user_growing_activities
from datetime import datetime
import json
import os
import random

dashboard_bp = Blueprint('dashboard', __name__)

def get_price_predictions(user_district, user_state):
    """Generate price trend predictions for user's district"""
    # Load market data
    market_file = 'data/market_prices.json'
    if not os.path.exists(market_file):
        return []
    
    with open(market_file, 'r', encoding='utf-8') as f:
        market_data = json.load(f)
    
    # Get commodities for user's district
    district_data = [item for item in market_data['data'] 
                     if item['state'] == user_state and item['district'] == user_district]
    
    if not district_data:
        return []
    
    # Generate predictions for top commodities
    predictions = []
    top_commodities = ['Tomato', 'Onion', 'Potato', 'Cabbage', 'Banana', 'Mango']
    
    for commodity in top_commodities[:4]:  # Top 4 predictions
        commodity_data = [item for item in district_data if item['commodity'] == commodity]
        if commodity_data:
            item = commodity_data[0]
            current_price = item['modal_price']
            
            # Simulate prediction (in real app, use ML model)
            trend = random.choice(['increase', 'decrease', 'stable'])
            if trend == 'increase':
                change_percent = random.randint(8, 25)
                predicted_price = int(current_price * (1 + change_percent/100))
                icon = '📈'
                trend_class = 'bullish'
                message = f"likely to increase by {change_percent}%"
            elif trend == 'decrease':
                change_percent = random.randint(5, 15)
                predicted_price = int(current_price * (1 - change_percent/100))
                icon = '📉'
                trend_class = 'bearish'
                message = f"expected to decrease by {change_percent}%"
            else:
                change_percent = random.randint(-3, 3)
                predicted_price = int(current_price * (1 + change_percent/100))
                icon = '➡️'
                trend_class = 'stable'
                message = "expected to remain stable"
            
            predictions.append({
                'commodity': commodity,
                'current_price': current_price,
                'current_price_kg': round(current_price / 100, 2),
                'predicted_price': predicted_price,
                'predicted_price_kg': round(predicted_price / 100, 2),
                'change_percent': abs(change_percent),
                'trend': trend,
                'trend_class': trend_class,
                'icon': icon,
                'message': message,
                'market': item['market']
            })
    
    return predictions

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    
    # Get complete user data from database (excluding password)
    user = find_user_by_id(user_id)
    
    # If user not found in database, use session data as fallback
    if not user:
        user = {
            '_id': user_id,
            'name': session.get('user_name', 'Unknown User'),
            'email': session.get('user_email', 'No email'),
            'phone': session.get('user_phone', 'Not provided'),
            'state': session.get('user_state', 'Not provided'), 
            'district': session.get('user_district', 'Not provided'),
            'created_at': datetime.utcnow()
        }
    else:
        # Ensure created_at exists for existing users
        if 'created_at' not in user or user['created_at'] is None:
            user['created_at'] = datetime.utcnow()
    
    saved_crops = get_user_crops(user_id)
    saved_fertilizers = get_user_fertilizers(user_id)
    growing_activities = get_user_growing_activities(user_id)
    notifications = get_dashboard_notifications(user_id)
    
    # Get price predictions for user's district
    price_predictions = []
    if user.get('district') and user.get('state'):
        price_predictions = get_price_predictions(user['district'], user['state'])
    
    # Calculate statistics
    stats = {
        'total_recommendations': len(saved_crops) + len(saved_fertilizers),
        'crops_suggested': len(saved_crops),
        'fertilizers_saved': len(saved_fertilizers),
        'active_crops': len(growing_activities)
    }
    
    return render_template('dashboard.html', 
                         user=user,  # Complete user object with real data
                         saved_crops=saved_crops,
                         saved_fertilizers=saved_fertilizers,
                         growing_activities=growing_activities,
                         notifications=notifications,
                         price_predictions=price_predictions,
                         stats=stats)
