from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class GenerateRequest(BaseModel):
    prompt: str
    model: str = 'gemini-2.5-flash-image'
    aspect_ratio: str = '1:1'
    resolution: Optional[str] = '1K'
    response_modality: str = 'TEXT_IMAGE'
    google_search_enabled: bool = False
    session_id: Optional[int] = None

class EditRequest(BaseModel):
    image_id: int
    prompt: str
    model: str = 'gemini-2.5-flash-image'
    aspect_ratio: Optional[str] = None
    resolution: Optional[str] = None

class ImageResponse(BaseModel):
    id: int
    filename: str
    image_url: str
    prompt: str
    model: str
    aspect_ratio: str
    resolution: Optional[str]
    response_modality: str
    text_response: Optional[str] = None
    created_at: str

class SessionCreate(BaseModel):
    name: str
    model: str = 'gemini-2.5-flash-image'

class SessionUpdate(BaseModel):
    name: Optional[str] = None

class SessionResponse(BaseModel):
    id: int
    name: str
    model: str
    created_at: str
    updated_at: str
    image_count: int = 0

class MessageRequest(BaseModel):
    message: str

class ConversationMessage(BaseModel):
    id: int
    role: str
    message: Optional[str]
    image_id: Optional[int]
    image_url: Optional[str] = None
    created_at: str

class SettingsUpdate(BaseModel):
    default_model: Optional[str] = None
    default_aspect_ratio: Optional[str] = None
    default_resolution: Optional[str] = None
    default_response_modality: Optional[str] = None
    google_search_default: Optional[bool] = None
    auto_save_conversations: Optional[bool] = None

class SettingsResponse(BaseModel):
    default_model: str
    default_aspect_ratio: str
    default_resolution: str
    default_response_modality: str
    google_search_default: bool
    auto_save_conversations: bool

class TemplateCreate(BaseModel):
    name: str
    category: str
    template: str
    description: Optional[str] = None

class TemplateResponse(BaseModel):
    id: int
    name: str
    category: str
    template: str
    description: Optional[str]
    created_at: str
