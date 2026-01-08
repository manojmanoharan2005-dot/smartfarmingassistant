# Equipment Sharing Marketplace - Technical Documentation

## Overview
Real-time equipment rental platform enabling farmers to rent out and book farming equipment with live market-based pricing and atomic booking to prevent double-booking.

---

## Tech Stack
- **Backend**: Flask (Python)
- **Database**: MongoDB Atlas (Cloud) with file-based fallback
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Authentication**: Session-based login

---

## Database Design

### Collection: `equipment_base_prices`
Stores live market rental rates for different equipment types.

```json
{
  "equipment_name": "Tractor",
  "location": "Tamil Nadu",
  "avg_rent_per_day": 1500
}
```

### Collection: `equipment_listings`
Stores equipment rental listings with booking information.

```json
{
  "_id": "ObjectId",
  "owner_id": "user_id",
  "owner_name": "Farmer Name",
  "owner_phone": "1234567890",
  "equipment_name": "Tractor",
  "district": "Dindigul",
  "state": "Tamil Nadu",
  "location": "Dindigul, Tamil Nadu",
  "owner_rent": 1500,
  "recommended_rent": 1500,
  "min_rent": 1275,
  "max_rent": 1725,
  "description": "Well maintained tractor",
  "available_from": "2026-01-10",
  "available_to": "2026-01-31",
  "status": "available",
  "renter_id": null,
  "renter_name": null,
  "renter_phone": null,
  "from_date": null,
  "to_date": null,
  "created_at": "2026-01-08T10:00:00",
  "booked_at": null,
  "completed_at": null
}
```

**Status Values:**
- `available` - Equipment is listed and can be booked
- `booked` - Equipment has been rented (removed from marketplace)
- `completed` - Rental period finished

---

## Business Logic

### 1. Live Rent Calculation
```python
recommended_rent = avg_rent_per_day
min_rent = recommended_rent * 0.85  # -15%
max_rent = recommended_rent * 1.15  # +15%
```

### 2. Rent Validation Rules
- Owner can only set rent within ±15% of recommended market rent
- Frontend validation with visual feedback
- Backend validation prevents manipulation
- If validation fails, listing is rejected

### 3. Marketplace Display Rules
- **Only** equipment with `status = "available"` appears
- Booked equipment is automatically hidden
- Completed rentals are hidden from marketplace
- Users cannot book their own equipment

### 4. Atomic Booking (Prevents Double-Booking)
**MongoDB Atomic Update:**
```python
db.equipment_listings.update_one(
    {
        '_id': listing_id,
        'status': 'available'  # CRITICAL: Only update if available
    },
    {
        '$set': {
            'status': 'booked',
            'renter_id': renter_id,
            'from_date': from_date,
            'to_date': to_date
        }
    }
)
```

**How it prevents double-booking:**
- MongoDB checks status is 'available' before updating
- If two renters try simultaneously, only ONE succeeds
- Second renter gets "Equipment no longer available" error
- No race conditions or duplicate bookings

---

## API Endpoints

### Owner Side

#### 1. List Equipment Form
```
GET /equipment-sharing/list-equipment
```
- Shows equipment listing form
- Displays user's existing listings
- Equipment types: Tractor, Harvester, Plough, etc.

#### 2. Get Live Rent
```
POST /equipment-sharing/api/get-live-rent
Body: { equipment: "Tractor", location: "Dindigul" }
Response: {
  recommended_rent: 1500,
  min_rent: 1275,
  max_rent: 1725,
  location: "Tamil Nadu"
}
```

#### 3. Add Equipment
```
POST /equipment-sharing/add-equipment
Form Data:
- equipment_name
- district
- state
- owner_rent
- description
- available_from
- available_to
```

**Backend Validation:**
```python
if owner_rent < min_allowed or owner_rent > max_allowed:
    return error("Rent must be within ±15% of ₹{recommended}")
```

