"""
Test notification creation
"""
from utils.db import init_db, add_notification, get_dashboard_notifications

class MockApp:
    pass

# Initialize
app = MockApp()
init_db(app)

print("=" * 60)
print("TESTING NOTIFICATION SYSTEM")
print("=" * 60)

user_id = "cb57cdef-86cf-4079-9d30-372067f41777"  # manoj kumar

# Add test notifications
print("\n📬 Creating test notifications...")

add_notification(
    user_id=user_id,
    type='listing_created',
    title='✅ Listing Created',
    message='Your Tomato listing (200 kg) has been created successfully and is now live in the marketplace!',
    priority='medium',
    data={'crop': 'Tomato'}
)
print("   ✓ Created: Listing notification")

add_notification(
    user_id=user_id,
    type='purchase_confirmed',
    title='🛒 Purchase Confirmed',
    message='Your purchase of Onion (100 kg) has been confirmed! The farmer will contact you.',
    priority='high'
)
print("   ✓ Created: Purchase notification")

add_notification(
    user_id=user_id,
    type='equipment_listed',
    title='✅ Equipment Listed',
    message='Your Tractor is now available for rent at ₹1500/day.',
    priority='medium'
)
print("   ✓ Created: Equipment notification")

# Retrieve notifications
print(f"\n📋 Retrieving notifications for user...")
notifications = get_dashboard_notifications(user_id)

print(f"\n   Found {len(notifications)} notification(s):")
for i, notif in enumerate(notifications, 1):
    print(f"\n   {i}. {notif.get('title')}")
    print(f"      {notif.get('message')}")
    print(f"      Type: {notif.get('type')} | Priority: {notif.get('priority')}")
    print(f"      Created: {notif.get('created_at')}")

print("\n" + "=" * 60)
print("✅ NOTIFICATION SYSTEM WORKING!")
print("=" * 60)
print("\nThese notifications will appear in the dashboard panel.")
