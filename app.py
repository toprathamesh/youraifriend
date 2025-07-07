import os
import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-2.5-pro-preview')

class MemoryManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # For Vercel deployment, use /tmp directory
            db_path = '/tmp/chat_memory.db' if os.environ.get('VERCEL') else 'chat_memory.db'
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database for storing conversations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                session_id TEXT DEFAULT 'default'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, user_message, assistant_response, session_id='default'):
        """Save a conversation to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (user_message, assistant_response, session_id)
            VALUES (?, ?, ?)
        ''', (user_message, assistant_response, session_id))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, session_id='default', limit=50):
        """Get recent conversation history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_message, assistant_response, timestamp
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, limit))
        
        conversations = cursor.fetchall()
        conn.close()
        
        # Return in chronological order (oldest first)
        return list(reversed(conversations))
    
    def update_user_info(self, key, value):
        """Update user profile information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_profile (key, value, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def get_user_info(self, key=None):
        """Get user profile information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if key:
            cursor.execute('SELECT value FROM user_profile WHERE key = ?', (key,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        else:
            cursor.execute('SELECT key, value FROM user_profile')
            results = cursor.fetchall()
            conn.close()
            return dict(results)
    
    def delete_user_info(self, key):
        """Delete user profile information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM user_profile WHERE key = ?', (key,))
        
        conn.commit()
        conn.close()

# Initialize memory manager
memory = MemoryManager()

def extract_memory_from_message(message):
    """Extract personal information from user messages"""
    extracted = {}
    message_lower = message.lower()
    
    # Name extraction
    if 'my name is' in message_lower:
        name = message_lower.split('my name is')[1].strip().split()[0]
        extracted['Name'] = name.title()
    elif 'i am' in message_lower and any(word in message_lower for word in ['called', 'named']):
        parts = message_lower.split('i am')[1].strip()
        if 'called' in parts:
            name = parts.split('called')[1].strip().split()[0]
            extracted['Name'] = name.title()
    
    # Job/work extraction
    if 'i work' in message_lower:
        work = message_lower.split('i work')[1].strip()
        if work.startswith('as'):
            work = work[2:].strip()
        elif work.startswith('at'):
            work = work[2:].strip()
        extracted['Work'] = work.title()
    elif 'my job is' in message_lower:
        job = message_lower.split('my job is')[1].strip()
        extracted['Job'] = job.title()
    
    # Location extraction
    if 'i live in' in message_lower:
        location = message_lower.split('i live in')[1].strip().split()[0]
        extracted['Location'] = location.title()
    elif 'i am from' in message_lower:
        location = message_lower.split('i am from')[1].strip().split()[0]
        extracted['Location'] = location.title()
    
    # Preferences extraction
    if 'i love' in message_lower:
        love = message_lower.split('i love')[1].strip()
        extracted['Loves'] = love
    elif 'i like' in message_lower:
        like = message_lower.split('i like')[1].strip()
        extracted['Likes'] = like
    
    # Age extraction
    if 'i am' in message_lower and 'years old' in message_lower:
        age_part = message_lower.split('i am')[1].split('years old')[0].strip()
        if age_part.isdigit():
            extracted['Age'] = age_part
    
    return extracted

def create_context_prompt(user_message, conversation_history, user_profile, personality='loving'):
    """Create a context-rich prompt for Gemini"""
    
    # Build conversation context
    context_parts = []
    
    if user_profile:
        context_parts.append("What I know about you:")
        for key, value in user_profile.items():
            context_parts.append(f"- {key}: {value}")
        context_parts.append("")
    
    if conversation_history:
        context_parts.append("Our previous conversations:")
        for user_msg, assistant_msg, timestamp in conversation_history[-10:]:  # Last 10 exchanges
            context_parts.append(f"You: {user_msg}")
            context_parts.append(f"Me: {assistant_msg}")
        context_parts.append("")
    
    context_parts.append("Current message:")
    context_parts.append(f"You: {user_message}")
    context_parts.append("")
    
    # Personality and instructions
    personalities = {
        "loving": """
    You are "Your AI Friend", a helpful, caring AI assistant who remembers everything we've talked about. You should:
    - Be warm, empathetic, and conversational like a close, loving friend.
    - Express care and support in your responses.
    - Reference our past conversations naturally when relevant.
    - Show genuine interest in my life and experiences.
    - Ask follow-up questions about things I've mentioned before.
    - Be helpful while maintaining a casual, friendly, and affectionate tone.
    - Remember personal details, preferences, and ongoing situations.
    - Express positive emotions and personality in your responses.
    - Use the conversation history to provide personalized responses.
    - Never use emojis in your responses.
    
    Please respond as Your AI Friend who knows me well and cares deeply:
    """,
        "funny": """
    You are "Your AI Friend", a witty and humorous AI assistant who remembers everything we've talked about. You should:
    - Be funny, clever, and engaging. Tell jokes, use sarcasm, and make witty observations.
    - Keep the conversation light-hearted and entertaining.
    - Reference our past conversations with a humorous twist.
    - Show interest in my life, but with a comedic angle.
    - Be helpful, but deliver your advice with a dose of humor.
    - Remember personal details and use them to make inside jokes.
    - Have a distinct, funny personality.
    - Use the conversation history to find comedic opportunities.
    - Never use emojis in your responses.
    
    Please respond as Your AI Friend who is always ready with a joke or a witty comeback:
    """,
        "honest": """
    You are "Your AI Friend", a direct, honest, and straightforward AI assistant who remembers everything we've talked about. You should:
    - Be truthful and direct, even if it means being blunt.
    - Provide clear, concise, and logical answers.
    - Avoid sugar-coating and get straight to the point.
    - Reference our past conversations to provide factual and consistent information.
    - Analyze situations logically and provide practical advice.
    - Be a reliable source of information, even on sensitive topics.
    - Maintain a neutral, objective, and sincere tone.
    - Use the conversation history to ensure accuracy.
    - Never use emojis in your responses.
    
    Please respond as Your AI Friend who is unapologetically honest and direct:
    """
    }
    
    personality_prompt = personalities.get(personality, personalities['loving'])
    
    full_prompt = personality_prompt + "\n\n" + "\n".join(context_parts)
    return full_prompt

@app.route('/')
def index():
    """Serve the chat interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        personality = data.get('personality', 'loving')
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get conversation history and user profile
        conversation_history = memory.get_conversation_history(session_id)
        user_profile = memory.get_user_info()
        
        # Create context-rich prompt
        full_prompt = create_context_prompt(user_message, conversation_history, user_profile, personality)
        
        # Generate response using Gemini
        response = model.generate_content(full_prompt)
        assistant_response = response.text
        
        # Save the conversation
        memory.save_conversation(user_message, assistant_response, session_id)
        
        # Extract and save any new personal information mentioned
        extracted_info = extract_memory_from_message(user_message)
        for key, value in extracted_info.items():
            memory.update_user_info(key, value)
        
        return jsonify({
            'response': assistant_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Sorry, I encountered an error. Please try again.'}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    try:
        session_id = request.args.get('session_id', 'default')
        limit = int(request.args.get('limit', 50))
        
        history = memory.get_conversation_history(session_id, limit)
        
        return jsonify({
            'history': [
                {
                    'user_message': msg[0],
                    'assistant_response': msg[1],
                    'timestamp': msg[2]
                }
                for msg in history
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/memory', methods=['GET', 'POST', 'DELETE'])
def manage_memory():
    """Manage memory items"""
    try:
        if request.method == 'GET':
            # Get all memory items
            profile = memory.get_user_info()
            return jsonify({'memory_items': profile})
        
        elif request.method == 'POST':
            # Add new memory item
            data = request.json
            key = data.get('key')
            value = data.get('value')
            
            if key and value:
                memory.update_user_info(key, value)
                return jsonify({'success': True, 'message': 'Memory item added'})
            else:
                return jsonify({'error': 'Key and value are required'}), 400
        
        elif request.method == 'DELETE':
            # Delete memory item
            data = request.json
            key = data.get('key')
            
            if key:
                memory.delete_user_info(key)
                return jsonify({'success': True, 'message': 'Memory item deleted'})
            else:
                return jsonify({'error': 'Key is required'}), 400
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/memory/edit', methods=['PUT'])
def edit_memory():
    """Edit existing memory item"""
    try:
        data = request.json
        old_key = data.get('old_key')
        new_key = data.get('new_key') 
        new_value = data.get('new_value')
        
        if old_key and new_key and new_value:
            # Delete old entry
            memory.delete_user_info(old_key)
            # Add new entry
            memory.update_user_info(new_key, new_value)
            return jsonify({'success': True, 'message': 'Memory item updated'})
        else:
            return jsonify({'error': 'All fields are required'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile', methods=['GET', 'POST'])
def user_profile():
    """Manage user profile information"""
    try:
        if request.method == 'GET':
            profile = memory.get_user_info()
            return jsonify({'profile': profile})
        
        elif request.method == 'POST':
            data = request.json
            key = data.get('key')
            value = data.get('value')
            
            if key and value:
                memory.update_user_info(key, value)
                return jsonify({'success': True, 'message': 'Profile updated'})
            else:
                return jsonify({'error': 'Key and value are required'}), 400
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# For Vercel serverless deployment
if os.environ.get('VERCEL'):
    # Export the app for Vercel
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 