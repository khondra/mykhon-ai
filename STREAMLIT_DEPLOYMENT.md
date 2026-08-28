# Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Cloud

Your MyKhon AI app is ready to deploy! Follow these steps:

### Step 1: Prepare Your Repository
✅ Your code is already pushed to GitHub at: https://github.com/khondra/mykhon-ai

### Step 2: Go to Streamlit Cloud
1. Open https://share.streamlit.io
2. Click **"New app"** button

### Step 3: Connect GitHub
1. Click **"Connect GitHub account"** (if not already connected)
2. Authorize Streamlit to access your repositories
3. Select repository: **khondra/mykhon-ai**
4. Select branch: **myai** (your default branch)
5. Set main file path: **My AI.py**

### Step 4: Deploy
- Click **"Deploy!"** button
- Wait 2-3 minutes for deployment to complete
- Streamlit will generate a public URL like: `https://mykhon-ai.streamlit.app`

---

## ⚠️ Important: Ollama Issue

Streamlit Cloud doesn't have Ollama installed. You need to use an AI API instead.

### Option A: Use OpenAI API (Recommended)
```python
# Install: pip install openai
import openai

openai.api_key = st.secrets["openai_api_key"]

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
)
```

### Option B: Use Ollama API Server
Host Ollama on a separate server (AWS, DigitalOcean, etc.) and connect to it.

### Option C: Use Other LLM APIs
- Anthropic Claude
- Google Gemini
- Hugging Face
- LocalAI

---

## Secrets Management

To safely add API keys on Streamlit Cloud:

1. Go to https://share.streamlit.io
2. Find your deployed app
3. Click **"⋯"** (three dots) → **"Settings"**
4. Go to **"Secrets"** tab
5. Add your secrets as TOML:
```toml
openai_api_key = "sk-..."
ollama_url = "http://your-server:11434"
```

These can be accessed in your app as:
```python
api_key = st.secrets["openai_api_key"]
```

---

## After Deployment

✅ Your app will be live at: `https://yourusername-mykhon-ai-xxxx.streamlit.app`

📱 Share the link with anyone
🔒 Choose public or private visibility in app settings
📊 Monitor logs and usage in Streamlit Cloud dashboard

---

## Troubleshooting

**Error: "Could not connect to Ollama"**
- Solution: Modify to use an API instead (see options above)

**Error: "Module not found"**
- Solution: Check `requirements.txt` has all dependencies

**App is slow**
- Solution: Reduce model size or use faster API

---

## Next Steps

Would you like me to:
1. ✏️ **Modify the app to use OpenAI API** instead of Ollama?
2. 📖 **Create detailed API integration guide**?
3. 🔑 **Setup secrets in Streamlit Cloud**?
