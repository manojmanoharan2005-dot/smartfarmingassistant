"""
MongoDB Atlas Setup Script for Smart Farming Assistant
========================================================
This script sets up all required collections and indexes in MongoDB Atlas.

Usage:
1. Set your MONGODB_URI environment variable or create a .env file with:
   MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority

2. Run this script:
   python setup_mongodb.py
"""

import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid, OperationFailure
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI')

def setup_mongodb():
    """Set up MongoDB Atlas with all required collections and indexes"""
    
    if not MONGODB_URI:
        print("❌ ERROR: MONGODB_URI environment variable is not set!")
        print("\nPlease set your MongoDB Atlas connection string:")
        print("  1. Create a .env file in the project root")
        print("  2. Add: MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority")
        print("\nOr set the environment variable directly:")
        print('  $env:MONGODB_URI = "your-connection-string"')
        return False
    
    try:
        print("🔄 Connecting to MongoDB Atlas...")
        client = MongoClient(MONGODB_URI, 
                           serverSelectionTimeoutMS=30000,
                           connectTimeoutMS=30000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # Use/create database
        db = client.myVirtualDatabase
        print(f"📁 Using database: myVirtualDatabase")
        
        # Define collections with their indexes
        collections_config = {
            'users': {
                'description': 'User accounts and profiles',
                'indexes': [
                    {'keys': [('email', ASCENDING)], 'unique': True},
                    {'keys': [('phone', ASCENDING)], 'unique': False},
                    {'keys': [('pincode', ASCENDING)], 'unique': False},
                    {'keys': [('state', ASCENDING), ('district', ASCENDING)], 'unique': False}
                ],
                'validator': {
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['email', 'password', 'name'],
                        'properties': {
                            'email': {'bsonType': 'string', 'description': 'User email address'},
                            'password': {'bsonType': 'string', 'description': 'Hashed password'},
                            'name': {'bsonType': 'string', 'description': 'User full name'},
                            'phone': {'bsonType': 'string', 'description': 'Phone number'},
                            'pincode': {'bsonType': 'string', 'description': '6-digit postal pincode'},
                            'state': {'bsonType': 'string', 'description': 'State location'},
                            'district': {'bsonType': 'string', 'description': 'District location'},
                            'village': {'bsonType': 'string', 'description': 'Village/Area name'},
                            'created_at': {'bsonType': 'string', 'description': 'Account creation timestamp'},
                            'saved_crops': {'bsonType': 'array', 'description': 'Saved crop recommendations'},
                            'saved_fertilizers': {'bsonType': 'array', 'description': 'Saved fertilizer recommendations'},
                            'disease_history': {'bsonType': 'array', 'description': 'Disease detection history'},
                            'last_notification_read_at': {'bsonType': 'string', 'description': 'Last notification read timestamp'}
                        }
                    }
                }
            },
            'otps': {
                'description': 'OTP verification codes',
                'indexes': [
                    {'keys': [('mobile_number', ASCENDING)], 'unique': False},
                    {'keys': [('expires_at', ASCENDING)], 'expireAfterSeconds': 0}  # TTL index
                ]
            },
            'password_reset_tokens': {
                'description': 'Password reset tokens',
                'indexes': [
                    {'keys': [('email', ASCENDING)], 'unique': False},
                    {'keys': [('token', ASCENDING)], 'unique': True},
                    {'keys': [('expires_at', ASCENDING)], 'expireAfterSeconds': 0}  # TTL index
                ]
            },
            'crops': {
                'description': 'Crop recommendation data',
                'indexes': [
                    {'keys': [('user_id', ASCENDING)], 'unique': False},
                    {'keys': [('crop_name', ASCENDING)], 'unique': False}
                ]
            },
            'fertilizers': {
                'description': 'Fertilizer recommendation data',
                'indexes': [
                    {'keys': [('user_id', ASCENDING)], 'unique': False},
                    {'keys': [('fertilizer_name', ASCENDING)], 'unique': False}
                ]
            },
            'diseases': {
                'description': 'Disease detection history',
                'indexes': [
                    {'keys': [('user_id', ASCENDING)], 'unique': False},
                    {'keys': [('detected_at', DESCENDING)], 'unique': False}
                ]
            },
            'crop_listings': {
                'description': 'Crop marketplace listings',
                'indexes': [
                    {'keys': [('farmer_id', ASCENDING)], 'unique': False},
                    {'keys': [('status', ASCENDING)], 'unique': False},
                    {'keys': [('state', ASCENDING), ('district', ASCENDING)], 'unique': False},
                    {'keys': [('crop', ASCENDING)], 'unique': False},
                    {'keys': [('created_at', DESCENDING)], 'unique': False},
                    {'keys': [('expires_at', ASCENDING)], 'unique': False}
                ],
                'validator': {
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['farmer_id', 'crop', 'quantity', 'status'],
                        'properties': {
                            'farmer_id': {'bsonType': 'string', 'description': 'ID of the farmer'},
                            'farmer_name': {'bsonType': 'string', 'description': 'Name of the farmer'},
                            'farmer_phone': {'bsonType': 'string', 'description': 'Phone of the farmer'},
                            'crop': {'bsonType': 'string', 'description': 'Crop name'},
                            'quantity': {'bsonType': 'double', 'description': 'Quantity available'},
                            'unit': {'bsonType': 'string', 'description': 'Unit of measurement'},
                            'state': {'bsonType': 'string', 'description': 'State location'},
                            'district': {'bsonType': 'string', 'description': 'District location'},
                            'latitude': {'bsonType': 'double', 'description': 'GPS latitude'},
                            'longitude': {'bsonType': 'double', 'description': 'GPS longitude'},
                            'farmer_price': {'bsonType': 'double', 'description': 'Price set by farmer'},
                            'recommended_price': {'bsonType': 'double', 'description': 'System recommended price'},
                            'min_price': {'bsonType': 'double', 'description': 'Minimum price'},
                            'max_price': {'bsonType': 'double', 'description': 'Maximum price'},
                            'live_market_price': {'bsonType': 'double', 'description': 'Current market price'},
                            'status': {'enum': ['active', 'sold', 'cancelled', 'expired'], 'description': 'Listing status'},
                            'created_at': {'bsonType': 'string', 'description': 'Creation timestamp'},
                            'expires_at': {'bsonType': 'string', 'description': 'Expiry timestamp'}
                        }
                    }
                }
            },
            'equipment_listings': {
                'description': 'Equipment sharing/rental listings',
                'indexes': [
                    {'keys': [('owner_id', ASCENDING)], 'unique': False},
                    {'keys': [('renter_id', ASCENDING)], 'unique': False},
                    {'keys': [('status', ASCENDING)], 'unique': False},
                    {'keys': [('equipment_name', ASCENDING)], 'unique': False},
                    {'keys': [('state', ASCENDING), ('district', ASCENDING)], 'unique': False},
                    {'keys': [('created_at', DESCENDING)], 'unique': False}
                ],
                'validator': {
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['owner_id', 'equipment_name', 'rent_per_day', 'status'],
                        'properties': {
                            'owner_id': {'bsonType': 'string', 'description': 'ID of equipment owner'},
                            'owner_name': {'bsonType': 'string', 'description': 'Name of owner'},
                            'owner_phone': {'bsonType': 'string', 'description': 'Phone of owner'},
                            'equipment_name': {'bsonType': 'string', 'description': 'Equipment name'},
                            'description': {'bsonType': 'string', 'description': 'Equipment description'},
                            'rent_per_day': {'bsonType': 'double', 'description': 'Daily rental rate'},
                            'state': {'bsonType': 'string', 'description': 'State location'},
                            'district': {'bsonType': 'string', 'description': 'District location'},
                            'status': {'enum': ['available', 'booked', 'unavailable'], 'description': 'Equipment status'},
                            'renter_id': {'bsonType': 'string', 'description': 'ID of current renter'},
                            'booked_at': {'bsonType': 'string', 'description': 'Booking timestamp'},
                            'created_at': {'bsonType': 'string', 'description': 'Creation timestamp'}
                        }
                    }
                }
            },
            'equipment_base_prices': {
                'description': 'Base rental prices for equipment by location',
                'indexes': [
                    {'keys': [('equipment_name', ASCENDING), ('location', ASCENDING)], 'unique': True}
                ]
            },
            'expenses': {
                'description': 'User expense tracking',
                'indexes': [
                    {'keys': [('user_id', ASCENDING)], 'unique': False},
                    {'keys': [('entry_date', DESCENDING)], 'unique': False},
                    {'keys': [('category', ASCENDING)], 'unique': False}
                ]
            },
            'notifications': {
                'description': 'User notifications',
                'indexes': [
                    {'keys': [('user_id', ASCENDING)], 'unique': False},
                    {'keys': [('created_at', DESCENDING)], 'unique': False},
                    {'keys': [('read', ASCENDING)], 'unique': False},
                    {'keys': [('type', ASCENDING)], 'unique': False}
                ]
            },
            'growing_activities': {
                'description': 'Growing activities and tasks',
                'indexes': [
                    {'keys': [('user_id', ASCENDING)], 'unique': False},
                    {'keys': [('crop_id', ASCENDING)], 'unique': False},
                    {'keys': [('status', ASCENDING)], 'unique': False},
                    {'keys': [('due_date', ASCENDING)], 'unique': False}
                ]
            }
        }
        
        print("\n📦 Creating collections and indexes...")
        print("=" * 50)
        
        for collection_name, config in collections_config.items():
            try:
                # Check if collection exists
                existing_collections = db.list_collection_names()
                
                if collection_name in existing_collections:
                    print(f"📂 Collection '{collection_name}' already exists")
                else:
                    # Create collection with validator if specified
                    if 'validator' in config:
                        try:
                            db.create_collection(collection_name, validator=config['validator'])
                            print(f"✅ Created collection: {collection_name} (with validation)")
                        except OperationFailure:
                            db.create_collection(collection_name)
                            print(f"✅ Created collection: {collection_name}")
                    else:
                        db.create_collection(collection_name)
                        print(f"✅ Created collection: {collection_name}")
                
                # Create indexes
                collection = db[collection_name]
                for idx_config in config.get('indexes', []):
                    try:
                        keys = idx_config['keys']
                        index_options = {k: v for k, v in idx_config.items() if k != 'keys'}
                        collection.create_index(keys, **index_options)
                    except Exception as idx_error:
                        # Index might already exist or not supported
                        pass
                
                print(f"   └── {config['description']}")
                
            except Exception as e:
                print(f"⚠️  Warning for '{collection_name}': {e}")
        
        # Insert sample equipment base prices data
        print("\n📊 Setting up equipment base prices...")
        equipment_prices = [
            {"equipment_name": "Tractor", "location": "Tamil Nadu", "avg_rent_per_day": 1500},
            {"equipment_name": "Tractor", "location": "Karnataka", "avg_rent_per_day": 1400},
            {"equipment_name": "Tractor", "location": "Andhra Pradesh", "avg_rent_per_day": 1450},
            {"equipment_name": "Harvester", "location": "Tamil Nadu", "avg_rent_per_day": 2500},
            {"equipment_name": "Harvester", "location": "Karnataka", "avg_rent_per_day": 2400},
            {"equipment_name": "Harvester", "location": "Andhra Pradesh", "avg_rent_per_day": 2450},
            {"equipment_name": "Plough", "location": "Tamil Nadu", "avg_rent_per_day": 400},
            {"equipment_name": "Plough", "location": "Karnataka", "avg_rent_per_day": 380},
            {"equipment_name": "Seed Drill", "location": "Tamil Nadu", "avg_rent_per_day": 600},
            {"equipment_name": "Seed Drill", "location": "Karnataka", "avg_rent_per_day": 580},
            {"equipment_name": "Sprayer", "location": "Tamil Nadu", "avg_rent_per_day": 300},
            {"equipment_name": "Sprayer", "location": "Karnataka", "avg_rent_per_day": 290},
            {"equipment_name": "Rotavator", "location": "Tamil Nadu", "avg_rent_per_day": 800},
            {"equipment_name": "Rotavator", "location": "Karnataka", "avg_rent_per_day": 750},
            {"equipment_name": "Cultivator", "location": "Tamil Nadu", "avg_rent_per_day": 500},
            {"equipment_name": "Cultivator", "location": "Karnataka", "avg_rent_per_day": 480},
            {"equipment_name": "Water Pump", "location": "Tamil Nadu", "avg_rent_per_day": 350},
            {"equipment_name": "Water Pump", "location": "Karnataka", "avg_rent_per_day": 320},
        ]
        
        equipment_prices_collection = db.equipment_base_prices
        for price_data in equipment_prices:
            try:
                equipment_prices_collection.update_one(
                    {"equipment_name": price_data["equipment_name"], "location": price_data["location"]},
                    {"$set": price_data},
                    upsert=True
                )
            except Exception:
                pass
        print("✅ Equipment base prices initialized")
        
        print("\n" + "=" * 50)
        print("🎉 MongoDB Atlas setup completed successfully!")
        print("=" * 50)
        
        # Print summary
        print("\n📋 Collections Summary:")
        for coll_name in db.list_collection_names():
            count = db[coll_name].count_documents({})
            print(f"   • {coll_name}: {count} documents")
        
        print("\n✨ Your Smart Farming Assistant is now ready to use MongoDB Atlas!")
        print("   Make sure your .env file has the MONGODB_URI variable set.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to setup MongoDB - {e}")
        print("\n🔍 Troubleshooting tips:")
        print("   1. Check if your MongoDB Atlas connection string is correct")
        print("   2. Ensure your IP address is whitelisted in MongoDB Atlas Network Access")
        print("   3. Verify your username and password are correct")
        print("   4. Check if the cluster is running and accessible")
        return False

def test_connection():
    """Test the MongoDB connection"""
    if not MONGODB_URI:
        print("❌ MONGODB_URI not set")
        return False
    
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("   Smart Farming Assistant - MongoDB Atlas Setup")
    print("=" * 60)
    print()
    
    setup_mongodb()