#### 4. Complete Rental
```
POST /equipment-sharing/complete-rental/<listing_id>
```
- Changes status to 'completed'
- Only owner can complete
- Removes equipment from marketplace

---

### Renter Side

#### 1. Browse Marketplace
```
GET /equipment-sharing/marketplace?equipment=Tractor&state=Tamil Nadu&sort=price_low
```
- Shows ONLY available equipment
- Filters: equipment type, state, district
- Sorting: recent, price_low, price_high

#### 2. Book Equipment
```
POST /equipment-sharing/api/book-equipment
Body: {
  listing_id: "abc123",
  from_date: "2026-01-10T00:00:00Z",
  to_date: "2026-01-15T00:00:00Z",
  renter_name: "John Farmer",
  renter_phone: "9876543210"
}
```

**Validations:**
- End date > Start date
- Start date cannot be in past
- Phone number must be 10 digits
- Equipment must be available
- Cannot book own equipment

**Atomic Update Ensures:**
- Equipment status changes to 'booked' atomically
- Renter info saved
- Equipment disappears from marketplace
- Other renters see "No longer available"

---

## Frontend Implementation

### Equipment Listing Form
**Key Features:**
1. Dynamic state/district dropdowns
2. Live rent fetching via AJAX
3. Auto-fill recommended rent
4. Visual validation (red/green border)
5. Client-side rent range checking

**JavaScript Flow:**
```javascript
1. User selects equipment + district
2. Fetch live rent from API
3. Display recommended rent + allowed range
4. Pre-fill rent input with recommended value
5. Validate on input change
6. Show red border if outside range
7. Block form submission if invalid
```

### Marketplace
**Key Features:**
1. Filter by equipment, state, sort order
2. Responsive card grid layout
3. Modal booking form
4. Date validation (min date = today)
5. Real-time booking status

**Booking Flow:**
```javascript
1. User clicks "Book Now"
2. Modal opens with equipment details
3. User fills dates + contact info
4. Validate dates (to > from, from >= today)
5. Submit to API with atomic update
6. Show success/error message
7. Reload page to update marketplace
```

---

## Database Functions (utils/db.py)

### 1. `get_live_equipment_rent(equipment, location)`
Returns live market rent with calculated ranges.

### 2. `create_equipment_listing(listing_data)`
Creates new listing with status='available'.

### 3. `get_available_equipment(filters, sort_by)`
Returns ONLY equipment where status='available'.

### 4. `book_equipment_atomic(listing_id, booking_data)`
**CRITICAL FUNCTION** - Prevents double-booking
- Uses MongoDB atomic update
- Returns (success, message)
- Only updates if status is 'available'

### 5. `complete_equipment_rental(listing_id)`
Changes status to 'completed', removes from marketplace.

### 6. `get_user_equipment_listings(user_id)`
Returns all listings created by user (all statuses).

### 7. `get_user_bookings(user_id)`
Returns all equipment booked by user.

---

## User Journey

### Owner Journey:
1. Navigate to "List Equipment"
2. Select equipment type and location
3. System shows live market rent
4. Set rent within allowed range (±15%)
5. Add availability dates and description
6. Submit listing
7. Equipment appears in marketplace
8. When rented, owner sees renter contact info
9. After rental, mark as completed

### Renter Journey:
1. Browse marketplace
2. Filter by equipment type/location
3. See available equipment with prices
4. Click "Book Now" on desired equipment
5. Select rental dates
6. Enter contact information
7. Submit booking
8. Equipment disappears from marketplace
9. Owner contacts renter for pickup

---

## Key Features for Viva/Project Explanation

### 1. **Live Market Pricing**
- Uses real market data from `equipment_base_prices`
- Auto-calculates ±15% range
- Prevents unrealistic pricing
- Dynamic based on location

### 2. **Atomic Booking (Race Condition Prevention)**
- MongoDB's `update_one` with condition
- Only ONE user can book at a time
- Prevents overselling/double-booking
- Industry-standard concurrency control

