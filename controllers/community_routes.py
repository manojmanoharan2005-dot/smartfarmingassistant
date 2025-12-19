from flask import Blueprint, render_template, session, request, jsonify
from utils.auth import login_required
import json
import os
from datetime import datetime
import uuid

community_bp = Blueprint('community', __name__)

MESSAGES_FILE = 'data/community_messages.json'

def load_messages():
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r') as f:
            return json.load(f)
    return {
        'rice_farmers': [],
        'pest_control': [],
        'organic_farming': [],
        'irrigation_tips': [],
        'general': []
    }

def save_messages(messages):
    os.makedirs('data', exist_ok=True)
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

@community_bp.route('/community-hub')
@login_required
def community_hub():
    user_name = session.get('user_name', 'Guest')
    messages = load_messages()
    
    # Topic rooms
    topic_rooms = [
        {'id': 'rice_farmers', 'name': 'Rice Farmers', 'icon': '🌾', 'count': len(messages.get('rice_farmers', []))},
        {'id': 'pest_control', 'name': 'Pest Control', 'icon': '🐛', 'count': len(messages.get('pest_control', []))},
        {'id': 'organic_farming', 'name': 'Organic Farming', 'icon': '🌿', 'count': len(messages.get('organic_farming', []))},
        {'id': 'irrigation_tips', 'name': 'Irrigation Tips', 'icon': '💧', 'count': len(messages.get('irrigation_tips', []))},
        {'id': 'general', 'name': 'General Discussion', 'icon': '💬', 'count': len(messages.get('general', []))}
    ]
    
    return render_template('community_hub.html',
                         user_name=user_name,
                         topic_rooms=topic_rooms)

@community_bp.route('/get-messages/<room_id>')
@login_required
def get_messages(room_id):
    messages = load_messages()
    room_messages = messages.get(room_id, [])
    return jsonify({
        'success': True,
        'messages': room_messages
    })

@community_bp.route('/send-message', methods=['POST'])
@login_required
def send_message():
    data = request.json
    room_id = data.get('room_id')
    message_text = data.get('message')
    
    if not room_id or not message_text:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400
    
    messages = load_messages()
    
    new_message = {
        'id': str(uuid.uuid4()),
        'user': session.get('user_name', 'Anonymous'),
        'message': message_text,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'image': None
    }
    
    if room_id not in messages:
        messages[room_id] = []
    
    messages[room_id].append(new_message)
    save_messages(messages)
    
    return jsonify({
        'success': True,
        'message': new_message
    })

@community_bp.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    room_id = request.form.get('room_id')
    message_text = request.form.get('message', 'Shared an image')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Save image
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join('static/uploads', filename)
    os.makedirs('static/uploads', exist_ok=True)
    file.save(filepath)
    
    # Add message with image
    messages = load_messages()
    new_message = {
        'id': str(uuid.uuid4()),
        'user': session.get('user_name', 'Anonymous'),
        'message': message_text,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'image': filename
    }
    
    if room_id not in messages:
        messages[room_id] = []
    
    messages[room_id].append(new_message)
    save_messages(messages)
    
    return jsonify({
        'success': True,
        'message': new_message
    })
