# Claude Development Guide - Nano Banana Image Studio

## Overview

Nano Banana Image Studio is an AI-powered image and video production platform that uses Google's Gemini and Imagen APIs for content generation.

## API Configuration

### Nano Banana API Integration

**IMPORTANT:** Always use the **Nano Banana API** for image generation, which is Google's Imagen API configured for the project.

#### Google Cloud Project
- **Project ID:** `august-sandbox-483210-c7`
- **API:** Google Generative AI (google-genai package)
- **Primary Model:** `imagen-3.0-generate-001`

#### Environment Variables

```bash
# Required
GEMINI_API_KEY=<your-api-key>

# Optional (defaults to august-sandbox-483210-c7)
GOOGLE_CLOUD_PROJECT=august-sandbox-483210-c7
```

### Image Generation Service

Located at: `backend/src/services/gemini.py`

#### Default Configuration

```python
from google import genai

# Initialize with Nano Banana project
GEMINI_CLIENT = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={'api_version': 'v1alpha'}
)
```

#### Image Generation Parameters

```python
await generate_image(
    prompt="Your prompt here",
    model="imagen-3.0-generate-001",  # Default model
    aspect_ratio="16:9",               # Supported: 1:1, 16:9, 9:16, 4:3, 3:4
    resolution="2K",                   # Used for mock mode
)
```

#### Supported Models

1. **imagen-3.0-generate-001** (Recommended)
   - Latest Imagen model
   - Best quality and detail
   - Supports person generation
   - Safety filtering options

2. **gemini-2.5-flash-image** (Alternative)
   - Faster generation
   - Lower cost
   - May have limited availability

### Mock Mode Fallback

When the API is unavailable or encounters errors, the system automatically falls back to **mock mode**:

- Generates gradient placeholder images
- Maintains full workflow functionality
- Marks images with `is_mock: true` flag
- Perfect for development and testing

## Video Production CLI

### Architecture

The CLI (`nb-studio`) uses a service-layer architecture:

```
CLI Commands (commands/*.py)
    ↓
Services (services/*.py)
    ↓
APIs (Nano Banana/Google Gemini)
```

### Services

1. **`gemini.py`** - Nano Banana API wrapper
   - Image generation via Imagen
   - Video generation via Veo (planned)
   - Automatic mock mode fallback

2. **`batch_service.py`** - Concurrent batch processing
   - Frame generation with retry logic
   - Progress tracking
   - Error logging

3. **`frame_service.py`** - Frame database operations
   - CRUD for frames
   - Approval workflows
   - Status tracking

4. **`workflow_service.py`** - State management
   - Phase tracking (planning → script → scenes → frames → videos → assembly)
   - Automatic advancement
   - Checkpoints

### Workflow Phases

```
planning → script → scenes → frames → videos → assembly → completed
```

Each phase has specific commands and services to progress the workflow.

## Best Practices

### 1. Always Use Nano Banana API

✅ **DO:**
```python
from ..services.gemini import generate_image

result = await generate_image(
    prompt=prompt,
    model='imagen-3.0-generate-001',
    aspect_ratio='16:9'
)
```

❌ **DON'T:**
- Use direct Google API calls without the wrapper
- Hardcode API endpoints
- Skip error handling

### 2. Handle Errors Gracefully

```python
try:
    result = await generate_image(...)
    if result.get('is_mock'):
        print("Warning: Using mock mode")
except Exception as e:
    print(f"Error: {e}")
    # System automatically falls back to mock mode
```

### 3. Database Operations

Always use async/await with aiosqlite:

```python
async with aiosqlite.connect(DATABASE_PATH) as db:
    cursor = await db.execute("SELECT ...")
    result = await cursor.fetchone()
    await db.commit()
```

### 4. Concurrency Control

For SQLite, limit concurrent writes to avoid locking:

```python
# In batch operations
MAX_CONCURRENT_GENERATIONS = 1  # Sequential for SQLite

# Use semaphore for control
semaphore = asyncio.Semaphore(MAX_CONCURRENT_GENERATIONS)
```

### 5. Progress Tracking

Use Rich library for beautiful terminal UI:

```python
from rich.progress import Progress, SpinnerColumn, BarColumn

with Progress(...) as progress:
    task_id = progress.add_task("Generating...", total=total)
    progress.update(task_id, advance=1)
```

## Project Structure

```
backend/
├── src/
│   ├── cli/
│   │   ├── commands/        # CLI command modules
│   │   │   ├── project.py   # Project management
│   │   │   ├── script.py    # Script generation
│   │   │   ├── scenes.py    # Scene breakdown
│   │   │   └── frames.py    # Frame generation
│   │   ├── ui/
│   │   │   ├── display.py   # Rich formatting
│   │   │   └── prompts.py   # User input
│   │   └── main.py          # CLI entry point
│   ├── services/
│   │   ├── gemini.py        # Nano Banana API
│   │   ├── batch_service.py # Batch processing
│   │   ├── frame_service.py # Frame operations
│   │   ├── workflow_service.py # State management
│   │   ├── claude_service.py   # Script generation
│   │   └── storage.py       # File management
│   └── database.py          # Schema and init
└── static/
    └── images/              # Generated images
```

## Common Tasks

### Generate Frames

```bash
# Set API key
export GEMINI_API_KEY="your-key-here"

# Generate frames
nb-studio generate-frames <project_id>

# View results
nb-studio show-frames <project_id>

# Approve all
nb-studio approve-all-frames <project_id>
```

### Troubleshooting

#### API Returns 403 Forbidden

Enable required APIs in Google Cloud Console:
1. Generative Language API
2. Vertex AI API
3. Enable billing

#### Database Locked Errors

Reduce concurrency in `batch_service.py`:
```python
MAX_CONCURRENT_GENERATIONS = 1
```

#### Mock Mode Activating

Check:
1. `GEMINI_API_KEY` is set
2. API key has correct permissions
3. Imagen API is enabled in project
4. Billing is active

## Testing

### End-to-End Workflow

```bash
# Create project
nb-studio create-video

# Generate script
nb-studio generate-script <project_id>

# Approve and create scenes
nb-studio approve-script <project_id>
nb-studio approve-scenes <project_id>

# Generate frames
nb-studio generate-frames <project_id>

# Approve frames
nb-studio approve-all-frames <project_id>
```

### Mock Mode Testing

Works without API key:
```bash
unset GEMINI_API_KEY
nb-studio generate-frames <project_id>
# Will use gradient placeholders
```

## Security

- **Never commit API keys** to git
- Use `.env` files (in `.gitignore`)
- API keys should have minimum required permissions
- Monitor usage in Google Cloud Console

## Resources

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [google-genai Package](https://github.com/googleapis/python-genai)
- [Imagen 3 Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview)

## Version History

- **Phase 4 (Current):** Frame generation workflow with Nano Banana API
- **Phase 3:** Scene breakdown and management
- **Phase 2:** Script generation with Claude
- **Phase 1:** Project foundation and database schema
