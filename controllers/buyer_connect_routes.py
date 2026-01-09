"""
Direct Buyer Connect Routes
Handles farmer listings and buyer marketplace with live price integration
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import datetime, timedelta
from utils.auth import login_required
from utils.db import (
    create_crop_listing, 
    get_user_listings, 
    get_available_listings,
    confirm_purchase,
    get_live_market_price,
    update_listing_status,
    get_listing_by_id,
    find_user_by_id
)
import json
import os

buyer_connect_bp = Blueprint('buyer_connect', __name__, url_prefix='/buyer-connect')

# ============================================
# FARMER ROUTES - Create and Manage Listings
# ============================================

@buyer_connect_bp.route('/create-listing', methods=['GET', 'POST'])
@login_required
def create_listing():
    """Create a new crop listing for sale"""
    user_id = session.get('user_id')
    
    if request.method == 'GET':
        # Load user info for location
        user = find_user_by_id(user_id)
        
        # Get available crops from dataset - Complete commodity list matching market prices
        vegetables = [
            "Tomato", "Onion", "Potato", "Brinjal", "Cabbage", "Cauliflower",
            "Carrot", "Beetroot", "Green Chilli", "Capsicum (Green)", "Capsicum (Red)",
            "Capsicum (Yellow)", "Beans", "Cluster Beans", "Lady Finger", "Drumstick",
            "Bottle Gourd", "Ridge Gourd", "Snake Gourd", "Bitter Gourd", "Pumpkin",
            "Ash Gourd", "Radish", "Turnip", "Sweet Corn", "Peas", "Garlic",
            "Ginger", "Coriander Leaves", "Spinach"
        ]
        
        fruits = [
            "Apple", "Banana", "Orange", "Mosambi", "Grapes", "Pomegranate",
            "Papaya", "Pineapple", "Watermelon", "Muskmelon", "Mango", "Guava",
            "Lemon", "Custard Apple", "Sapota", "Strawberry", "Kiwi", "Pear",
            "Plum", "Peach"
        ]
        
        cereals = [
            "Paddy (Rice – Common)", "Paddy (Basmati)", "Wheat", "Maize (Corn)", "Barley",
            "Jowar (Sorghum)", "Bajra (Pearl Millet)", "Ragi (Finger Millet)"
        ]
        
        pulses = [
            "Red Gram (Tur/Arhar)", "Green Gram (Moong)", "Black Gram (Urad)", "Bengal Gram (Chana)",
            "Lentil (Masur)", "Horse Gram", "Field Pea"
        ]
        
        oilseeds = [
            "Groundnut", "Mustard Seed", "Soybean", "Sunflower Seed", "Sesame (Gingelly)",
            "Castor Seed", "Linseed"
        ]
        
        spices = [
            "Dry Chilli", "Turmeric", "Coriander Seed", "Cumin Seed (Jeera)", "Pepper (Black)",
            "Cardamom", "Clove"
        ]
        
        commercial = [
            "Sugarcane", "Cotton", "Jute", "Copra (Dry Coconut)", "Tobacco", "Tea Leaves", "Coffee Beans"
        ]
        
        dry_fruits = [
            "Coconut", "Cashew Nut", "Groundnut Kernel", "Almond", "Walnut", "Raisins"
        ]
        
        # Combine all crops with categories
        crops = {
            'Vegetables': vegetables,
            'Fruits': fruits,
            'Cereals': cereals,
            'Pulses': pulses,
            'Oilseeds': oilseeds,
            'Spices': spices,
            'Commercial Crops': commercial,
            'Dry Fruits': dry_fruits
        }
        
        # Load states and districts
        import os
        states_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'states_districts.json')
        with open(states_file, 'r') as f:
            states_districts = json.load(f)
        
        return render_template('create_listing.html', 
                             user=user, 
                             crops=crops,
                             states_districts=states_districts,
                             current_date=datetime.now().strftime('%Y-%m-%d'))
    
    # POST: Create listing
    try:
        # Get form data
        crop = request.form.get('crop', '').strip()
        quantity_str = request.form.get('quantity', '').strip()
        unit = request.form.get('unit', 'kg').strip()
        district = request.form.get('district', '').strip()
        state = request.form.get('state', '').strip()
        description = request.form.get('description', '').strip()
        price_str = request.form.get('price', '').strip()
        
        # Validation
        if not all([crop, quantity_str, district, state, price_str]):
            flash('❌ All required fields must be filled', 'error')
            return redirect(url_for('buyer_connect.create_listing'))
        
        try:
            quantity = float(quantity_str)
            farmer_price = float(price_str)
        except ValueError:
            flash('❌ Quantity and price must be valid numbers', 'error')
            return redirect(url_for('buyer_connect.create_listing'))
        
        # Get location coordinates
        latitude_str = request.form.get('latitude', '').strip()
        longitude_str = request.form.get('longitude', '').strip()
        
        try:
            latitude = float(latitude_str) if latitude_str else None
            longitude = float(longitude_str) if longitude_str else None
        except ValueError:
            latitude = None
            longitude = None
        
        # Validate location
        if not latitude or not longitude:
            flash('❌ Please select your location on the map', 'error')
            return redirect(url_for('buyer_connect.create_listing'))
        
        # Validate quantity
        if quantity <= 0:
            flash('❌ Quantity must be greater than 0', 'error')
            return redirect(url_for('buyer_connect.create_listing'))
        
        if quantity > 100000:
            flash('❌ Quantity seems unreasonably high. Please check your input.', 'error')
            return redirect(url_for('buyer_connect.create_listing'))
        
        # Validate price
        if farmer_price <= 0:
            flash('❌ Price must be greater than 0', 'error')
            return redirect(url_for('buyer_connect.create_listing'))
        
        # Get live market price
        live_price_data = get_live_market_price(crop, district, state)
        
        if not live_price_data:
            flash('❌ Could not fetch live market price. Please try again.', 'error')
            return redirect(url_for('buyer_connect.create_listing'))
        
        recommended_price = live_price_data['recommended_price']
        min_allowed = live_price_data['min_price']
        max_allowed = live_price_data['max_price']
        
        # BACKEND VALIDATION: Price must be within ±20% of live price
        if farmer_price < min_allowed or farmer_price > max_allowed:
            flash(f'❌ Price must be between ₹{min_allowed:.2f}/kg and ₹{max_allowed:.2f}/kg (±20% of market price ₹{recommended_price:.2f}/kg)', 'error')
            return redirect(url_for('buyer_connect.create_listing'))
        
        # Get farmer info for the listing
        farmer = find_user_by_id(user_id)
        farmer_name = farmer.get('name', 'Unknown') if farmer else 'Unknown'
        farmer_phone = farmer.get('phone', '') if farmer else ''
        
        # Create listing object
        listing_data = {
            'farmer_id': user_id,
            'farmer_name': farmer_name,
            'farmer_phone': farmer_phone,
            'crop': crop,
            'quantity': quantity,
            'unit': unit,
            'district': district,
            'state': state,
            'latitude': latitude,
            'longitude': longitude,
            'description': description,
            'farmer_price': farmer_price,
            'recommended_price': recommended_price,
            'min_price': min_allowed,
            'max_price': max_allowed,
            'live_market_price': recommended_price,
            'status': 'available',  # available, sold, expired
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        # Save to MongoDB
        listing_id = create_crop_listing(listing_data)
        
        if listing_id:
            flash('✅ Your crop listing has been created successfully!', 'success')
            return redirect(url_for('buyer_connect.my_listings'))
        else:
            flash('❌ Failed to create listing. Please try again.', 'error')
            return redirect(url_for('buyer_connect.create_listing'))
            
    except ValueError as e:
        flash(f'❌ Invalid input: {str(e)}', 'error')
        return redirect(url_for('buyer_connect.create_listing'))
    except Exception as e:
        flash(f'❌ Error creating listing: {str(e)}', 'error')
        return redirect(url_for('buyer_connect.create_listing'))


@buyer_connect_bp.route('/my-listings')
@login_required
def my_listings():
    """View farmer's own listings"""
    user_id = session.get('user_id')
    listings = get_user_listings(user_id)
    
    return render_template('my_listings.html', listings=listings)


