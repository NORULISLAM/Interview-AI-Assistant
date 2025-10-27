# Interview AI Assistant

A real-time, personalized interview assistant leveraging speech recognition, large language models, and experience-based personalization.

## Features

- Real-time transcription and instant AI-generated answers for interview questions
- Resume upload and parsing for personalized responses
- Seamless integration with video platforms (Zoom, Google Meet, Teams)
- Invisible overlay for displaying suggestions during interviews
- Privacy-conscious with end-to-end encryption and automatic transcript deletion

## Architecture

- **Backend**: FastAPI with PostgreSQL, Redis, and Qdrant vector database
- **ASR**: Faster-Whisper for real-time speech recognition
- **LLM**: OpenAI GPT-4o mini for response generation
- **Frontend**: Electron desktop app and browser extension
- **Storage**: Encrypted S3 for resumes and transcripts

## Project Structure

```
├── backend/                 # FastAPI backend services
├── frontend/               # Electron desktop app
├── extension/              # Browser extension
├── shared/                 # Shared types and utilities
├── docker-compose.yml      # Development environment
└── README.md
```

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run `docker-compose up` for development environment
4. Install dependencies: `npm install` (frontend) and `pip install -r backend/requirements.txt`

## Development

- Backend API runs on `http://localhost:8000`
- Frontend Electron app runs on `http://localhost:3000`
- Browser extension loads from `extension/` directory

## Privacy & Security

- End-to-end encryption for all data
- Automatic transcript deletion (configurable retention)
- GDPR compliant data handling
- Zero-retention mode available

