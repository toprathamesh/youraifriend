import os
import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from google.generativeai import types
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
# The model will be dynamically selected in the chat function
model = None

# --- Constants ---
PERSONALITY_PROMPTS = {
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
    - For image requests, describe the generated image in a warm, personal way.
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
    - If you generate an image, make a witty or funny comment about it.
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
    - For image requests, provide a straightforward description of the generated image.
    - Never use emojis in your responses.
    
    Please respond as Your AI Friend who is unapologetically honest and direct:
    """,
    "default": """
    You are a helpful AI assistant. Provide clear and direct answers.
    - Respond concisely and accurately.
    - Do not use any personality or conversational filler.
    - Get straight to the point.
    - If you generate an image, describe it factually.
    """
}

class MemoryManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # For Vercel deployment, use /tmp directory
            db_path = '/tmp/chat_memory.db' if os.environ.get('VERCEL') else 'chat_memory.db'
        self.db_path = db_path
        self.init_database()

    def get_db_connection(self):
        """Creates and returns a database connection and cursor."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn, conn.cursor()

    def close_db_connection(self, conn):
        """Commits changes and closes the database connection."""
        conn.commit()
        conn.close()

    def init_database(self):
        """Initialize the SQLite database for storing conversations"""
        conn, cursor = self.get_db_connection()
        
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
        
        self.close_db_connection(conn)
    
    def save_conversation(self, user_message, assistant_response, session_id='default'):
        """Save a conversation to the database"""
        conn, cursor = self.get_db_connection()
        
        cursor.execute('''
            INSERT INTO conversations (user_message, assistant_response, session_id)
            VALUES (?, ?, ?)
        ''', (user_message, assistant_response, session_id))
        
        self.close_db_connection(conn)
    
    def get_conversation_history(self, session_id='default', limit=50):
        """Get recent conversation history"""
        conn, cursor = self.get_db_connection()
        
        cursor.execute('''
            SELECT user_message, assistant_response, timestamp
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, limit))
        
        conversations = cursor.fetchall()
        self.close_db_connection(conn)
        
        return list(reversed(conversations))
    
    def update_user_info(self, key, value):
        """Update user profile information"""
        conn, cursor = self.get_db_connection()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_profile (key, value, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        
        self.close_db_connection(conn)
    
    def get_user_info(self, key=None):
        """Get user profile information"""
        conn, cursor = self.get_db_connection()
        
        if key:
            cursor.execute('SELECT value FROM user_profile WHERE key = ?', (key,))
            result = cursor.fetchone()
            self.close_db_connection(conn)
            return result['value'] if result else None
        else:
            cursor.execute('SELECT key, value FROM user_profile')
            results = cursor.fetchall()
            self.close_db_connection(conn)
            return {row['key']: row['value'] for row in results}
    
    def delete_user_info(self, key):
        """Delete user profile information"""
        conn, cursor = self.get_db_connection()
        
        cursor.execute('DELETE FROM user_profile WHERE key = ?', (key,))
        
        self.close_db_connection(conn)

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

def create_context_prompt(user_message, conversation_history, user_profile, personality='loving', is_image_request=False):
    """Create a context-rich prompt for Gemini"""
    
    # Select personality prompt
    personality_prompt = PERSONALITY_PROMPTS.get(personality, PERSONALITY_PROMPTS['loving'])
    
    # Build conversation context
    context_parts = []

    if is_image_request:
        context_parts.append("Image Generation Instructions:")
        context_parts.append("- You are creating a new image based on the user's request.")
        context_parts.append("- Interpret the user's description creatively and generate a high-quality, relevant image.")
        context_parts.append("- After generating, provide a brief, engaging text description of the image, matching your personality.")
        context_parts.append("")

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
    
    full_prompt = personality_prompt + "\n\n" + "\n".join(context_parts)
    return full_prompt

@app.route('/')
def index():
    """Serve the chat interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id', 'default')
    personality = data.get('personality', 'default')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Detect image generation request
    image_keywords = ['image', 'picture', 'photo', 'generate']
    is_image_request = any(keyword in user_message.lower() for keyword in image_keywords)

    # Select model based on request type
    if is_image_request:
        model = genai.GenerativeModel('gemini-2.0-flash-preview-image-generation')
    else:
        model = genai.GenerativeModel('gemini-2.5-flash')

    # Extract memories from the new message
    extracted_info = extract_memory_from_message(user_message)
    if extracted_info:
        for key, value in extracted_info.items():
            memory.update_user_info(key, value)

    # Get context
    conversation_history = memory.get_conversation_history(session_id)
    user_profile = memory.get_user_info()

    # Create a rich prompt
    prompt = create_context_prompt(user_message, conversation_history, user_profile, personality, is_image_request)

    try:
        if is_image_request:
            # Generate both text and image
            response = model.generate_content(
                [prompt, user_message],
                generation_config=genai.types.GenerationConfig(
                    response_modalities=["TEXT", "IMAGE"]
                )
            )
            assistant_response = response.candidates[0].content.parts[0].text
            image_data = response.candidates[0].content.parts[1].image.data
        else:
            # Generate text only
            chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [prompt]
                    }
                ]
            )
            response = chat_session.send_message(user_message)
            assistant_response = response.text

        # Save conversation
        memory.save_conversation(user_message, assistant_response, session_id)

        if is_image_request:
            return jsonify({
                "response": assistant_response,
                "image_data": image_data.decode('utf-8')
            })
        else:
            return jsonify({"response": assistant_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@app.route('/analyze_document', methods=['POST'])
def analyze_document():
    """Analyzes an uploaded document"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    prompt = request.form.get('prompt', 'Summarize this document.')
    session_id = request.form.get('session_id', 'default')
    
    if file:
        try:
            # For simplicity, we'll read the file as text.
            # In a real-world scenario, you might need libraries like pdfplumber for PDFs
            # or python-docx for DOCX files.
            document_text = file.read().decode('utf-8', errors='replace')
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            analysis_prompt = f"""
            Analyze the following document based on the prompt below.
            
            Prompt: "{prompt}"
            
            Document:
            ---
            {document_text}
            ---
            """
            
            response = model.generate_content(analysis_prompt)
            assistant_response = response.text
            
            # Save the interaction to history
            user_request_text = f"Analyzed document '{file.filename}': {prompt}"
            memory.save_conversation(user_request_text, assistant_response, session_id)

            return jsonify({'response': assistant_response})

        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'File processing failed'}), 500

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