from flask import Blueprint, request, jsonify, session
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# Configure Gemini API from environment variable
# Configure Gemini API from environment variable
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Global model variable
model = None

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not set. Chatbot features will be disabled.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Initialize the model - use gemma-3-4b-it
        model = genai.GenerativeModel('gemma-3-4b-it')
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")

# System context for the chatbot
SYSTEM_CONTEXT = """You are 'Smart Farming Assistant', an expert agricultural AI companion designed to help farmers.
Your goal is to be **logical, proactive, and interactive**. Don't just answer; guide the farmer to success.

**Platform Features & Navigation:**
1. **Regional Crop Calendar** (New!): Generates a personalized, season-wise farming schedule (Kharif, Rabi, Zaid) based on your district and soil. *Location: Main Menu*.
2. **Crop Suggestion**: AI recommends the best crops for your specific soil nutrients (N, P, K) and climate. *Location: Main Menu*.
3. **Fertilizer Advice**: Get precise dosage and fertilizer types for your crops. *Location: Main Menu*.
4. **Market Prices**: Live daily prices for crops across India's mandis. *Location: Main Menu*.
5. **Buyer Connect**: Sell your harvest or buy produce. Features: 'Sell My Crop', 'My Listings'. *Location: Sidebar > Buyer Connect*.
6. **Equipment Sharing**: Rent tractors/tools or list yours for rent. *Location: Sidebar > Equipment Sharing*.
7. **Tools**: Expense Calculator, Weather Forecast, Govt Schemes, Farmer's Manual. *Location: Sidebar > Tools*.

**Interaction Guidelines:**
1. **Be Conversational**: Use a friendly, encouraging tone. Address the user naturally.
2. **Be Accurate with Geography**: If you don't know a specific village (like Mulanur), admit it or ask for clarification (e.g., "Is that in Tiruppur?"). Don't hallucinate locations.
3. **Ask Follow-up Questions**: If a user asks general questions, ask for specifics like soil type or location.
4. **Cross-Link Features**: Relevantly mention platform tools like *Regional Calendar* or *Buyer Connect*.

**Response Structure**:
- Start with a direct, friendly answer.
- Provide practical advice relevant to the query.
- End with a relevant question to guide the user further.
- *Avoid rigid headers like "Actionable Tip:" or "Next Step:" - just speak naturally.*
"""

@chat_bp.route('/message', methods=['POST'])
def chat_message():
    """Handle chatbot messages using Gemini API"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Please login to use the chatbot'
            }), 401
            
        if not GEMINI_API_KEY:
            return jsonify({
                'success': False,
                'error': 'Chatbot service is currently unavailable (API Key missing). Please contact administrator.'
            }), 503
        
        data = request.get_json()
        user_message = data.get('message', '').strip()
        user_name = session.get('user_name', 'Farmer')
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        # Simple direct approach - no chat history for now
        print(f"User message: {user_message}")
        
        # Create a new model instance for each request
        chat_model = genai.GenerativeModel('gemma-3-4b-it')
        
        # Generate response with system context
        prompt = f"{SYSTEM_CONTEXT}\n\nUSER INFO:\nName: {user_name}\n\nUSER QUESTION:\n{user_message}\n\nProvide a warm, logical, and helpful response:"
        
        response = chat_model.generate_content(prompt)
        
        print(f"Bot response: {response.text}")
        
        return jsonify({
            'success': True,
            'response': response.text,
            'timestamp': None
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"Chatbot error details: {error_msg}")
        print(f"Error type: {type(e).__name__}")
        
        # Return more detailed error for debugging
        return jsonify({
            'success': False,
            'error': f'API Error: {error_msg}',
            'details': f'Check if API key is valid. Error type: {type(e).__name__}'
        }), 500

@chat_bp.route('/test', methods=['GET'])
def test_api():
    """Test endpoint to verify Gemini API is configured"""
    try:
        if GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY_HERE':
            return jsonify({
                'success': False,
                'message': 'Please configure your Gemini API key in chat_routes.py or as GEMINI_API_KEY environment variable'
            }), 500
        
        # Simple test
        model = genai.GenerativeModel('gemma-3-4b-it')
        response = model.generate_content("Say 'Hello, Smart Farming!' in one sentence.")
        
        return jsonify({
            'success': True,
            'message': 'Gemini API is configured correctly!',
            'test_response': response.text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Gemini API test failed',
            'error': str(e)
        }), 500
