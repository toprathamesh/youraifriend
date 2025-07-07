# Your AI Friend

Your AI Friend is a smart, conversational AI assistant with persistent memory, powered by Google's Gemini 2.5 Flash model. It's designed to remember your conversations and provide a personalized experience, just like a real friend.

![Your AI Friend Screenshot](https://i.imgur.com/your-screenshot.png) <!-- Replace with a real screenshot -->

## ✨ Features

- **Personalized Conversations**: Remembers details from your chats to make every interaction unique.
- **Persistent Memory**: Securely stores conversation history and user information in a local SQLite database.
- **Editable Memory**: View, add, edit, or delete memories through an intuitive UI.
- **Selectable Personalities**: Choose from different AI personalities (e.g., Loving, Funny, Honest) to match your mood.
- **Modern & Responsive UI**: A clean, ChatGPT-style interface that works beautifully on any device.
- **Powered by Gemini 2.5 Flash**: Utilizes Google's latest and most efficient AI model for fast and accurate responses.
- **Easy to Deploy**: Ready for deployment on Vercel with just a few clicks.

## 🛠️ Tech Stack

- **Backend**: Python (Flask)
- **AI Model**: Google Gemini 2.5 Flash
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Vercel

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

- Python 3.8+
- A Google Gemini API Key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/youraifriend.git
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

1.  **Push to GitHub**: Make sure your latest code is on a GitHub repository.
2.  **Import to Vercel**: Import your repository in Vercel. It will be automatically detected as a Python project.
3.  **Add Environment Variable**: Go to your project's **Settings > Environment Variables** in Vercel and add your `GEMINI_API_KEY`.
4.  **Deploy**: Vercel will automatically deploy your project.

## ⚙️ API Endpoints

The application exposes the following RESTful API endpoints for managing the chat and memory:

| Method   | Endpoint         | Description                               |
|----------|------------------|-------------------------------------------|
| `GET`    | `/`              | Serves the main chat interface.           |
| `POST`   | `/chat`          | Handles chat messages and AI responses.   |
| `GET`    | `/history`       | Retrieves the full conversation history.  |
| `GET`    | `/memory`        | Fetches all stored user memories.         |
| `POST`   | `/memory`        | Adds a new memory item.                   |
| `PUT`    | `/memory/edit`   | Updates an existing memory item.          |
| `DELETE` | `/memory`        | Deletes a specified memory item.          |

## 🤝 Contributing

Contributions are welcome! Please feel free to fork the repository, make your changes, and submit a pull request.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. 