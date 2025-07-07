# Your AI Friend

A ChatGPT-style AI assistant powered by Google's Gemini 2.0 Flash model with persistent memory capabilities. Features a modern, responsive interface with real-time memory management.

## Features

- **ChatGPT-style Interface**: Polished chat bubbles, smooth animations, and professional design
- **Intelligent Memory System**: Automatically detects and saves personal information from conversations
- **Real-time Memory Management**: Add, edit, and delete memory entries with live updates
- **Latest AI Model**: Powered by Google Gemini 2.0 Flash Experimental
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Persistent Conversations**: SQLite database stores all chat history and user memories

## Local Development

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/toprathamesh/youraifriend.git
cd youraifriend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Run the application:
```bash
python app.py
```

5. Open your browser to `http://localhost:5000`

## Deployment on Vercel

### Step 1: Deploy to Vercel

1. Fork this repository to your GitHub account
2. Go to [Vercel](https://vercel.com) and sign in with your GitHub account
3. Click "New Project" and import your forked repository
4. Vercel will automatically detect it's a Python project

### Step 2: Configure Environment Variables

**IMPORTANT**: Do not commit your API key to GitHub. Instead, add it securely in Vercel:

1. In your Vercel project dashboard, go to **Settings** → **Environment Variables**
2. Add a new environment variable:
   - **Name**: `GEMINI_API_KEY`
   - **Value**: `your_actual_gemini_api_key_here`
   - **Environments**: Select all (Production, Preview, Development)
3. Click **Save**

### Step 3: Deploy

1. Vercel will automatically deploy your application
2. Your app will be available at `https://your-project-name.vercel.app`

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key
5. Add it to your Vercel environment variables (never commit it to code!)

## Project Structure

```
youraifriend/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Frontend interface
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel deployment configuration
├── .gitignore           # Git ignore file (includes .env)
├── .env                 # Environment variables (not committed)
└── README.md           # This file
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes |

## Security Notes

- ✅ API keys are stored as environment variables
- ✅ `.env` file is in `.gitignore`
- ✅ No secrets are committed to the repository
- ✅ Database files are excluded from version control

## Technologies Used

- **Backend**: Flask (Python)
- **AI Model**: Google Gemini 2.0 Flash Experimental
- **Database**: SQLite
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Deployment**: Vercel
- **Styling**: Inter font, modern CSS animations

## API Endpoints

- `GET /` - Serve the chat interface
- `POST /chat` - Send message to AI and get response
- `GET /history` - Get conversation history
- `GET /memory` - Get all memory items
- `POST /memory` - Add new memory item
- `DELETE /memory` - Delete memory item
- `PUT /memory/edit` - Edit existing memory item

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues:

1. Check that your `GEMINI_API_KEY` is correctly set in Vercel environment variables
2. Ensure all dependencies are listed in `requirements.txt`
3. Check Vercel deployment logs for any errors
4. Make sure your Gemini API key has the necessary permissions

For additional help, please open an issue on GitHub. 