# Your AI Friend

**A smart, conversational AI assistant powered by Google's Gemini 2.5 Flash model. This assistant can remember your conversations and extract key information to provide a personalized experience.**

<div align="center">
    <img alt="Python" src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python">
    <img alt="Flask" src="https://img.shields.io/badge/Flask-black?style=for-the-badge&logo=flask">
    <img alt="Vercel" src="https://img.shields.io/badge/Vercel-black?style=for-the-badge&logo=vercel">
</div>

## ✨ Features

- **🧠 Conversational Memory**: Remembers past conversations within a session to provide context-aware responses.
- **✍️ Automatic Fact Extraction**: Intelligently extracts key facts (like name, work, preferences) from your messages. This profile is managed client-side to personalize interactions.
- **🎭 Selectable Personalities**: Choose from different AI personalities (e.g., Loving, Funny, Honest) to match your mood.
- **📄 Document Analysis**: Upload PDF and TXT documents and ask questions about their content.
- **🗂️ Session Management**: Organizes chats into separate, manageable sessions stored in a local SQLite database.
- **🚀 Powered by Gemini 2.5 Flash**: Utilizes Google's latest and most efficient AI model for fast and accurate responses.
- **☁️ Vercel-Ready**: Optimized for easy deployment on Vercel.

## 🛠️ Tech Stack

- **Backend**: Python (Flask)
- **AI Model**: Google Gemini 2.5 Flash
- **Database**: SQLite (for conversation history)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Vercel

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

- Python 3.11+
- A Google Gemini API Key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/toprathamesh/youraifriend.git
    cd youraifriend
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your environment variables:**
    Create a `.env` file in the root of your project and add your Gemini API key:
    ```env
    GEMINI_API_KEY="your_gemini_api_key_here"
    ```

4.  **Run the application:**
    ```bash
    flask run
    ```
    The application will be available at `http://127.0.0.1:5000`.

## 📦 Deployment

This project is optimized for deployment on Vercel.

1.  Fork the repository to your GitHub account.
2.  Go to [Vercel](https://vercel.com) and create a new project.
3.  Import your forked repository.
4.  Vercel will automatically detect that it is a Python (Flask) project.
5.  Go to your project's **Settings > Environment Variables** in Vercel and add your `GEMINI_API_KEY`.
6.  Deploy. Vercel will handle the rest.

## ⚙️ API Endpoints

The application exposes the following RESTful API endpoints:

| Method   | Endpoint              | Description                                        |
|----------|-----------------------|----------------------------------------------------|
| `GET`    | `/`                   | Serves the main chat interface.                    |
| `POST`   | `/chat`               | Handles chat messages and AI responses.            |
| `GET`    | `/history`            | Retrieves the conversation history for a session.  |
| `GET`    | `/conversations`      | Retrieves all conversation sessions.               |
| `POST`   | `/analyze_document`   | Analyzes an uploaded PDF or TXT document.          |

## 🤝 Contributing

Contributions are welcome! Please feel free to fork the repository, make your changes, and submit a pull request. 