# Interview AI Assistant - Setup Guide

This guide will help you set up and run the Interview AI Assistant application.

## Prerequisites

Before starting, ensure you have the following installed:

### Required Software

- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download here](https://git-scm.com/)

### API Keys

- **OpenAI API Key** - [Get from OpenAI](https://platform.openai.com/api-keys)

## Quick Start (Windows)

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Inter
   ```

2. **Set up environment variables**

   ```bash
   copy env.example .env
   ```

   Edit `.env` and add your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Start the application**
   ```bash
   start-dev.bat
   ```

## Quick Start (Linux/macOS)

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Inter
   ```

2. **Set up environment variables**

   ```bash
   cp env.example .env
   ```

   Edit `.env` and add your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Start the application**
   ```bash
   chmod +x start-dev.sh
   ./start-dev.sh
   ```

## Manual Setup

If you prefer to set up each component manually:

### 1. Start Infrastructure Services

```bash
docker-compose up -d postgres redis qdrant
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

# FastAPI

```
uvicorn main:app --reload

```

The backend API will be available at: http://localhost:8000

### 3. ASR Service Setup

```bash
cd backend
python asr_service.py
```

The ASR service will be available at: http://localhost:8001

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at: http://localhost:3000

## Browser Extension Setup

1. **Load the extension in Chrome/Edge:**

   - Open Chrome/Edge and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `extension` folder

2. **Pin the extension:**
   - Click the puzzle piece icon in the toolbar
   - Pin "Interview AI Assistant"

## Usage

### Desktop Application

1. **Start the Electron app:**

   ```bash
   cd frontend
   npm run dev:electron
   ```

2. **Login:**

   - Enter your email address
   - Check the console for the magic link (for demo purposes)
   - Click the magic link to authenticate

3. **Upload Resume:**

   - Go to the dashboard
   - Click "Choose File" under "Upload Resume"
   - Select your resume (PDF, DOC, DOCX)

4. **Start Interview Session:**
   - Click "Start Session"
   - The overlay will appear automatically
   - Use Ctrl+Shift+I to toggle overlay visibility

### Browser Extension

1. **Navigate to a video call:**

   - Go to Google Meet, Microsoft Teams, or Zoom
   - Join or start a meeting

2. **Activate the extension:**

   - Click the extension icon
   - Click "Connect to Service"
   - Click "Start Recording"

3. **View suggestions:**
   - AI suggestions will appear in the overlay
   - Use the extension popup to control recording

## Features

### ✅ Implemented Features

- **Real-time Speech Recognition** - Using Faster-Whisper
- **AI-powered Suggestions** - OpenAI GPT-4o mini integration
- **Resume Parsing** - PDF/DOCX parsing with skill extraction
- **Desktop Overlay** - Electron-based invisible overlay
- **Browser Extension** - Chrome/Edge extension for video calls
- **User Authentication** - Magic link authentication
- **Session Management** - Track interview sessions
- **Privacy Controls** - Auto-delete transcripts

### 🚧 Coming Soon

- **Vector Database Integration** - Qdrant for resume embeddings
- **Advanced Privacy Features** - End-to-end encryption
- **Multi-language Support** - Support for different languages
- **Custom AI Models** - Fine-tuned models for interviews

## API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Port already in use:**

   ```bash
   # Kill processes using ports 8000, 8001, 3000
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **Docker services not starting:**

   ```bash
   # Check Docker is running
   docker --version
   docker-compose --version
   ```

3. **Python dependencies issues:**

   ```bash
   # Create virtual environment
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

4. **Node.js dependencies issues:**
   ```bash
   # Clear npm cache
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

### Performance Issues

- **Slow ASR:** Ensure you have a GPU with CUDA support for faster transcription
- **High CPU usage:** The app uses multiple services; ensure your system has sufficient resources

## Development

### Project Structure

```
Inter/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   ├── main.py            # Main application entry
│   ├── asr_service.py     # ASR service
│   └── requirements.txt   # Python dependencies
├── frontend/              # Electron + React frontend
│   ├── src/              # React components
│   ├── electron/         # Electron main process
│   └── package.json      # Node.js dependencies
├── extension/            # Browser extension
├── docker-compose.yml    # Infrastructure services
└── README.md            # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:

- Check the troubleshooting section above
- Open an issue on GitHub
- Contact the development team

## License

This project is licensed under the MIT License - see the LICENSE file for details.
