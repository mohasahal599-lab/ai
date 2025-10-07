from flask import Flask, render_template, request, jsonify, session
import requests
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Configuration
class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "base_url": "https://agentrouter.org",
            "auth_token": "",
            "model": "claude-3-opus-20240229",
            "max_tokens": 1000
        }
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.config = {**self.default_config, **config}
            else:
                self.config = self.default_config.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self.default_config.copy()

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key):
        return self.config.get(key, self.default_config.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

config = Config()

class AgentRouterClient:
    def __init__(self):
        self.base_url = config.get("base_url").rstrip('/')
        self.auth_token = config.get("auth_token")

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}"
        }

    def complete(self, prompt, model=None, max_tokens=None):
        if not self.auth_token:
            raise Exception("No authentication token provided. Please configure your API settings.")
        
        model = model or config.get("model")
        max_tokens = max_tokens or config.get("max_tokens")
        
        url = f"{self.base_url}/v1/complete"
        body = {
            "model": model,
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": max_tokens
        }

        try:
            resp = requests.post(url, headers=self._headers(), json=body, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

client = AgentRouterClient()

@app.route('/')
def index():
    if 'conversations' not in session:
        session['conversations'] = []
    if 'current_conversation_id' not in session:
        session['current_conversation_id'] = None
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    try:
        # Get or create current conversation
        conversations = session.get('conversations', [])
        current_id = session.get('current_conversation_id')
        
        if not current_id or not any(conv['id'] == current_id for conv in conversations):
            # Create new conversation
            conversation = {
                'id': str(uuid.uuid4()),
                'title': message[:50] + "..." if len(message) > 50 else message,
                'messages': [],
                'created_at': datetime.now().isoformat()
            }
            conversations.append(conversation)
            current_id = conversation['id']
            session['current_conversation_id'] = current_id
            session['conversations'] = conversations

        # Find current conversation
        current_conversation = next(conv for conv in conversations if conv['id'] == current_id)
        
        # Add user message
        user_message = {
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().strftime("%H:%M")
        }
        current_conversation['messages'].append(user_message)
        
        # Get AI response
        response = client.complete(message)
        ai_text = response.get("completion", "").strip()
        
        if not ai_text:
            ai_text = "I apologize, but I couldn't generate a response. Please try again."
        
        # Add AI message
        ai_message = {
            'role': 'assistant',
            'content': ai_text,
            'timestamp': datetime.now().strftime("%H:%M")
        }
        current_conversation['messages'].append(ai_message)
        
        # Update conversation title if it's the first message
        if len(current_conversation['messages']) == 2:  # user + ai
            current_conversation['title'] = message[:50] + "..." if len(message) > 50 else message
        
        session['conversations'] = conversations
        
        return jsonify({
            'response': ai_text,
            'conversation_id': current_id,
            'timestamp': ai_message['timestamp']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    conversations = session.get('conversations', [])
    return jsonify(conversations)

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    conversations = session.get('conversations', [])
    conversation = next((conv for conv in conversations if conv['id'] == conversation_id), None)
    
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    return jsonify(conversation)

@app.route('/api/conversations/<conversation_id>', methods=['POST'])
def set_current_conversation(conversation_id):
    conversations = session.get('conversations', [])
    conversation = next((conv for conv in conversations if conv['id'] == conversation_id), None)
    
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    session['current_conversation_id'] = conversation_id
    return jsonify({'success': True})

@app.route('/api/conversations', methods=['POST'])
def new_conversation():
    conversation = {
        'id': str(uuid.uuid4()),
        'title': 'New Chat',
        'messages': [],
        'created_at': datetime.now().isoformat()
    }
    
    conversations = session.get('conversations', [])
    conversations.append(conversation)
    session['conversations'] = conversations
    session['current_conversation_id'] = conversation['id']
    
    return jsonify(conversation)

@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify({
        'base_url': config.get('base_url'),
        'model': config.get('model'),
        'max_tokens': config.get('max_tokens')
    })

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.get_json()
    
    config.set('base_url', data.get('base_url', config.get('base_url')))
    config.set('model', data.get('model', config.get('model')))
    config.set('max_tokens', data.get('max_tokens', config.get('max_tokens')))
    
    # Update auth token if provided
    if 'auth_token' in data:
        config.set('auth_token', data['auth_token'])
    
    # Recreate client with new config
    global client
    client = AgentRouterClient()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)