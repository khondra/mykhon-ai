# 🤖 MyKhon AI Assistant

A multi-functional AI chatbot built with Streamlit and Ollama, supporting multiple AI modes and bilingual support (English & Khmer).

## Features

- **💬 Q&A** - Ask questions and get intelligent answers
- **✍️ Prompt Generator** - Transform ideas into professional AI prompts
- **📰 Article Writer** - Generate high-quality articles on any topic
- **🌐 Khmer ↔ English Translation** - Seamless bilingual translation

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running locally
- Ollama model: `qwen3:4b` (or modify MODEL in the code)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/khondra/mykhon-ai.git
cd mykhon-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure Ollama is running:
```bash
ollama serve
```

In another terminal, pull the model:
```bash
ollama pull qwen3:4b
```

## Running Locally

```bash
streamlit run "My AI.py"
```

The app will open at `http://localhost:8501`

## Deployment Options

### Option 1: Streamlit Cloud (Recommended)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app" and select your repository
5. Set main file path to: `My AI.py`
6. Deploy!

**Note:** Streamlit Cloud won't have Ollama. You'll need to use an API instead.

### Option 2: Heroku

1. Add `Procfile`:
```
web: streamlit run "My AI.py" --server.port=$PORT --server.address=0.0.0.0
```

2. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Option 3: Docker (Local or Cloud)

1. Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD streamlit run "My AI.py" --server.port=8501 --server.address=0.0.0.0
```

2. Build and run:
```bash
docker build -t mykhon-ai .
docker run -p 8501:8501 mykhon-ai
```

### Option 4: Railway, Render, or Hugging Face Spaces

- Connect your GitHub repo
- Set start command: `streamlit run "My AI.py"`
- Deploy!

## Configuration

Edit `My AI.py` to change:
- `MODEL`: Change the Ollama model used
- `SYSTEM_PROMPTS`: Customize AI behavior for each mode
- `DB_NAME`: Change database filename

## Database

The app uses SQLite (`chatbot.db`) to store:
- User accounts (email & hashed passwords)
- Conversation history

## Security Notes

- Passwords are hashed with PBKDF2-SHA256 (600,000 iterations)
- Each user can only see their own conversation history
- Change `PASSWORD_HASH_ITERATIONS` if needed for security updates

## Troubleshooting

**Error: "Could not connect to Ollama"**
- Ensure Ollama is running: `ollama serve`
- Check Ollama is listening on `http://localhost:11434`

**Error: "Model not found"**
- Pull the model: `ollama pull qwen3:4b`
- Or modify `MODEL` variable to use a different model

**Port already in use**
- Change port in `.streamlit/config.toml` or:
```bash
streamlit run "My AI.py" --server.port 8502
```

## License

MIT

## Author

khondra