@buyer_connect_bp.route('/api/get-live-price', methods=['POST'])
@login_required
def api_get_live_price():
    """API endpoint to fetch live market price for auto-fill"""
    try:
        data = request.get_json()
        crop = data.get('crop')
        district = data.get('district')
        state = data.get('state')
        
        if not all([crop, district, state]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        price_data = get_live_market_price(crop, district, state)
        
        if price_data:
            return jsonify({
                'success': True,
                'recommended_price': price_data['recommended_price'],
                'min_price': price_data['min_price'],
                'max_price': price_data['max_price'],
                'market_name': price_data.get('market', 'Local Mandi'),
                'price_date': price_data.get('date', datetime.now().strftime('%Y-%m-%d'))
            })
        else:
            return jsonify({'success': False, 'error': 'No price data available for this crop and location'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# BUYER ROUTES - Marketplace and Purchase
# ============================================

@buyer_connect_bp.route('/marketplace')
@login_required
def marketplace():
    """Buyer marketplace showing all available listings"""
    # Get filters from query params
    crop_filter = request.args.get('crop', '')
    district_filter = request.args.get('district', '')
    state_filter = request.args.get('state', '')
    sort_by = request.args.get('sort', 'recent')  # recent, price_low, price_high
    
    # Get only available listings
    listings = get_available_listings(
        crop=crop_filter,
        district=district_filter,
        state=state_filter,
        sort_by=sort_by
    )
    
    # Get unique values for filters
    all_listings = get_available_listings()
    crops = sorted(set(l['crop'] for l in all_listings))
    states = sorted(set(l['state'] for l in all_listings))
    
    return render_template('buyer_marketplace.html',
                         listings=listings,
                         crops=crops,
                         states=states,
                         crop_filter=crop_filter,
                         district_filter=district_filter,
                         state_filter=state_filter,
                         sort_by=sort_by)


@buyer_connect_bp.route('/listing/<listing_id>')
@login_required
def view_listing(listing_id):
    """View detailed listing page"""
    listing = get_listing_by_id(listing_id)
    
    if not listing:
        flash('❌ Listing not found', 'error')
        return redirect(url_for('buyer_connect.marketplace'))
    
    # Don't show sold listings
    if listing['status'] != 'available':
        flash('❌ This listing is no longer available', 'error')
        return redirect(url_for('buyer_connect.marketplace'))
    
    return render_template('listing_detail.html', listing=listing)


@buyer_connect_bp.route('/api/confirm-purchase', methods=['POST'])
@login_required
def api_confirm_purchase():
    """Confirm purchase and update listing status atomically"""
    try:
        buyer_id = session.get('user_id')
        data = request.get_json()
        listing_id = data.get('listing_id')
        buyer_name = data.get('buyer_name', '').strip()
        buyer_phone = data.get('buyer_phone', '').strip()
        
        # Validation
        if not all([listing_id, buyer_name, buyer_phone]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        # Validate phone number
        if not buyer_phone.isdigit() or len(buyer_phone) != 10:
            return jsonify({'success': False, 'error': 'Phone number must be 10 digits'}), 400
        
        # Get listing details
        listing = get_listing_by_id(listing_id)
        if not listing:
            return jsonify({'success': False, 'error': 'Listing not found'}), 404
        
        # Check if listing is available
        if listing['status'] != 'available':
            return jsonify({'success': False, 'error': 'This listing is no longer available'}), 400
        
        # Prevent farmers from buying their own crops
        if listing['farmer_id'] == buyer_id:
            return jsonify({'success': False, 'error': 'You cannot purchase your own listing'}), 400
        
        # Atomic update to prevent double-selling
        purchase_data = {
            'buyer_id': buyer_id,
            'buyer_name': buyer_name,
            'buyer_phone': buyer_phone,
            'purchased_at': datetime.utcnow().isoformat()
        }
        
        success, message = confirm_purchase(listing_id, purchase_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Purchase confirmed! The farmer will contact you soon.'
            })
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        print(f"Purchase error: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred. Please try again.'}), 500


@buyer_connect_bp.route('/api/cancel-listing/<listing_id>', methods=['POST'])
@login_required
def api_cancel_listing(listing_id):
    """Cancel/delete a listing (farmer only)"""
    try:
        user_id = session.get('user_id')
        
        # Get listing and verify ownership
        listing = get_listing_by_id(listing_id)
        
        if not listing:
            return jsonify({'success': False, 'error': 'Listing not found'}), 404
        
        if listing['farmer_id'] != user_id:
            return jsonify({'success': False, 'error': 'You can only cancel your own listings'}), 403
        
        # Check if already sold
        if listing['status'] == 'sold':
            return jsonify({'success': False, 'error': 'Cannot cancel a sold listing'}), 400
        
        # Check if already cancelled
        if listing['status'] == 'cancelled':
            return jsonify({'success': False, 'error': 'Listing is already cancelled'}), 400
        
        # Update status to cancelled
        success = update_listing_status(listing_id, 'cancelled')
        
        if success:
            return jsonify({'success': True, 'message': 'Listing cancelled successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to cancel listing. Please try again.'}), 500
            
    except Exception as e:
        print(f"Cancel listing error: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred. Please try again.'}), 500
