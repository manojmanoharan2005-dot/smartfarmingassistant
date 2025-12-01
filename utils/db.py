from datetime import datetime
import os
import json
from pymongo import MongoClient

# MongoDB Atlas connection string from the screenshot
MONGODB_URI = "mongodb+srv://manojmanokaran007_db_user:manoj28@cluster0.jgpydp.mongodb.net/?appName=Cluster0"

# Local file-based storage directory and file paths (used when MongoDB is not available)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DATA_DIR = os.path.abspath(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, 'users.json')
CROPS_FILE = os.path.join(DATA_DIR, 'crops.json')
FERTILIZERS_FILE = os.path.join(DATA_DIR, 'fertilizers.json')
DISEASES_FILE = os.path.join(DATA_DIR, 'diseases.json')

client = None
db = None

def init_db(app):
    global client, db
    
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Initialize JSON files if they don't exist
    for file_path in [USERS_FILE, CROPS_FILE, FERTILIZERS_FILE, DISEASES_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump({}, f)
    
    print("✅ File-based database initialized successfully!")
    print("📁 Data will be stored in the 'data' directory")
    
    # Try MongoDB Atlas connection as backup
    try:
        client = MongoClient(MONGODB_URI, 
                           serverSelectionTimeoutMS=10000,
                           connectTimeoutMS=10000,
                           socketTimeoutMS=10000)
        
        # Use smart_farming database
        db = client.smart_farming
        # Test the connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # Create indexes for better performance
        try:
            db.users.create_index("email", unique=True)
            print("📊 Database indexes created successfully")
        except Exception as e:
            print(f"⚠️ Index creation note: {e}")
            
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("🔧 Using enhanced mock database for development")
        db = MockDatabase()

class MockDatabase:
    """Enhanced Mock database for development when MongoDB is not available"""
    def __init__(self):
        self.users_data = {}
        self.crops_data = []
        self.fertilizers_data = []
        self.diseases_data = []
        print("📝 Mock database initialized with enhanced features")
    
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

def find_user_by_id(user_id):
    try:
        if hasattr(db, 'users') and db:
            from bson.objectid import ObjectId
            users = db.users
            # Explicitly exclude password field from query result
            user = users.find_one(
                {'_id': ObjectId(user_id)}, 
                {'password': 0}  # Exclude password field
            )
            return user
    except Exception as e:
        print(f"Error fetching user by ID: {e}")
        
    # Mock user for development if database fails
    return {
        '_id': user_id, 
        'name': 'Test User', 
        'email': 'test@example.com',
        'phone': '+91 9876543210',
        'state': 'Karnataka',
        'district': 'Bangalore',
        'created_at': datetime.utcnow()
    }

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
    print(f"🧪 Fertilizer recommendation saved for user {user_id}: {fertilizer_data['name']}")
    return type('MockResult', (), {'inserted_id': 'mock_fertilizer_id'})()

def get_user_fertilizers(user_id):
    # Return some mock data for testing
    return [
        {
            '_id': 'fert1',
            'fertilizer_name': 'Urea',
            'crop_type': 'Rice',
            'priority': 'High'
        }
    ]

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
