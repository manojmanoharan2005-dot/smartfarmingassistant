"""
Equipment Sharing Routes (Similar to Buyer Connect)
Handles equipment owner listings and renter marketplace with live pricing
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import datetime, timedelta
from utils.auth import login_required
from utils.db import (
    create_equipment_listing,
    get_user_equipment_listings,
    get_available_equipment,
    confirm_equipment_rental,
    get_live_equipment_rent,
    update_equipment_status,
    get_equipment_listing_by_id,
    find_user_by_id
)
import json
import os

equipment_sharing_bp = Blueprint('equipment_sharing', __name__, url_prefix='/equipment-sharing')

# ============================================
# OWNER ROUTES - Create and Manage Equipment Listings
# ============================================

@equipment_sharing_bp.route('/create-listing', methods=['GET', 'POST'])
@login_required
def create_listing():
    """Create a new equipment listing for rent"""
    user_id = session.get('user_id')
    
    if request.method == 'GET':
        # Load user info for location
        user = find_user_by_id(user_id)
        
        # Available equipment types
        equipment_types = [
            'Tractor', 'Harvester', 'Plough', 'Seed Drill', 'Sprayer',
            'Cultivator', 'Rotavator', 'Thresher', 'Irrigation Pump',
            'Trailer', 'Disc Harrow', 'Leveler'
        ]
        
        # Load states and districts
        states_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'states_districts.json')
        with open(states_file, 'r') as f:
            states_districts = json.load(f)
        
        return render_template('equipment_create_listing.html',
                             user=user,
                             equipment_types=equipment_types,
                             states_districts=states_districts,
                             current_date=datetime.now().strftime('%Y-%m-%d'))
    
    # POST: Create listing
    try:
        # Get form data
        equipment_name = request.form.get('equipment_name', '').strip()
        district = request.form.get('district', '').strip()
        state = request.form.get('state', '').strip()
        description = request.form.get('description', '').strip()
        rent_str = request.form.get('rent', '').strip()
        available_from = request.form.get('available_from', '').strip()
        available_to = request.form.get('available_to', '').strip()
        
        # Validation
        if not all([equipment_name, district, state, rent_str, available_from, available_to]):
            flash('❌ All required fields must be filled', 'error')
            return redirect(url_for('equipment_sharing.create_listing'))
        
        try:
            owner_rent = float(rent_str)
        except ValueError:
            flash('❌ Rent must be a valid number', 'error')
            return redirect(url_for('equipment_sharing.create_listing'))
        
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
            return redirect(url_for('equipment_sharing.create_listing'))
        
        # Validate rent
        if owner_rent <= 0:
            flash('❌ Rent must be greater than 0', 'error')
            return redirect(url_for('equipment_sharing.create_listing'))
        
        # Get live market rent
        live_rent_data = get_live_equipment_rent(equipment_name, district, state)
        
        if not live_rent_data:
            flash('❌ Could not fetch live market rent. Please try again.', 'error')
            return redirect(url_for('equipment_sharing.create_listing'))
        
        recommended_rent = live_rent_data['recommended_rent']
        min_allowed = live_rent_data['min_rent']
        max_allowed = live_rent_data['max_rent']
        
        # BACKEND VALIDATION: Rent must be within ±15% of live rent
        if owner_rent < min_allowed or owner_rent > max_allowed:
            flash(f'❌ Rent must be between ₹{min_allowed:.2f}/day and ₹{max_allowed:.2f}/day (±15% of market rent ₹{recommended_rent:.2f}/day)', 'error')
            return redirect(url_for('equipment_sharing.create_listing'))
        
        # Validate dates
        try:
            from_date = datetime.strptime(available_from, '%Y-%m-%d')
            to_date = datetime.strptime(available_to, '%Y-%m-%d')
            
            if from_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                flash('❌ Start date cannot be in the past', 'error')
                return redirect(url_for('equipment_sharing.create_listing'))
            
            if to_date <= from_date:
                flash('❌ End date must be after start date', 'error')
                return redirect(url_for('equipment_sharing.create_listing'))
        except ValueError:
            flash('❌ Invalid date format', 'error')
            return redirect(url_for('equipment_sharing.create_listing'))
        
        # Get owner info for the listing
        owner = find_user_by_id(user_id)
        owner_name = owner.get('name', 'Unknown') if owner else 'Unknown'
        owner_phone = owner.get('phone', '') if owner else ''
        
        # Create listing object
        listing_data = {
            'owner_id': user_id,
            'owner_name': owner_name,
            'owner_phone': owner_phone,
            'equipment_name': equipment_name,
            'district': district,
            'state': state,
            'latitude': latitude,
            'longitude': longitude,
            'description': description,
            'owner_rent': owner_rent,
            'recommended_rent': recommended_rent,
            'min_rent': min_allowed,
            'max_rent': max_allowed,
            'live_market_rent': recommended_rent,
            'available_from': available_from,
            'available_to': available_to,
            'status': 'available',  # available, booked, completed, cancelled
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Save to database
        listing_id = create_equipment_listing(listing_data)
        
        if listing_id:
            flash('✅ Your equipment listing has been created successfully!', 'success')
            return redirect(url_for('equipment_sharing.my_listings'))
        else:
            flash('❌ Failed to create listing. Please try again.', 'error')
            return redirect(url_for('equipment_sharing.create_listing'))
            
    except ValueError as e:
        flash(f'❌ Invalid input: {str(e)}', 'error')
        return redirect(url_for('equipment_sharing.create_listing'))
    except Exception as e:
        flash(f'❌ Error creating listing: {str(e)}', 'error')
        return redirect(url_for('equipment_sharing.create_listing'))


@equipment_sharing_bp.route('/my-listings')
@login_required
def my_listings():
    """View owner's own equipment listings"""
    user_id = session.get('user_id')
    listings = get_user_equipment_listings(user_id)
    
    return render_template('equipment_my_listings.html', listings=listings)


