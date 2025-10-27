# 🚀 Interview AI Assistant - Quick Start Guide

## Prerequisites

Before starting, ensure you have installed:

- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download here](https://git-scm.com/)

## 🔑 Required API Keys

### 1. OpenAI API Key (REQUIRED)

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

### 2. Optional API Keys

- **Anthropic API Key** - For Claude models (optional)
- **AWS Credentials** - For cloud file storage (optional)

## ⚡ Quick Setup (Windows)

### Step 1: Clone and Setup

```bash
git clone <your-repo-url>
cd Inter
```

### Step 2: Configure Environment

```bash
# Copy environment file
copy env.example .env

# Edit .env file and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Step 3: Start Everything

```bash
# Start all services
start-dev.bat
```

## ⚡ Quick Setup (Linux/macOS)

### Step 1: Clone and Setup

```bash
git clone <your-repo-url>
cd Inter
```

### Step 2: Configure Environment

```bash
# Copy environment file
cp env.example .env

# Edit .env file and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Step 3: Start Everything

```bash
# Make script executable
chmod +x start-dev.sh

# Start all services
./start-dev.sh
```

## 🎯 What You'll Get

After running the setup, you'll have:

- **Backend API**: http://localhost:8000
- **Frontend App**: http://localhost:3000
- **ASR Service**: http://localhost:8001
- **API Documentation**: http://localhost:8000/docs

## 📱 Using the Application

### 1. Desktop Application

1. Open http://localhost:3000
2. Enter your email address
3. Check console for magic link (demo mode)
4. Upload a resume
5. Start an interview session

### 2. Browser Extension

1. Load extension in Chrome/Edge:
   - Go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `extension/` folder
2. Go to Google Meet/Teams/Zoom
3. Click extension icon and start recording

## 🔧 Manual Setup (If Needed)

If the automatic setup doesn't work:

### 1. Start Infrastructure

```bash
docker-compose up -d postgres redis qdrant
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
python app/main.py
```

### 3. ASR Service

```bash
cd backend
pip install -r requirements.asr.txt
python asr_service.py
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🎉 Features You Can Test

### ✅ Working Features

- **Real-time Speech Recognition** - Faster-Whisper integration
- **AI-powered Suggestions** - OpenAI GPT-4o mini
- **Resume Parsing** - PDF/DOCX with skill extraction
- **Desktop Overlay** - Electron invisible overlay
- **Browser Extension** - Chrome/Edge support
- **Magic Link Auth** - Passwordless authentication
- **Session Management** - Track interviews
- **Privacy Controls** - Auto-delete transcripts
- **Vector Search** - Resume content search
- **GDPR Compliance** - Data export/deletion

### 🧪 Test Scenarios

1. **Upload Resume**: Upload a PDF/DOCX resume
2. **Start Session**: Begin an interview session
3. **Real-time Transcription**: Speak and see live transcription
4. **AI Suggestions**: Get contextual interview tips
5. **Privacy Controls**: Test data retention settings
6. **Browser Extension**: Use on video call platforms

## 🛠️ Troubleshooting

### Common Issues

**Port already in use:**

```bash
# Kill processes using ports
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Docker issues:**

```bash
# Restart Docker Desktop
# Check if Docker is running
docker --version
```

**Python dependencies:**

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Node.js issues:**

```bash
# Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## 📊 Performance Tips

- **GPU Support**: Enable CUDA for faster ASR (requires NVIDIA GPU)
- **Memory**: Ensure 8GB+ RAM for optimal performance
- **Storage**: SSD recommended for faster file processing

## 🔒 Security Notes

- Change default encryption keys in production
- Use environment variables for all secrets
- Enable HTTPS in production
- Regularly update dependencies

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure API keys are correctly configured
4. Check console logs for error messages

## 🎯 Next Steps

Once everything is running:

1. Test all features
2. Upload your own resume
3. Try the browser extension
4. Explore the API documentation at `/docs`
5. Customize settings in the dashboard

**Happy interviewing! 🎉**
