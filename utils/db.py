from datetime import datetime
import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Atlas connection string from environment variable
MONGODB_URI = os.getenv('MONGODB_URI')

# Local file-based storage directory and file paths (used when MongoDB is not available)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DATA_DIR = os.path.abspath(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, 'users.json')
CROPS_FILE = os.path.join(DATA_DIR, 'crops.json')
FERTILIZERS_FILE = os.path.join(DATA_DIR, 'fertilizers.json')
DISEASES_FILE = os.path.join(DATA_DIR, 'diseases.json')
GROWING_FILE = os.path.join(DATA_DIR, 'growing_activities.json')
EQUIPMENT_FILE = os.path.join(DATA_DIR, 'equipment.json')
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, 'notifications.json')
EXPENSES_FILE = os.path.join(DATA_DIR, 'expenses.json')

client = None
db = None

def init_db(app):
    global client, db
    
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Initialize JSON files if they don't exist
    for file_path in [USERS_FILE, CROPS_FILE, FERTILIZERS_FILE, DISEASES_FILE, GROWING_FILE, EQUIPMENT_FILE, NOTIFICATIONS_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                if file_path in [EQUIPMENT_FILE, NOTIFICATIONS_FILE]:
                    json.dump([], f)
                else:
                    json.dump({}, f)
    
    print("[SUCCESS] File-based database initialized successfully!")
    print("[INFO] Data will be stored in the 'data' directory")
    
    # Try MongoDB Atlas connection as backup (only if URI is configured)
    if MONGODB_URI:
        try:
            print("[INFO] Attempting MongoDB Atlas connection...")
            client = MongoClient(MONGODB_URI, 
                               serverSelectionTimeoutMS=30000,
                               connectTimeoutMS=30000,
                               socketTimeoutMS=30000,
                               retryWrites=False)
            
            # Use myVirtualDatabase database
            db = client.myVirtualDatabase
            # Test the connection
            client.admin.command('ping')
            print("[SUCCESS] Successfully connected to MongoDB Atlas!")
            print(f"[INFO] Using database: myVirtualDatabase")
            
            # Create indexes for better performance (if supported)
            try:
                db.users.create_index("email", unique=True)
                print("[INFO] Database indexes created successfully")
            except Exception as e:
                print(f"[WARNING] Index creation note: {e}")
                print("   (This is normal for Atlas SQL interface)")
                
        except Exception as e:
            print(f"[ERROR] MongoDB connection failed: {e}")
            print("[WARNING] Common issues:")
            print("   1. Check if your IP address is whitelisted in MongoDB Atlas")
            print("   2. Verify network connectivity and firewall settings")
            print("   3. Ensure Atlas SQL interface is enabled")
            print("[INFO] Using file-based database for development")
            db = MockDatabase()
    else:
        print("[INFO] MongoDB disabled - using file-based database")
        db = MockDatabase()

class MockDatabase:
    """Enhanced Mock database for development when MongoDB is not available"""
    def __init__(self):
        self.users_data = {}
        self.crops_data = []
        self.fertilizers_data = []
        self.diseases_data = []
        print("[INFO] Mock database initialized with enhanced features")
    
    @property
    def users(self):
        return MockCollection('users', self.users_data, is_dict=True)
    
    @property 
    def crops(self):
        return MockCollection('crops', self.crops_data)
        
    @property
    def fertilizers(self):
        return MockCollection('fertilizers', self.fertilizers_data)
        
    @property
    def diseases(self):
        return MockCollection('diseases', self.diseases_data)

class MockCollection:
    def __init__(self, name, data_store, is_dict=False):
        self.name = name
        self.data_store = data_store
        self.is_dict = is_dict
        
    def find_one(self, query):
        if self.is_dict and 'email' in query:
            return self.data_store.get(query['email'])
        elif '_id' in query:
            for item in self.data_store:
                if item.get('_id') == query['_id']:
                    return item
        return None
    
    def insert_one(self, data):
        import uuid
        mock_id = str(uuid.uuid4())
        data['_id'] = mock_id
        
        if self.is_dict and 'email' in data:
            self.data_store[data['email']] = data
        else:
            self.data_store.append(data)
            
        return type('MockResult', (), {'inserted_id': mock_id})()
    
    def find(self, query):
        if 'user_id' in query:
            return [item for item in self.data_store if item.get('user_id') == query['user_id']]
        return list(self.data_store) if not self.is_dict else list(self.data_store.values())
    
    def delete_one(self, query):
        if '_id' in query:
            self.data_store = [item for item in self.data_store if item.get('_id') != query['_id']]
            return type('MockResult', (), {'deleted_count': 1})()
        return type('MockResult', (), {'deleted_count': 0})()
    
    def create_index(self, field, unique=False):
        print(f"Mock index created for {field} (unique: {unique})")

def get_db():
    return db

# User model functions
def create_user(name, email, password, phone, state, district):
    users = db.users
    user_data = {
        'name': name,
        'email': email,
        'password': password,
        'phone': phone,
        'state': state,
        'district': district,
        'created_at': datetime.utcnow(),
        'saved_crops': [],
        'saved_fertilizers': [],
        'disease_history': []
    }
    result = users.insert_one(user_data)
    print(f"👤 User created: {name} ({email})")
    return result

def find_user_by_email(email):
    if hasattr(db, 'users'):
        users = db.users
        user = users.find_one({'email': email})
    else:
        # Handle mock database
        user = db.users.find_one({'email': email}) if db else None
    
    if user:
        print(f"🔍 User found: {email}")
    return user

def find_user_by_phone(phone):
    """Find user by phone number"""
    if hasattr(db, 'users'):
        users = db.users
        # Get all users and search for phone
        all_users = users.find({})
        for user in all_users:
            if user.get('phone') == phone:
                print(f"🔍 User found with phone: {phone}")
                return user
    return None

def update_user_password(email, new_password):
    """Update user password by email"""
    try:
        # Load users from file
        with open(USERS_FILE, 'r') as f:
            users_db = json.load(f)
        
        # Find and update user
        for user_id, user in users_db.items():
            if user.get('email') == email:
                user['password'] = new_password
                # Save back to file
                with open(USERS_FILE, 'w') as f:
                    json.dump(users_db, f, indent=2, default=str)
                print(f"[SUCCESS] Password updated for user: {email}")
                return True
        
        print(f"[WARNING] User not found: {email}")
        return False
    except Exception as e:
        print(f"[ERROR] Error updating password: {e}")
        return False

def find_user_by_id(user_id):
    try:
        if hasattr(db, 'users') and db:
            users = db.users
            
            # Try with ObjectId first (for MongoDB)
            try:
                from bson.objectid import ObjectId
                user = users.find_one(
                    {'_id': ObjectId(user_id)}, 
                    {'password': 0}  # Exclude password field
                )
                if user:
                    return user
            except:
                pass
            
            # Try with string ID (for file-based storage)
            user = users.find_one({'_id': user_id})
            if user:
                # Remove password from result
                user_copy = user.copy()
                user_copy.pop('password', None)
                return user_copy
                
    except Exception as e:
        print(f"Error fetching user by ID: {e}")
    
    # If user not found, return None
    return None

# Alias for backward compatibility
get_user_by_id = find_user_by_id

# Mock functions for development
def save_crop_recommendation(user_id, crop_data, timeline_data):
    print(f"🌱 Crop recommendation saved for user {user_id}: {crop_data['crop_name']}")
    return type('MockResult', (), {'inserted_id': 'mock_crop_id'})()

def get_user_crops(user_id):
    # Return some mock data for testing
    return [
        {
            '_id': 'crop1',
            'crop_name': 'Rice',
            'probability': 0.89,
            'sowing_date': '2024-01-15',
            'status': 'monitoring'
        }
    ]

def delete_crop(crop_id):
    print(f"🗑️ Crop deleted: {crop_id}")
    return type('MockResult', (), {'deleted_count': 1})()

def save_fertilizer_recommendation(user_id, fertilizer_data):
    """Save fertilizer recommendation to file"""
    import uuid
    try:
        # Load existing fertilizers
        with open(FERTILIZERS_FILE, 'r') as f:
            fertilizer_db = json.load(f)
        
        # Generate unique ID
        fertilizer_id = str(uuid.uuid4())
        fertilizer_data['_id'] = fertilizer_id
        fertilizer_data['user_id'] = user_id
        fertilizer_data['saved_at'] = datetime.utcnow().isoformat()
        
        # Save fertilizer
        if user_id not in fertilizer_db:
            fertilizer_db[user_id] = []
        
        fertilizer_db[user_id].append(fertilizer_data)
        
        # Write back to file
        with open(FERTILIZERS_FILE, 'w') as f:
            json.dump(fertilizer_db, f, indent=2)
        
        print(f"🧪 Fertilizer recommendation saved for user {user_id}: {fertilizer_data.get('name')}")
        return type('MockResult', (), {'inserted_id': fertilizer_id})()
    except Exception as e:
        print(f"Error saving fertilizer: {e}")
        return None

def get_user_fertilizers(user_id):
    """Get user's saved fertilizers from file"""
    import uuid
    try:
        with open(FERTILIZERS_FILE, 'r') as f:
            fertilizer_db = json.load(f)
        
        # Get user's fertilizers
        user_fertilizers = fertilizer_db.get(user_id, [])
        
        # Add _id to fertilizers that don't have one
        needs_save = False
        for fert in user_fertilizers:
            if '_id' not in fert:
                fert['_id'] = str(uuid.uuid4())
                needs_save = True
        
        # Save back if we added any IDs
        if needs_save:
            fertilizer_db[user_id] = user_fertilizers
            with open(FERTILIZERS_FILE, 'w') as f:
                json.dump(fertilizer_db, f, indent=2)
        
        return user_fertilizers
    except Exception as e:
        print(f"Error loading fertilizers: {e}")
        return []

def delete_fertilizer_recommendation(fertilizer_id, user_id):
    """Delete a fertilizer recommendation from file"""
    try:
        # Load existing fertilizers
        with open(FERTILIZERS_FILE, 'r') as f:
            fertilizer_db = json.load(f)
        
        # Get user's fertilizers
        user_fertilizers = fertilizer_db.get(user_id, [])
        
        # Find and remove the fertilizer
        initial_count = len(user_fertilizers)
        user_fertilizers = [f for f in user_fertilizers if f.get('_id') != fertilizer_id]
        
        if len(user_fertilizers) < initial_count:
            # Fertilizer was found and removed
            fertilizer_db[user_id] = user_fertilizers
            
            # Write back to file
            with open(FERTILIZERS_FILE, 'w') as f:
                json.dump(fertilizer_db, f, indent=2)
            
            print(f"[SUCCESS] Successfully deleted fertilizer {fertilizer_id} for user {user_id}")
            return True
        else:
            print(f"[WARNING] Fertilizer {fertilizer_id} not found for user {user_id}")
            return False
            
    except Exception as e:
        print(f"Error deleting fertilizer: {e}")
        return False

def save_disease_detection(user_id, disease_data):
    print(f"🦠 Disease detection saved for user {user_id}: {disease_data['disease_name']}")
    return type('MockResult', (), {'inserted_id': 'mock_disease_id'})()

def get_user_diseases(user_id):
    # Return some mock data for testing
    return [
        {
            '_id': 'disease1',
            'disease_name': 'Tomato Blight',
            'plant_type': 'Tomato',
            'confidence': 0.87,
            'detected_at': datetime.utcnow()
        }
    ]

def save_growing_activity(activity_data):
    """Save a growing activity to database"""
    import uuid
    try:
        # Load existing activities
        with open(GROWING_FILE, 'r') as f:
            growing_data = json.load(f)
        
        # Generate unique ID
        activity_id = str(uuid.uuid4())
        activity_data['_id'] = activity_id
        
        # Save activity
        user_id = activity_data.get('user_id')
        if user_id not in growing_data:
            growing_data[user_id] = []
        
        growing_data[user_id].append(activity_data)
        
        # Write back to file
        with open(GROWING_FILE, 'w') as f:
            json.dump(growing_data, f, indent=2)
        
        print(f"🌱 Growing activity saved: {activity_data.get('crop_display_name')} [ID: {activity_id}]")
        return type('MockResult', (), {'inserted_id': activity_id})()
    except Exception as e:
        print(f"Error saving growing activity: {e}")
        return None

def get_user_growing_activities(user_id, status='active'):
    """Get user's growing activities"""
    import uuid
    try:
        with open(GROWING_FILE, 'r') as f:
            growing_data = json.load(f)
        
        # Get user's activities
        user_activities = growing_data.get(user_id, [])
        
        # Add _id to activities that don't have one
        needs_save = False
        for activity in user_activities:
            if '_id' not in activity:
                activity['_id'] = str(uuid.uuid4())
                needs_save = True
        
        # Save back if we added any IDs
        if needs_save:
            growing_data[user_id] = user_activities
            with open(GROWING_FILE, 'w') as f:
                json.dump(growing_data, f, indent=2)
        
        # Filter by status if specified
        if status:
            user_activities = [a for a in user_activities if a.get('status') == status]
        
        return user_activities
    except Exception as e:
        print(f"Error loading growing activities: {e}")
        return []

def update_growing_activity(activity_id, user_id, update_data):
    """Update growing activity with new data (stage, notes, tasks)"""
    try:
        print(f"💾 DB: Updating activity {activity_id} for user {user_id}")
        print(f"💾 DB: Update data: {update_data}")
        
        # Load existing activities
        with open(GROWING_FILE, 'r') as f:
            growing_data = json.load(f)
        
        print(f"💾 DB: Loaded data for {len(growing_data)} users")
        
        # Get user's activities
        user_activities = growing_data.get(user_id, [])
        print(f"💾 DB: User has {len(user_activities)} activities")
        
        # Find and update the activity
        activity_found = False
        for i, activity in enumerate(user_activities):
            print(f"💾 DB: Checking activity {i}: {activity.get('_id')} == {activity_id}?")
            if activity.get('_id') == activity_id or activity.get('id') == activity_id:
                print(f"💾 DB: Match found! Updating...")
                # Update the activity fields
                if 'current_stage' in update_data:
                    print(f"💾 DB: Updating stage: {activity.get('current_stage')} -> {update_data['current_stage']}")
                    user_activities[i]['current_stage'] = update_data['current_stage']
                if 'progress' in update_data:
                    print(f"💾 DB: Updating progress: {activity.get('progress')} -> {update_data['progress']}")
                    user_activities[i]['progress'] = update_data['progress']
                if 'notes' in update_data:
                    print(f"💾 DB: Updating notes")
                    user_activities[i]['notes'] = update_data['notes']
                if 'completed_tasks' in update_data:
                    print(f"💾 DB: Updating tasks")
                    user_activities[i]['completed_tasks'] = update_data['completed_tasks']
                
                user_activities[i]['updated_at'] = datetime.now().isoformat()
                activity_found = True
                break
        
        if activity_found:
            growing_data[user_id] = user_activities
            
            # Write back to file
            with open(GROWING_FILE, 'w') as f:
                json.dump(growing_data, f, indent=2)
            
            print(f"[SUCCESS] Successfully updated activity {activity_id} for user {user_id}")
            print(f"[INFO] DB: File saved to {GROWING_FILE}")
            return True
        else:
            print(f"⚠️ Activity {activity_id} not found for user {user_id}")
            return False
            
    except Exception as e:
        print(f"Error updating activity: {e}")
        import traceback
        traceback.print_exc()
        return False

def delete_growing_activity(activity_id, user_id):
    """Delete a growing activity"""
    try:
        # Load existing activities
        with open(GROWING_FILE, 'r') as f:
            growing_data = json.load(f)
        
        # Get user's activities
        user_activities = growing_data.get(user_id, [])
        
        # Find and remove the activity
        initial_count = len(user_activities)
        user_activities = [a for a in user_activities if a.get('_id') != activity_id]
        
        if len(user_activities) < initial_count:
            # Activity was found and removed
            growing_data[user_id] = user_activities
            
            # Write back to file
            with open(GROWING_FILE, 'w') as f:
                json.dump(growing_data, f, indent=2)
            
            print(f"[SUCCESS] Successfully deleted activity {activity_id} for user {user_id}")
            return True
        else:
            print(f"⚠️ Activity {activity_id} not found for user {user_id}")
            return False
            
    except Exception as e:
        print(f"Error deleting activity: {e}")
        return False

def get_dashboard_notifications(user_id):
    """Get notifications for dashboard"""
    from datetime import datetime, timedelta
    notifications = []
    
    # Get user's last read timestamp
    user = find_user_by_id(user_id)
    last_read_at = datetime.min
    if user and 'last_notification_read_at' in user:
        if isinstance(user['last_notification_read_at'], str):
            last_read_at = datetime.fromisoformat(user['last_notification_read_at'])
        else:
            last_read_at = user['last_notification_read_at']
    
    # Get active growing activities
    activities = get_user_growing_activities(user_id)
    
    for activity in activities:
        # Check for upcoming tasks (only if tasks have 'week' key - old structure)
        if 'tasks' in activity and activity['tasks']:
            # Check if it's the old task structure with 'week' key
            if isinstance(activity['tasks'], list) and len(activity['tasks']) > 0:
                first_task = activity['tasks'][0]
                if isinstance(first_task, dict) and 'week' in first_task:
                    # Old structure - process weekly tasks
                    start_date = datetime.fromisoformat(activity['created_at'])
                    days_passed = (datetime.now() - start_date).days
                    weeks_passed = days_passed // 7
                    
                    # Find pending tasks for current week
                    for task in activity['tasks']:
                        if task.get('week') == weeks_passed + 1:
                            # Deterministic timestamp: Start of the current week (approx)
                            notif_time = start_date + timedelta(weeks=weeks_passed)
                            if notif_time > last_read_at:
                                notifications.append({
                                    'type': 'task',
                                    'crop': activity.get('crop_display_name', activity.get('crop', 'Unknown')),
                                    'message': f"Week {task['week']} task: {task['task']}",
                                    'priority': 'high',
                                    'created_at': notif_time.isoformat(),
                                    'time_ago': 'This week'
                                })
                elif isinstance(first_task, dict) and 'date' in first_task:
                    # New structure - process date-based tasks
                    for task in activity['tasks']:
                        try:
                            task_date = datetime.strptime(task['date'], '%Y-%m-%d')
                        except:
                            try:
                                task_date = datetime.fromisoformat(task['date'])
                            except:
                                continue

                        days_until = (task_date.date() - datetime.now().date()).days
                        
                        # Notify for tasks within next 3 days
                        if 0 <= days_until <= 3 and not task.get('completed', False):
                            # Deterministic timestamp: 6 AM of the task date (or today if overdue/today)
                            # Actually, we want it to show up TODAY if it is due TODAY.
                            # So logical timestamp is: max(task_date - 3 days, today 00:00)?
                            # Simplest: notification timestamp is the start of today for this specific alert
                            # But if I read it at 8am, I don't want to see it at 9am.
                            # So consistent creation time = today 00:00:00.
                            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                            
                            # However, if the task was due yesterday (overdue), distinct alert?
                            # Let's use today_start. If user cleared after today_start, they won't see it.
                            if today_start > last_read_at:
                                notifications.append({
                                    'type': 'task',
                                    'crop': activity.get('crop_display_name', activity.get('crop', 'Unknown')),
                                    'message': f"{task['type']} scheduled for {task_date.strftime('%b %d')}",
                                    'priority': 'high' if days_until == 0 else 'medium',
                                    'created_at': today_start.isoformat(), 
                                    'time_ago': 'Today' if days_until == 0 else f'In {days_until} days'
                                })
                        
                        # Also check for OVERDUE tasks
                        if days_until < 0 and not task.get('completed', False) and days_until > -7:
                             today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                             if today_start > last_read_at:
                                notifications.append({
                                    'type': 'warning',
                                    'crop': activity.get('crop_display_name', activity.get('crop', 'Unknown')),
                                    'message': f"Overdue: {task['type']} was due on {task_date.strftime('%b %d')}",
                                    'priority': 'high',
                                    'created_at': today_start.isoformat(),
                                    'time_ago': f'{abs(days_until)} days ago'
                                })

        
        # Check if harvest is near (within 7 days)
        if 'harvest_date' in activity or 'expected_harvest_date' in activity:
            harvest_date_str = activity.get('expected_harvest_date') or activity.get('harvest_date')
            if harvest_date_str:
                try:
                    harvest_date = datetime.fromisoformat(harvest_date_str) if 'T' in harvest_date_str else datetime.strptime(harvest_date_str, '%Y-%m-%d')
                    days_to_harvest = (harvest_date - datetime.now()).days
                    
                    if 0 <= days_to_harvest <= 7:
                         today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                         if today_start > last_read_at:
                            notifications.append({
                                'type': 'harvest',
                                'crop': activity.get('crop_display_name', activity.get('crop', 'Unknown')),
                                'message': f"Harvest ready in {days_to_harvest} days!",
                                'priority': 'high',
                                'created_at': today_start.isoformat(),
                                'time_ago': f'In {days_to_harvest} days'
                            })
                except Exception as e:
                    print(f"Error parsing harvest date: {e}")
    
    # Add persistent notifications
    persistent = get_persistent_notifications(user_id)
    # Filter persistent ones that are not read
    unread_persistent = [n for n in persistent if not n.get('read', False)]
    notifications.extend(unread_persistent)
    
    # Sort by date
    notifications.sort(key=lambda x: x['created_at'], reverse=True)
    
    return notifications

def mark_user_notifications_read(user_id):
    """Mark all notifications as read for a user"""
    try:
        # 1. Update persistent notifications
        if os.path.exists(NOTIFICATIONS_FILE):
             with open(NOTIFICATIONS_FILE, 'r') as f:
                all_notifs = json.load(f)
             
             updated = False
             for n in all_notifs:
                 if n.get('user_id') == str(user_id) and not n.get('read', False):
                     n['read'] = True
                     updated = True
             
             if updated:
                 with open(NOTIFICATIONS_FILE, 'w') as f:
                    json.dump(all_notifs, f, indent=2)

        # 2. Update user's last_notification_read_at timestamp
        users = db.users
        timestamp = datetime.now().isoformat()
        
        if hasattr(users, 'update_one'):
            # MongoDB
            users.update_one(
                {'_id': user_id} if not isinstance(user_id, str) else {'email': user_id}, 
                {'$set': {'last_notification_read_at': timestamp}}
            )
        else:
            # File-based DB (MockCollection)
            user_found = False
            # If using dict store (email keys)
            if hasattr(users, 'data_store') and isinstance(users.data_store, dict):
                 for email, u in users.data_store.items():
                     if str(u.get('_id')) == str(user_id) or u.get('email') == str(user_id):
                         u['last_notification_read_at'] = timestamp
                         user_found = True
                         break
            # If using list store (unlikely for users but possible)
            elif hasattr(users, 'data_store') and isinstance(users.data_store, list):
                for u in users.data_store:
                     if str(u.get('_id')) == str(user_id) or u.get('email') == str(user_id):
                         u['last_notification_read_at'] = timestamp
                         user_found = True
                         break
            
            if user_found and os.path.exists(USERS_FILE):
                with open(USERS_FILE, 'w') as f:
                    # Determine what to save based on data_store type
                    data_to_save = users.data_store
                    json.dump(data_to_save, f, indent=2, default=str)

        return True

        return True
    except Exception as e:
        print(f"Error marking notifications read: {e}")
        return False
        
def add_notification(user_id, type, message, priority='medium', title=None, data=None):
    """Save a user notification to file"""
    try:
        notifications = []
        if os.path.exists(NOTIFICATIONS_FILE):
            with open(NOTIFICATIONS_FILE, 'r') as f:
                notifications = json.load(f)
        
        # Determine title if not provided
        if not title:
            if type == 'equipment' or type == 'rental_request':
                title = 'Equipment Rental'
            elif type == 'system':
                title = 'System Alert'
            else:
                title = 'Notification'

        new_notif = {
            'id': str(datetime.now().timestamp()),
            'user_id': str(user_id),
            'type': type,
            'title': title,
            'message': message,
            'priority': priority,
            'created_at': datetime.now().isoformat(),
            'read': False,
            'data': data or {}
        }
        notifications.append(new_notif)
        
        with open(NOTIFICATIONS_FILE, 'w') as f:
            json.dump(notifications, f, indent=2)
        return True
    except Exception as e:
        print(f"Error adding notification: {e}")
        return False
        
def delete_notification(notification_id):
    """Delete a notification by ID"""
    try:
        if not os.path.exists(NOTIFICATIONS_FILE):
            return False
            
        with open(NOTIFICATIONS_FILE, 'r') as f:
            notifications = json.load(f)
            
        initial_len = len(notifications)
        notifications = [n for n in notifications if n.get('id') != notification_id]
        
        if len(notifications) < initial_len:
            with open(NOTIFICATIONS_FILE, 'w') as f:
                json.dump(notifications, f, indent=2)
            return True
        return False
    except Exception as e:
        print(f"Error deleting notification: {e}")
        return False

def update_equipment(equipment_id, update_data):
    """Update generic equipment fields"""
    try:
        with open(EQUIPMENT_FILE, 'r') as f:
            equipment = json.load(f)
        
        updated = False
        for item in equipment:
            if item.get('_id') == equipment_id:
                item.update(update_data)
                item['updated_at'] = datetime.now().isoformat()
                updated = True
                break
        
        if updated:
            with open(EQUIPMENT_FILE, 'w') as f:
                json.dump(equipment, f, indent=2)
            return True
        return False
    except Exception as e:
        print(f"Error updating equipment: {e}")
        return False
    except Exception as e:
        print(f"Error adding notification: {e}")
        return False

def get_persistent_notifications(user_id):
    """Retrieve saved notifications for a user"""
    try:
        if not os.path.exists(NOTIFICATIONS_FILE):
            return []
        with open(NOTIFICATIONS_FILE, 'r') as f:
            all_notifs = json.load(f)
            return [n for n in all_notifs if n.get('user_id') == str(user_id)]
    except Exception as e:
        print(f"Error loading notifications: {e}")
        return []

def get_all_equipment():
    """Get all listed equipment"""
    try:
        if not os.path.exists(EQUIPMENT_FILE):
            return []
        with open(EQUIPMENT_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading equipment: {e}")
        return []

def save_equipment(equipment_data):
    """Save a new equipment listing"""
    import uuid
    try:
        equipment = get_all_equipment()
        
        # Generate unique ID and basic fields
        equipment_id = str(uuid.uuid4())
        equipment_data['_id'] = equipment_id
        equipment_data['created_at'] = datetime.utcnow().isoformat()
        equipment_data['status'] = 'available'
        
        equipment.append(equipment_data)
        
        with open(EQUIPMENT_FILE, 'w') as f:
            json.dump(equipment, f, indent=2)
            
        print(f"🚜 Equipment listed: {equipment_data.get('name')} [ID: {equipment_id}]")
        return equipment_id
    except Exception as e:
        print(f"Error saving equipment: {e}")
        return None

def update_equipment_status(equipment_id, status):
    """Update equipment status (available, rented, etc.)"""
    try:
        equipment = get_all_equipment()
        for item in equipment:
            if item.get('_id') == equipment_id:
                item['status'] = status
                item['updated_at'] = datetime.utcnow().isoformat()
                break
        
        with open(EQUIPMENT_FILE, 'w') as f:
            json.dump(equipment, f, indent=2)
        return True
    except Exception as e:
        print(f"Error updating equipment status: {e}")
        return False

def save_expense(expense_data):
    """Save a new expense entry (supports both MongoDB and JSON file fallback)"""
    global db
    try:
        if db is not None:
            # Check if ObjectId is needed for user_id
            from bson import ObjectId
            if 'user_id' in expense_data and isinstance(expense_data['user_id'], str):
                try:
                    expense_data['user_id'] = ObjectId(expense_data['user_id'])
                except:
                    pass
            
            result = db.expenses.insert_one(expense_data)
            return str(result.inserted_id)
        else:
            # File fallback
            import uuid
            expense_id = str(uuid.uuid4())
            expense_data['_id'] = expense_id
            
            expenses = []
            if os.path.exists(EXPENSES_FILE):
                with open(EXPENSES_FILE, 'r') as f:
                    try:
                        expenses = json.load(f)
                    except:
                        expenses = []
            
            expenses.append(expense_data)
            with open(EXPENSES_FILE, 'w') as f:
                json.dump(expenses, f, indent=2)
            
            return expense_id
    except Exception as e:
        print(f"Error saving expense: {e}")
        return None

def get_user_expenses(user_id):
    """Get all expenses for a user (supports both MongoDB and JSON file fallback)"""
    global db
    try:
        if db is not None:
            from bson import ObjectId
            query = {'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id}
            return list(db.expenses.find(query).sort('entry_date', -1))
        else:
            # File fallback
            if os.path.exists(EXPENSES_FILE):
                with open(EXPENSES_FILE, 'r') as f:
                    try:
                        all_expenses = json.load(f)
                        return [exp for exp in all_expenses if str(exp.get('user_id')) == str(user_id)]
                    except:
                        return []
            return []
    except Exception as e:
        print(f"Error fetching expenses: {e}")
        return []


# ============================================
# BUYER CONNECT - Direct Buyer-Farmer Connect
# ============================================

LISTINGS_FILE = os.path.join(DATA_DIR, 'crop_listings.json')
MARKET_PRICES_FILE = os.path.join(DATA_DIR, 'market_prices.json')

# Initialize listings file
if not os.path.exists(LISTINGS_FILE):
    with open(LISTINGS_FILE, 'w') as f:
        json.dump([], f)


def get_live_market_price(crop, district, state):
    """Fetch live market price for a crop from market_prices.json"""
    try:
        if not os.path.exists(MARKET_PRICES_FILE):
            return None
        
        with open(MARKET_PRICES_FILE, 'r', encoding='utf-8') as f:
            market_data = json.load(f)
        
        # Search for crop in user's district first
        matching_items = [
            item for item in market_data.get('data', [])
            if item['commodity'].lower() == crop.lower() 
            and item['district'].lower() == district.lower()
            and item['state'].lower() == state.lower()
        ]
        
        # If not found in exact district, search in same state
        if not matching_items:
            matching_items = [
                item for item in market_data.get('data', [])
                if item['commodity'].lower() == crop.lower()
                and item['state'].lower() == state.lower()
            ]
        
        # If still not found, search nationwide
        if not matching_items:
            matching_items = [
                item for item in market_data.get('data', [])
                if item['commodity'].lower() == crop.lower()
            ]
        
        if matching_items:
            item = matching_items[0]
            modal_price_quintal = item['modal_price']  # Price per quintal
            price_per_kg = round(modal_price_quintal / 100, 2)  # Convert to per kg
            
            # Calculate ±20% range
            min_price = round(price_per_kg * 0.8, 2)
            max_price = round(price_per_kg * 1.2, 2)
            
            return {
                'recommended_price': price_per_kg,
                'min_price': min_price,
                'max_price': max_price,
                'market': item.get('market', 'Local Mandi'),
                'date': item.get('price_date', datetime.now().strftime('%Y-%m-%d'))
            }
        
        return None
        
    except Exception as e:
        print(f"Error fetching live market price: {e}")
        return None


def create_crop_listing(listing_data):
    """Create a new crop listing for sale"""
    try:
        # MongoDB Atlas
        if db:
            try:
                # Don't set _id manually - let MongoDB generate ObjectId
                # Remove _id if it exists in listing_data
                if '_id' in listing_data:
                    del listing_data['_id']
                
                result = db.crop_listings.insert_one(listing_data)
                print(f"[MONGODB] ✅ Listing created successfully with ID: {str(result.inserted_id)}")
                return str(result.inserted_id)
            except Exception as e:
                print(f"[MONGODB ERROR] ❌ Failed to create listing: {e}")
                import traceback
                traceback.print_exc()
                return None
        
        # File-based fallback
        import uuid
        listing_data['_id'] = str(uuid.uuid4())
        
        with open(LISTINGS_FILE, 'r') as f:
            listings = json.load(f)
        
        listings.append(listing_data)
        
        with open(LISTINGS_FILE, 'w') as f:
            json.dump(listings, f, indent=2)
        
        print(f"[FILE] Listing created: {listing_data['_id']}")
        return listing_data['_id']
        
    except Exception as e:
        print(f"❌ Error creating listing: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_user_listings(user_id):
    """Get all listings by a specific farmer"""
    try:
        # MongoDB Atlas
        if db:
            try:
                listings = list(db.crop_listings.find({'farmer_id': user_id}).sort('created_at', -1))
                for listing in listings:
                    listing['_id'] = str(listing['_id'])
                return listings
            except Exception as e:
                print(f"[MONGODB ERROR] {e}")
        
        # File-based fallback
        with open(LISTINGS_FILE, 'r') as f:
            all_listings = json.load(f)
        
        user_listings = [l for l in all_listings if l.get('farmer_id') == user_id]
        user_listings.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return user_listings
        
    except Exception as e:
        print(f"Error fetching user listings: {e}")
        return []


def get_available_listings(crop='', district='', state='', sort_by='recent'):
    """Get all available listings for buyers (status='available')"""
    try:
        # MongoDB Atlas
        if db:
            try:
                query = {'status': 'available'}
                if crop:
                    query['crop'] = crop
                if district:
                    query['district'] = district
                if state:
                    query['state'] = state
                
                sort_order = [('created_at', -1)]  # Default: recent first
                if sort_by == 'price_low':
                    sort_order = [('farmer_price', 1)]
                elif sort_by == 'price_high':
                    sort_order = [('farmer_price', -1)]
                
                listings = list(db.crop_listings.find(query).sort(sort_order))
                for listing in listings:
                    listing['_id'] = str(listing['_id'])
                    # Add farmer details
                    farmer = get_user_by_id(listing['farmer_id'])
                    if farmer:
                        listing['farmer_name'] = farmer.get('name', 'Unknown')
                        listing['farmer_phone'] = farmer.get('phone', '')
                return listings
            except Exception as e:
                print(f"[MONGODB ERROR] {e}")
        
        # File-based fallback
        with open(LISTINGS_FILE, 'r') as f:
            all_listings = json.load(f)
        
        # Filter by status and criteria
        available = [l for l in all_listings if l.get('status') == 'available']
        
        if crop:
            available = [l for l in available if l.get('crop', '').lower() == crop.lower()]
        if district:
            available = [l for l in available if l.get('district', '').lower() == district.lower()]
        if state:
            available = [l for l in available if l.get('state', '').lower() == state.lower()]
        
        # Sort
        if sort_by == 'price_low':
            available.sort(key=lambda x: x.get('farmer_price', 0))
        elif sort_by == 'price_high':
            available.sort(key=lambda x: x.get('farmer_price', 0), reverse=True)
        else:  # recent
            available.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Add farmer details
        for listing in available:
            farmer = get_user_by_id(listing['farmer_id'])
            if farmer:
                listing['farmer_name'] = farmer.get('name', 'Unknown')
                listing['farmer_phone'] = farmer.get('phone', '')
        
        return available
        
    except Exception as e:
        print(f"Error fetching available listings: {e}")
        return []


def get_listing_by_id(listing_id):
    """Get a specific listing by ID"""
    try:
        # MongoDB Atlas
        if db:
            try:
                from bson.objectid import ObjectId
                # Try both ObjectId and string ID
                try:
                    listing = db.crop_listings.find_one({'_id': ObjectId(listing_id)})
                except:
                    listing = db.crop_listings.find_one({'_id': listing_id})
                
                if listing:
                    listing['_id'] = str(listing['_id'])
                    # Add farmer details
                    farmer = get_user_by_id(listing['farmer_id'])
                    if farmer:
                        listing['farmer_name'] = farmer.get('name', 'Unknown')
                        listing['farmer_phone'] = farmer.get('phone', '')
                    return listing
            except Exception as e:
                print(f"[MONGODB ERROR] {e}")
        
        # File-based fallback
        with open(LISTINGS_FILE, 'r') as f:
            listings = json.load(f)
        
        for listing in listings:
            if listing.get('_id') == listing_id:
                # Add farmer details
                farmer = get_user_by_id(listing['farmer_id'])
                if farmer:
                    listing['farmer_name'] = farmer.get('name', 'Unknown')
                    listing['farmer_phone'] = farmer.get('phone', '')
                return listing
        
        return None
        
    except Exception as e:
        print(f"Error fetching listing: {e}")
        return None


def confirm_purchase(listing_id, purchase_data):
    """Confirm purchase and update listing status atomically"""
    try:
        # MongoDB Atlas - ATOMIC UPDATE
        if db:
            try:
                from bson.objectid import ObjectId
                
                # Atomic update: only update if status is still 'available'
                # This prevents double-selling
                try:
                    obj_id = ObjectId(listing_id)
                except:
                    obj_id = listing_id
                
                result = db.crop_listings.find_one_and_update(
                    {'_id': obj_id, 'status': 'available'},  # Only if still available
                    {
                        '$set': {
                            'status': 'sold',
                            'buyer_id': purchase_data['buyer_id'],
                            'buyer_name': purchase_data['buyer_name'],
                            'buyer_phone': purchase_data['buyer_phone'],
                            'sold_at': purchase_data['purchased_at']
                        }
                    },
                    return_document=True
                )
                
                if result:
                    print(f"[MONGODB] Purchase confirmed for listing: {listing_id}")
                    return True, "Purchase confirmed successfully"
                else:
                    return False, "This listing is no longer available"
                    
            except Exception as e:
                print(f"[MONGODB ERROR] {e}")
        
        # File-based fallback (with lock to prevent race condition)
        try:
            import fcntl
            use_fcntl = True
        except ImportError:
            # Windows doesn't support fcntl
            use_fcntl = False
        
        with open(LISTINGS_FILE, 'r+') as f:
            # Lock file to prevent concurrent access (Unix/Linux only)
            if use_fcntl:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                except:
                    pass
            
            try:
                listings = json.load(f)
                
                # Find listing and check if still available
                for listing in listings:
                    if listing.get('_id') == listing_id:
                        if listing.get('status') != 'available':
                            return False, "This listing is no longer available"
                        
                        # Update status
                        listing['status'] = 'sold'
                        listing['buyer_id'] = purchase_data['buyer_id']
                        listing['buyer_name'] = purchase_data['buyer_name']
                        listing['buyer_phone'] = purchase_data['buyer_phone']
                        listing['sold_at'] = purchase_data['purchased_at']
                        
                        # Write back
                        f.seek(0)
                        json.dump(listings, f, indent=2)
                        f.truncate()
                        
                        print(f"[FILE] Purchase confirmed for listing: {listing_id}")
                        return True, "Purchase confirmed successfully"
                
                return False, "Listing not found"
                
            finally:
                # Release lock
                if use_fcntl:
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    except:
                        pass
        
    except Exception as e:
        print(f"Error confirming purchase: {e}")
        return False, str(e)


def update_listing_status(listing_id, new_status):
    """Update listing status (for cancellation, expiry, etc.)"""
    try:
        # MongoDB Atlas
        if db:
            try:
                from bson.objectid import ObjectId
                try:
                    obj_id = ObjectId(listing_id)
                except:
                    obj_id = listing_id
                
                result = db.crop_listings.update_one(
                    {'_id': obj_id},
                    {'$set': {'status': new_status, 'updated_at': datetime.utcnow().isoformat()}}
                )
                return result.modified_count > 0
            except Exception as e:
                print(f"[MONGODB ERROR] {e}")
        
        # File-based fallback
        with open(LISTINGS_FILE, 'r') as f:
            listings = json.load(f)
        
        for listing in listings:
            if listing.get('_id') == listing_id:
                listing['status'] = new_status
                listing['updated_at'] = datetime.utcnow().isoformat()
                
                with open(LISTINGS_FILE, 'w') as f:
                    json.dump(listings, f, indent=2)
                
                return True
        
        return False
        
    except Exception as e:
        print(f"Error updating listing status: {e}")
        return False


# ============================================
# EQUIPMENT SHARING MARKETPLACE FUNCTIONS
# ============================================

EQUIPMENT_LISTINGS_FILE = os.path.join(DATA_DIR, 'equipment_listings.json')
EQUIPMENT_BASE_PRICES_FILE = os.path.join(DATA_DIR, 'equipment_base_prices.json')

def get_live_equipment_rent(equipment_name, district='', state=''):
    """
    Get live market rent for equipment
    Returns: {recommended_rent, min_rent, max_rent}
    """
    try:
        # MongoDB Atlas
        if db:
            try:
                query = {'equipment_name': equipment_name}
                # Try to match by state, fallback to generic
                if state:
                    query['location'] = {'$regex': state, '$options': 'i'}
                
                base_price = db.equipment_base_prices.find_one(query)
                
                if base_price:
                    avg_rent = base_price['avg_rent_per_day']
                    return {
                        'recommended_rent': avg_rent,
                        'min_rent': round(avg_rent * 0.85, 2),
                        'max_rent': round(avg_rent * 1.15, 2)
                    }
            except Exception as e:
                print(f"[MONGODB ERROR] {e}")
        
        # File-based fallback
        if not os.path.exists(EQUIPMENT_BASE_PRICES_FILE):
            return None
        
        with open(EQUIPMENT_BASE_PRICES_FILE, 'r') as f:
            base_prices = json.load(f)
        
        # Find matching equipment
        for price in base_prices:
            if price['equipment_name'].lower() == equipment_name.lower():
                # Try to match by state first, fallback to any location
                if state and state.lower() in price.get('location', '').lower():
                    avg_rent = price['avg_rent_per_day']
                    return {
                        'recommended_rent': avg_rent,
                        'min_rent': round(avg_rent * 0.85, 2),
                        'max_rent': round(avg_rent * 1.15, 2)
                    }
        
        # Fallback: return first matching equipment regardless of location
        for price in base_prices:
            if price['equipment_name'].lower() == equipment_name.lower():
                avg_rent = price['avg_rent_per_day']
                print(f"[DB] Found equipment rent: {equipment_name} = ₹{avg_rent}/day")
                return {
                    'recommended_rent': avg_rent,
                    'min_rent': round(avg_rent * 0.85, 2),
                    'max_rent': round(avg_rent * 1.15, 2)
                }
        
        print(f"[DB] No rental rate found for equipment: {equipment_name}, state: {state}")
        print(f"[DB] Available equipment in file: {[p['equipment_name'] for p in base_prices[:5]]}")
        return None
        
    except Exception as e:
        print(f"Error fetching live equipment rent: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_equipment_listing(listing_data):
    """Create new equipment listing"""
    try:
        # MongoDB Atlas
        if db:
            try:
                result = db.equipment_listings.insert_one(listing_data)
                return str(result.inserted_id)
            except Exception as e:
                print(f"[MONGODB ERROR] {e}")
        
        # File-based fallback
        if not os.path.exists(EQUIPMENT_LISTINGS_FILE):
            with open(EQUIPMENT_LISTINGS_FILE, 'w') as f:
                json.dump([], f)
        
        with open(EQUIPMENT_LISTINGS_FILE, 'r') as f:
            listings = json.load(f)
        
        # Generate unique ID
        import uuid
        listing_data['_id'] = str(uuid.uuid4())
        
        listings.append(listing_data)
        
        with open(EQUIPMENT_LISTINGS_FILE, 'w') as f:
            json.dump(listings, f, indent=2)
        
        return listing_data['_id']
        
    except Exception as e:
        print(f"Error creating equipment listing: {e}")
        return None


def get_available_equipment(equipment_name='', district='', state='', sort_by='recent'):
    """Get all available equipment (status='available')"""
    try:
        # MongoDB Atlas
        if db:
            try:
                query = {'status': 'available'}
                if equipment_name:
                    query['equipment_name'] = equipment_name
                if district:
                    query['district'] = district
                if state:
                    query['state'] = state
                
                sort_order = [('created_at', -1)]  # Default: recent first
                if sort_by == 'price_low':
                    sort_order = [('owner_rent', 1)]
                elif sort_by == 'price_high':
                    sort_order = [('owner_rent', -1)]
                
                listings = list(db.equipment_listings.find(query).sort(sort_order))
                for listing in listings:
                    listing['_id'] = str(listing['_id'])
                return listings
            except Exception as e:
                print(f"[MONGODB ERROR] {e}")
        
        # File-based fallback
        if not os.path.exists(EQUIPMENT_LISTINGS_FILE):
            return []
        
        with open(EQUIPMENT_LISTINGS_FILE, 'r') as f:
            all_listings = json.load(f)
        
        # Filter by status and criteria
        available = [l for l in all_listings if l.get('status') == 'available']
        
        if equipment_name:
            available = [l for l in available if l.get('equipment_name', '').lower() == equipment_name.lower()]
        if district:
            available = [l for l in available if l.get('district', '').lower() == district.lower()]
        if state:
            available = [l for l in available if l.get('state', '').lower() == state.lower()]
        
        # Sort
        if sort_by == 'price_low':
            available.sort(key=lambda x: x.get('owner_rent', 0))
        elif sort_by == 'price_high':
            available.sort(key=lambda x: x.get('owner_rent', 0), reverse=True)
        else:
            available.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return available
        
    except Exception as e:
        print(f"Error fetching available equipment: {e}")
        return []


def get_equipment_listing_by_id(listing_id):
    """Get equipment listing by ID"""
    try:
        # MongoDB Atlas
        if db:
            try:
                from bson.objectid import ObjectId
                listing = db.equipment_listings.find_one({'_id': ObjectId(listing_id)})
                if listing:
                    listing['_id'] = str(listing['_id'])
                    return listing
            except:
                pass
        
        # File-based fallback
        if not os.path.exists(EQUIPMENT_LISTINGS_FILE):
            return None
        
        with open(EQUIPMENT_LISTINGS_FILE, 'r') as f:
            listings = json.load(f)
        
        for listing in listings:
            if listing.get('_id') == listing_id:
                return listing
        
        return None
        
    except Exception as e:
        print(f"Error fetching equipment listing: {e}")
        return None


def book_equipment_atomic(listing_id, booking_data):
    """
    Atomically book equipment (prevents double booking)
    Returns: (success, message)
    """
    try:
        # MongoDB Atlas - ATOMIC UPDATE
        if db:
            try:
                from bson.objectid import ObjectId
                
                # Atomic update: only update if status is 'available'
                result = db.equipment_listings.update_one(
                    {
                        '_id': ObjectId(listing_id),
                        'status': 'available'  # Critical: only update if still available
                    },
                    {
                        '$set': {
                            'status': 'booked',
                            'renter_id': booking_data['renter_id'],
                            'renter_name': booking_data['renter_name'],
                            'renter_phone': booking_data['renter_phone'],
                            'from_date': booking_data['from_date'],
                            'to_date': booking_data['to_date'],
                            'booked_at': booking_data['booked_at']
                        }
                    }
                )
                
                if result.modified_count > 0:
                    return (True, 'Equipment booked successfully')
                else:
                    return (False, 'Equipment is no longer available')
                    
            except Exception as e:
                print(f"[MONGODB ERROR] {e}")
        
        # File-based fallback with simple locking
        if not os.path.exists(EQUIPMENT_LISTINGS_FILE):
            return (False, 'Equipment not found')
        
        with open(EQUIPMENT_LISTINGS_FILE, 'r') as f:
            listings = json.load(f)
        
        for listing in listings:
            if listing.get('_id') == listing_id:
                if listing.get('status') != 'available':
                    return (False, 'Equipment is no longer available')
                
                # Update listing
                listing['status'] = 'booked'
                listing['renter_id'] = booking_data['renter_id']
                listing['renter_name'] = booking_data['renter_name']
                listing['renter_phone'] = booking_data['renter_phone']
                listing['from_date'] = booking_data['from_date']
                listing['to_date'] = booking_data['to_date']
                listing['booked_at'] = booking_data['booked_at']
                
                with open(EQUIPMENT_LISTINGS_FILE, 'w') as f:
                    json.dump(listings, f, indent=2)
                
                return (True, 'Equipment booked successfully')
        
        return (False, 'Equipment not found')
        
    except Exception as e:
        print(f"Error booking equipment: {e}")
        return (False, 'An error occurred')


def complete_equipment_rental(listing_id):
    """Mark equipment rental as completed"""
    try:
        # MongoDB Atlas
        if db:
            try:
                from bson.objectid import ObjectId
                
                result = db.equipment_listings.update_one(
                    {'_id': ObjectId(listing_id)},
                    {
                        '$set': {
                            'status': 'completed',
                            'completed_at': datetime.utcnow().isoformat()
                        }
                    }
                )
                
                if result.modified_count > 0:
                    return (True, 'Rental completed successfully')
                else:
                    return (False, 'Equipment not found')
                    
            except Exception as e:
                print(f"[MONGODB ERROR] {e}")
        
        # File-based fallback
        if not os.path.exists(EQUIPMENT_LISTINGS_FILE):
            return (False, 'Equipment not found')
        
        with open(EQUIPMENT_LISTINGS_FILE, 'r') as f:
            listings = json.load(f)
        
        for listing in listings:
            if listing.get('_id') == listing_id:
                listing['status'] = 'completed'
                listing['completed_at'] = datetime.utcnow().isoformat()
                
                with open(EQUIPMENT_LISTINGS_FILE, 'w') as f:
                    json.dump(listings, f, indent=2)
                
                return (True, 'Rental completed successfully')
        
        return (False, 'Equipment not found')
        
    except Exception as e:
        print(f"Error completing rental: {e}")
        return (False, 'An error occurred')


def get_user_equipment_listings(user_id):
    """Get all equipment listings by a user"""
    try:
        # MongoDB Atlas
        if db:
            try:
                listings = list(db.equipment_listings.find({'owner_id': user_id}).sort('created_at', -1))
                for listing in listings:
                    listing['_id'] = str(listing['_id'])
                return listings
            except Exception as e:
                print(f"[MONGODB ERROR] {e}")
        
        # File-based fallback
        if not os.path.exists(EQUIPMENT_LISTINGS_FILE):
            return []
        
        with open(EQUIPMENT_LISTINGS_FILE, 'r') as f:
            all_listings = json.load(f)
        
        user_listings = [l for l in all_listings if l.get('owner_id') == user_id]
        user_listings.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return user_listings
        
    except Exception as e:
        print(f"Error fetching user equipment listings: {e}")
        return []


def confirm_equipment_rental(listing_id, rental_data):
    """Confirm equipment rental and update listing status atomically"""
    try:
        # MongoDB Atlas - ATOMIC UPDATE
        if db:
            try:
                from bson.objectid import ObjectId
                
                # Atomic update: only update if status is still 'available'
                # This prevents double-booking
                try:
                    obj_id = ObjectId(listing_id)
                except:
                    obj_id = listing_id
                
                result = db.equipment_listings.find_one_and_update(
                    {'_id': obj_id, 'status': 'available'},  # Only if still available
                    {
                        '$set': {
                            'status': 'booked',
                            'renter_id': rental_data['renter_id'],
                            'renter_name': rental_data['renter_name'],
                            'renter_phone': rental_data['renter_phone'],
                            'rental_from': rental_data['rental_from'],
                            'rental_to': rental_data['rental_to'],
                            'rental_days': rental_data['rental_days'],
                            'total_rent': rental_data['total_rent'],
                            'booked_at': rental_data['booked_at']
                        }
                    },
                    return_document=True
                )
                
                if result:
                    print(f"[MONGODB] Rental confirmed for listing: {listing_id}")
                    return True, "Rental confirmed successfully"
                else:
                    return False, "This equipment is no longer available"
                    
            except Exception as e:
                print(f"[MONGODB ERROR] {e}")
        
        # File-based fallback (with lock to prevent race condition)
        try:
            import fcntl
            use_fcntl = True
        except ImportError:
            # Windows doesn't support fcntl
            use_fcntl = False
        
        if not os.path.exists(EQUIPMENT_LISTINGS_FILE):
            return False, "Listing not found"
        
        with open(EQUIPMENT_LISTINGS_FILE, 'r+') as f:
            # Lock file to prevent concurrent access (Unix/Linux only)
            if use_fcntl:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                except:
                    pass
            
            try:
                listings = json.load(f)
                
                # Find listing and check if still available
                for listing in listings:
                    if listing.get('_id') == listing_id:
                        if listing.get('status') != 'available':
                            return False, "This equipment is no longer available"
                        
                        # Update status
                        listing['status'] = 'booked'
                        listing['renter_id'] = rental_data['renter_id']
                        listing['renter_name'] = rental_data['renter_name']
                        listing['renter_phone'] = rental_data['renter_phone']
                        listing['rental_from'] = rental_data['rental_from']
                        listing['rental_to'] = rental_data['rental_to']
                        listing['rental_days'] = rental_data['rental_days']
                        listing['total_rent'] = rental_data['total_rent']
                        listing['booked_at'] = rental_data['booked_at']
                        
                        # Write back
                        f.seek(0)
                        f.truncate()
                        json.dump(listings, f, indent=4)
                        
                        return True, "Rental confirmed successfully"
                
                return False, "Listing not found"
                
            finally:
                if use_fcntl:
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    except:
                        pass
        
    except Exception as e:
        print(f"Error confirming rental: {e}")
        return False, f"Error: {str(e)}"


def get_user_bookings(user_id):
    """Get all equipment bookings made by a user"""
    try:
        # MongoDB Atlas
        if db:
            try:
                bookings = list(db.equipment_listings.find({'renter_id': user_id}).sort('booked_at', -1))
                for booking in bookings:
                    booking['_id'] = str(booking['_id'])
                return bookings
            except Exception as e:
                print(f"[MONGODB ERROR] {e}")
        
        # File-based fallback
        if not os.path.exists(EQUIPMENT_LISTINGS_FILE):
            return []
        
        with open(EQUIPMENT_LISTINGS_FILE, 'r') as f:
            all_listings = json.load(f)
        
        user_bookings = [l for l in all_listings if l.get('renter_id') == user_id]
        user_bookings.sort(key=lambda x: x.get('booked_at', ''), reverse=True)
        
        return user_bookings
        
    except Exception as e:
        print(f"Error fetching user bookings: {e}")
        return []