@equipment_sharing_bp.route('/api/get-live-rent', methods=['POST'])
@login_required
def api_get_live_rent():
    """API endpoint to fetch live market rent for auto-fill"""
    try:
        data = request.get_json()
        equipment_name = data.get('equipment_name')
        district = data.get('district')
        state = data.get('state')
        
        if not all([equipment_name, district, state]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        rent_data = get_live_equipment_rent(equipment_name, district, state)
        
        if rent_data:
            return jsonify({
                'success': True,
                'recommended_rent': rent_data['recommended_rent'],
                'min_rent': rent_data['min_rent'],
                'max_rent': rent_data['max_rent']
            })
        else:
            return jsonify({'success': False, 'error': 'No rent data available for this equipment and location'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# RENTER ROUTES - Marketplace and Booking
# ============================================

@equipment_sharing_bp.route('/marketplace')
@login_required
def marketplace():
    """Renter marketplace showing all available equipment"""
    # Get filters from query params
    equipment_filter = request.args.get('equipment', '')
    district_filter = request.args.get('district', '')
    state_filter = request.args.get('state', '')
    sort_by = request.args.get('sort', 'recent')  # recent, rent_low, rent_high
    
    # Get only available equipment
    listings = get_available_equipment(
        equipment_name=equipment_filter,
        district=district_filter,
        state=state_filter,
        sort_by=sort_by
    )
    
    # Get unique values for filters
    all_listings = get_available_equipment()
    equipment_types = sorted(set(l['equipment_name'] for l in all_listings))
    states = sorted(set(l['state'] for l in all_listings))
    
    return render_template('equipment_marketplace.html',
                         listings=listings,
                         equipment_types=equipment_types,
                         states=states,
                         equipment_filter=equipment_filter,
                         district_filter=district_filter,
                         state_filter=state_filter,
                         sort_by=sort_by)


@equipment_sharing_bp.route('/listing/<listing_id>')
@login_required
def view_listing(listing_id):
    """View detailed equipment listing page"""
    listing = get_equipment_listing_by_id(listing_id)
    
    if not listing:
        flash('❌ Listing not found', 'error')
        return redirect(url_for('equipment_sharing.marketplace'))
    
    # Don't show booked/completed listings
    if listing['status'] != 'available':
        flash('❌ This equipment is no longer available', 'error')
        return redirect(url_for('equipment_sharing.marketplace'))
    
    return render_template('equipment_listing_detail.html', listing=listing)


@equipment_sharing_bp.route('/api/confirm-rental', methods=['POST'])
@login_required
def api_confirm_rental():
    """Confirm equipment rental and update listing status atomically"""
    try:
        renter_id = session.get('user_id')
        data = request.get_json()
        listing_id = data.get('listing_id')
        renter_name = data.get('renter_name', '').strip()
        renter_phone = data.get('renter_phone', '').strip()
        rental_from = data.get('rental_from', '').strip()
        rental_to = data.get('rental_to', '').strip()
        
        # Validation
        if not all([listing_id, renter_name, renter_phone, rental_from, rental_to]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        # Validate phone number
        if not renter_phone.isdigit() or len(renter_phone) != 10:
            return jsonify({'success': False, 'error': 'Phone number must be 10 digits'}), 400
        
        # Validate dates
        try:
            from_date = datetime.strptime(rental_from, '%Y-%m-%d')
            to_date = datetime.strptime(rental_to, '%Y-%m-%d')
            
            if from_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                return jsonify({'success': False, 'error': 'Start date cannot be in the past'}), 400
            
            if to_date <= from_date:
                return jsonify({'success': False, 'error': 'End date must be after start date'}), 400
                
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format'}), 400
        
        # Get listing details
        listing = get_equipment_listing_by_id(listing_id)
        if not listing:
            return jsonify({'success': False, 'error': 'Listing not found'}), 404
        
        # Check if listing is available
        if listing['status'] != 'available':
            return jsonify({'success': False, 'error': 'This equipment is no longer available'}), 400
        
        # Prevent owners from booking their own equipment
        if listing['owner_id'] == renter_id:
            return jsonify({'success': False, 'error': 'You cannot book your own equipment'}), 400
        
        # Check if rental dates are within availability period
        available_from = datetime.strptime(listing['available_from'], '%Y-%m-%d')
        available_to = datetime.strptime(listing['available_to'], '%Y-%m-%d')
        
        if from_date < available_from or to_date > available_to:
            return jsonify({
                'success': False,
                'error': f'Rental dates must be between {listing["available_from"]} and {listing["available_to"]}'
            }), 400
        
        # Calculate total rent
        rental_days = (to_date - from_date).days + 1
        total_rent = listing['owner_rent'] * rental_days
        
        # Atomic update to prevent double-booking
        rental_data = {
            'renter_id': renter_id,
            'renter_name': renter_name,
            'renter_phone': renter_phone,
            'rental_from': rental_from,
            'rental_to': rental_to,
            'rental_days': rental_days,
            'total_rent': total_rent,
            'booked_at': datetime.utcnow().isoformat()
        }
        
        success, message = confirm_equipment_rental(listing_id, rental_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Booking confirmed! Total rent: ₹{total_rent:.2f} for {rental_days} days. The owner will contact you soon.'
            })
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        print(f"Rental error: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred. Please try again.'}), 500


@equipment_sharing_bp.route('/api/cancel-listing/<listing_id>', methods=['POST'])
@login_required
def api_cancel_listing(listing_id):
    """Cancel/delete an equipment listing (owner only)"""
    try:
        user_id = session.get('user_id')
        
        # Get listing and verify ownership
        listing = get_equipment_listing_by_id(listing_id)
        
        if not listing:
            return jsonify({'success': False, 'error': 'Listing not found'}), 404
        
        if listing['owner_id'] != user_id:
            return jsonify({'success': False, 'error': 'You can only cancel your own listings'}), 403
        
        # Check if already booked
        if listing['status'] == 'booked':
            return jsonify({'success': False, 'error': 'Cannot cancel a booked listing. Please contact the renter.'}), 400
        
        # Check if already completed
        if listing['status'] == 'completed':
            return jsonify({'success': False, 'error': 'Cannot cancel a completed rental'}), 400
        
        # Check if already cancelled
        if listing['status'] == 'cancelled':
            return jsonify({'success': False, 'error': 'Listing is already cancelled'}), 400
        
        # Update status to cancelled
        success = update_equipment_status(listing_id, 'cancelled')
        
        if success:
            return jsonify({'success': True, 'message': 'Listing cancelled successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to cancel listing. Please try again.'}), 500
            
    except Exception as e:
        print(f"Cancel listing error: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred. Please try again.'}), 500


@equipment_sharing_bp.route('/api/complete-rental/<listing_id>', methods=['POST'])
@login_required
def api_complete_rental(listing_id):
    """Mark equipment rental as completed (owner only)"""
    try:
        user_id = session.get('user_id')
        
        # Get listing and verify ownership
        listing = get_equipment_listing_by_id(listing_id)
        
        if not listing:
            return jsonify({'success': False, 'error': 'Listing not found'}), 404
        
        if listing['owner_id'] != user_id:
            return jsonify({'success': False, 'error': 'Only the owner can mark rentals as completed'}), 403
        
        # Check if currently booked
        if listing['status'] != 'booked':
            return jsonify({'success': False, 'error': 'Only booked rentals can be marked as completed'}), 400
        
        # Update status to completed
        success = update_equipment_status(listing_id, 'completed')
        
        if success:
            return jsonify({'success': True, 'message': 'Rental marked as completed successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update rental status. Please try again.'}), 500
            
    except Exception as e:
        print(f"Complete rental error: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred. Please try again.'}), 500
