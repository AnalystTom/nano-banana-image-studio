# Nano Banana Image Studio

AI-powered image generation, management, and editing studio powered by Gemini's Nano Banana API.

## Features

- **Image Generation**: Generate images from text prompts with configurable models, aspect ratios, and resolutions
- **Image Editing**: Edit existing images with conversational prompts
- **Multi-Turn Sessions**: Create sessions for iterative image refinement with conversation history
- **Gallery Management**: Browse, filter, and manage generated images
- **Prompt Templates**: Pre-built templates for common use cases
- **Settings**: Configure default preferences for generation

## Tech Stack

- **Frontend**: Vue 3 + TypeScript + Vite + Pinia
- **Backend**: FastAPI + Python (uv)
- **Database**: SQLite

## Project Structure

```
├── backend/
│   ├── src/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── config.py        # Settings and env vars
│   │   ├── database.py      # SQLite setup and models
│   │   ├── models.py        # Pydantic models
│   │   ├── routers/         # API endpoints
│   │   └── services/        # Business logic
│   └── static/images/       # Generated images storage
├── frontend/
│   ├── src/
│   │   ├── views/           # Page components
│   │   ├── stores/          # Pinia stores
│   │   ├── services/        # API client
│   │   └── types/           # TypeScript types
│   └── vite.config.ts
└── database.db
```

## Requirements

- Node.js 20+
- Python 3.11+
- uv (Python package manager)

## Setup

### Backend

```bash
cd backend
uv sync
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## Environment Variables

Create a `.env` file in the backend directory:

```
GEMINI_API_KEY=your_api_key_here
```

Note: If no API key is provided, the app will use mock image generation.

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/generate` - Generate image from prompt
- `POST /api/edit` - Edit existing image
- `GET/POST /api/sessions` - Session management
- `GET /api/images` - List images with filtering
- `GET/PUT /api/settings` - Settings management
- `GET /api/templates` - Prompt templates

## License

MIT
