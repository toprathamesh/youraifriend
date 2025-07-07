<div align="center">
  <img src="https://raw.githubusercontent.com/Tavishi-Ananad/Your-AI-Friend/main/assets/logo.png" alt="Your AI Friend Logo" width="150">
  <h1>Your AI Friend</h1>
  <p>
    <strong>A smart, conversational AI assistant with persistent memory, powered by Google's Gemini 2.5 Flash model.</strong>
  </p>
  <p>
    <em>Your AI Friend is designed to remember your conversations and provide a personalized experience, just like a real friend.</em>
  </p>
  <br>
    <img alt="Python" src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python">
    <img alt="Flask" src="https://img.shields.io/badge/Flask-black?style=for-the-badge&logo=flask">
    <img alt="Vercel" src="https://img.shields.io/badge/Vercel-black?style=for-the-badge&logo=vercel">
    <img alt="License" src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge">
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/Tavishi-Ananad/Your-AI-Friend/main/assets/screenshot.png" alt="Your AI Friend Screenshot" width="800">
</div>

## ✨ Features

- **🧠 Personalized Conversations**: Remembers details from your chats to make every interaction unique.
- **💾 Persistent Memory**: Securely stores conversation history and user information in a local SQLite database.
- **✍️ Editable Memory**: View, add, edit, or delete memories through an intuitive UI.
- **🎭 Selectable Personalities**: Choose from different AI personalities (e.g., Loving, Funny, Honest) to match your mood.
- **📄 Document Analysis**: Upload PDF documents and ask questions about their content.
- **🗂️ Session Management**: Organizes chats into separate, manageable sessions.
- **📱 Modern & Responsive UI**: A clean, ChatGPT-style interface that works beautifully on any device.
- **🚀 Powered by Gemini 2.5 Flash**: Utilizes Google's latest and most efficient AI model for fast and accurate responses.
- **☁️ Easy to Deploy**: Ready for deployment on Vercel with just a few clicks.

## 🛠️ Tech Stack

- **Backend**: Python (Flask)
- **AI Model**: Google Gemini 2.5 Flash
- **Database**: SQLite
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
    git clone https://github.com/Tavishi-Ananad/Your-AI-Friend.git
    cd Your-AI-Friend
    ```

2.  **Install dependencies:**
    ```bash
    python -m pip install -r requirements.txt
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

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FTavishi-Ananad%2FYour-AI-Friend)

1.  **Click the Deploy Button**: Click the "Deploy with Vercel" button above.
2.  **Import to Vercel**: It will automatically clone the repository and configure the project for you.
3.  **Add Environment Variable**: Go to your project's **Settings > Environment Variables** in Vercel and add your `GEMINI_API_KEY`.
4.  **Deploy**: Vercel will automatically deploy your project.

## ⚙️ API Endpoints

The application exposes the following RESTful API endpoints for managing the chat and memory:

| Method   | Endpoint              | Description                                        |
|----------|-----------------------|----------------------------------------------------|
| `GET`    | `/`                   | Serves the main chat interface.                    |
| `POST`   | `/chat`               | Handles chat messages and AI responses.            |
| `GET`    | `/history`            | Retrieves the conversation history for a session.  |
| `GET`    | `/conversations`      | Retrieves all conversation sessions.               |
| `GET`    | `/memory`             | Fetches all stored user memories.                  |
| `POST`   | `/memory`             | Adds a new memory item.                            |
| `PUT`    | `/memory/edit`        | Updates an existing memory item.                   |
| `DELETE` | `/memory`             | Deletes a specified memory item.                   |
| `POST`   | `/analyze_document`   | Analyzes an uploaded PDF document.                 |


## 🤝 Contributing

Contributions are welcome! Please feel free to fork the repository, make your changes, and submit a pull request.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. 