### 3. **Status-Based Visibility**
- Available → shown in marketplace
- Booked → hidden automatically
- Completed → hidden, shows in history
- Real-time updates

### 4. **Input Validation (Multi-Layer)**
- Frontend: Visual feedback, range checking
- Backend: Price range, date validation
- Database: Atomic updates, constraints

### 5. **User Experience**
- Responsive design (mobile-friendly)
- Real-time rent fetching
- Clear status indicators
- Simple booking flow

---

## Testing Scenarios

### Test 1: Normal Booking Flow
1. Owner lists Tractor at ₹1500/day
2. Renter searches for Tractors
3. Renter books from Jan 10-15
4. Booking succeeds
5. Tractor disappears from marketplace
6. Owner sees booking details

**Expected:** ✅ Success

### Test 2: Double Booking Prevention
1. Two renters view same equipment
2. Both click "Book Now" simultaneously
3. Both submit booking forms
4. **First submission:** Success
5. **Second submission:** "Equipment no longer available"

**Expected:** ✅ Only one booking succeeds

### Test 3: Price Validation
1. Owner tries to set ₹500 when market is ₹1500
2. Min allowed: ₹1275, Max: ₹1725
3. Frontend shows red border
4. Backend rejects submission

**Expected:** ✅ Rejected

### Test 4: Self-Booking Prevention
1. Owner views their own equipment in marketplace
2. Button shows "Your Own Equipment" (disabled)

**Expected:** ✅ Cannot book own equipment

---

## MongoDB vs File-Based Storage

### MongoDB (Production - Recommended):
- Cloud-based (MongoDB Atlas)
- Atomic updates for booking
- Scales to thousands of users
- Real-time performance
- Automatic indexing

### File-Based (Development Fallback):
- JSON files in `/data` folder
- Works without internet
- Good for demo/testing
- Limited concurrency protection
- Slower performance

**Code automatically uses MongoDB if available, falls back to files.**

---

## Deployment Considerations

### Environment Variables (.env):
```
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/smartfarming
```

### Data Files:
- `equipment_base_prices.json` - Market rental rates
- `equipment_listings.json` - All equipment listings

### Requirements:
```
Flask==2.3.0
pymongo==4.5.0
python-dotenv==1.0.0
```

---

## Code Architecture

```
smartfarmingassitant/
├── controllers/
│   └── equipment_sharing_routes.py  # All routes
├── utils/
│   └── db.py  # Database functions (lines 1287-1541)
├── templates/
│   ├── equipment_list_form.html     # Owner side
│   └── equipment_marketplace.html   # Renter side
├── data/
│   ├── equipment_base_prices.json   # Market rates
│   └── equipment_listings.json      # Listings
└── app.py  # Blueprint registration
```

---

## Advantages Over Manual Rental

### Before (Manual):
- No pricing guidance
- Phone calls/WhatsApp coordination
- No availability tracking
- Risk of double-booking
- No rental history

### After (Our System):
- Live market-based pricing
- Centralized marketplace
- Real-time availability
- Prevents double-booking
- Complete rental history
- Location-based search
- Automated status management

---

## Future Enhancements

1. **Payment Integration** - Online payment gateway
2. **Rating System** - Rate owners and equipment
3. **Image Upload** - Photos of equipment
4. **GPS Integration** - Equipment location on map
5. **Automatic Completion** - Auto-complete after end date
6. **Notifications** - SMS/Email for bookings
7. **Insurance** - Equipment damage coverage
8. **Delivery Option** - Owner delivers equipment

---

## Conclusion

This Equipment Sharing Marketplace is a production-ready module with:
- ✅ Live market pricing
- ✅ Atomic booking (no double-booking)
- ✅ Real-time availability
- ✅ MongoDB Atlas integration
- ✅ Responsive UI
- ✅ Complete validation
- ✅ Easy to explain in viva
- ✅ Scalable architecture

**Perfect for final year project demonstration!**
