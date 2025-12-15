from fastapi import APIRouter, Depends
import aiosqlite
from ..database import get_db
from ..models import SettingsUpdate, SettingsResponse

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("", response_model=SettingsResponse)
async def get_settings(db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute_fetchall("SELECT * FROM settings WHERE id = 1")
    if not rows:
        await db.execute("INSERT INTO settings (id) VALUES (1)")
        await db.commit()
        rows = await db.execute_fetchall("SELECT * FROM settings WHERE id = 1")

    row = rows[0]
    return SettingsResponse(
        default_model=row['default_model'],
        default_aspect_ratio=row['default_aspect_ratio'],
        default_resolution=row['default_resolution'],
        default_response_modality=row['default_response_modality'],
        google_search_default=bool(row['google_search_default']),
        auto_save_conversations=bool(row['auto_save_conversations'])
    )

@router.put("", response_model=SettingsResponse)
async def update_settings(request: SettingsUpdate, db: aiosqlite.Connection = Depends(get_db)):
    updates = []
    params = []

    if request.default_model is not None:
        updates.append("default_model = ?")
        params.append(request.default_model)
    if request.default_aspect_ratio is not None:
        updates.append("default_aspect_ratio = ?")
        params.append(request.default_aspect_ratio)
    if request.default_resolution is not None:
        updates.append("default_resolution = ?")
        params.append(request.default_resolution)
    if request.default_response_modality is not None:
        updates.append("default_response_modality = ?")
        params.append(request.default_response_modality)
    if request.google_search_default is not None:
        updates.append("google_search_default = ?")
        params.append(request.google_search_default)
    if request.auto_save_conversations is not None:
        updates.append("auto_save_conversations = ?")
        params.append(request.auto_save_conversations)

    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE settings SET {', '.join(updates)} WHERE id = 1"
        await db.execute(query, params)
        await db.commit()

    return await get_settings(db)
