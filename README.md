# Claude AI Assistant

A modern, ChatGPT-style web interface for interacting with Claude AI through the AgentRouter API. This application provides a beautiful, responsive UI with conversation management, settings configuration, and real-time chat functionality.

## Features

### 🎨 Modern UI/UX
- **ChatGPT-inspired design** with dark theme
- **Responsive layout** that works on desktop and mobile
- **Sidebar navigation** for conversation management
- **Real-time status indicators** and loading states
- **Smooth animations** and hover effects

### 💬 Chat Functionality
- **Multi-conversation support** with persistent history
- **Real-time messaging** with Claude AI
- **Message timestamps** and role indicators
- **Auto-scrolling** to latest messages
- **Keyboard shortcuts** (Ctrl+Enter to send)

### ⚙️ Configuration
- **Settings panel** for API configuration
- **Multiple Claude models** support (Opus, Sonnet, Haiku)
- **Customizable parameters** (max tokens, base URL)
- **Secure token storage** with masked input

### 🔧 Technical Features
- **Flask backend** with RESTful API
- **Session-based** conversation storage
- **Error handling** with user-friendly messages
- **Background processing** for API calls
- **Configuration persistence** across sessions

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd claude-ai-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Configuration

### API Setup
1. Click the **Settings** button in the sidebar
2. Enter your AgentRouter API details:
   - **Base URL**: `https://agentrouter.org`
   - **Auth Token**: Your API token
   - **Model**: Choose from Claude 3 Opus, Sonnet, or Haiku
   - **Max Tokens**: Maximum response length (1-4000)

### Getting an API Token
1. Visit [AgentRouter](https://agentrouter.org)
2. Sign up for an account
3. Generate an API token
4. Enter the token in the settings panel

## Usage

### Starting a New Chat
- Click the **"+ New Chat"** button in the sidebar
- Or use the **File > New Chat** menu option

### Sending Messages
- Type your message in the input field
- Press **Ctrl+Enter** or click **Send** to send
- Regular **Enter** creates new lines in the textarea

### Managing Conversations
- View recent chats in the sidebar
- Click on any conversation to switch to it
- Conversations are automatically saved

### Settings
- Access settings via the **⚙️ Settings** button
- Configure API parameters
- Settings are automatically saved

## File Structure

```
claude-ai-assistant/
├── app.py                 # Flask backend application
├── py.py                  # Original Tkinter version (legacy)
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main web interface
└── README.md             # This file
```

## API Endpoints

### Chat
- `POST /api/chat` - Send a message to Claude
- `GET /api/conversations` - Get all conversations
- `GET /api/conversations/<id>` - Get specific conversation
- `POST /api/conversations` - Create new conversation

### Settings
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **API**: AgentRouter Claude API
- **Styling**: Custom CSS with modern design patterns
- **Storage**: Flask sessions (in-memory)

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Development

### Running in Development Mode
```bash
python app.py
```
The app runs in debug mode by default with auto-reload enabled.

### Production Deployment
For production, use a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the GitHub Issues page
2. Review the documentation
3. Contact the maintainers

---

**Note**: This application requires a valid AgentRouter API token to function. Make sure to configure your API settings before using the chat functionality.