from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from pathlib import Path

from .database import init_db
from .routers import generate, sessions, images, settings, templates

BASE_DIR = Path(__file__).parent.parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Nano Banana Image Studio",
    description="AI-powered image generation and editing studio",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = BASE_DIR / "static"
(static_dir / "images").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(generate.router)
app.include_router(sessions.router)
app.include_router(images.router)
app.include_router(settings.router)
app.include_router(templates.router)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Nano Banana Image Studio"}

@app.get("/api")
async def api_info():
    return {
        "name": "Nano Banana Image Studio API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/api/generate",
            "edit": "/api/edit",
            "sessions": "/api/sessions",
            "images": "/api/images",
            "settings": "/api/settings",
            "templates": "/api/templates"
        }
    }
