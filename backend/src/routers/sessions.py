from fastapi import APIRouter, Depends, HTTPException
import aiosqlite
from ..database import get_db
from ..models import (
    SessionCreate, SessionUpdate, SessionResponse,
    MessageRequest, ConversationMessage, ImageResponse
)
from ..services.gemini import generate_image
from ..services.storage import generate_filename, save_image, get_image_url
from typing import List

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.post("", response_model=SessionResponse)
async def create_session(request: SessionCreate, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute(
        "INSERT INTO sessions (name, model) VALUES (?, ?)",
        (request.name, request.model)
    )
    await db.commit()
    session_id = cursor.lastrowid

    row = await db.execute_fetchall("SELECT * FROM sessions WHERE id = ?", (session_id,))
    session = dict(row[0])

    return SessionResponse(
        id=session['id'],
        name=session['name'],
        model=session['model'],
        created_at=session['created_at'],
        updated_at=session['updated_at'],
        image_count=0
    )

@router.get("", response_model=List[SessionResponse])
async def list_sessions(db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute_fetchall("""
        SELECT s.*, COUNT(i.id) as image_count
        FROM sessions s
        LEFT JOIN images i ON s.id = i.session_id
        GROUP BY s.id
        ORDER BY s.updated_at DESC
    """)

    return [
        SessionResponse(
            id=row['id'],
            name=row['name'],
            model=row['model'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            image_count=row['image_count']
        )
        for row in rows
    ]

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute_fetchall("""
        SELECT s.*, COUNT(i.id) as image_count
        FROM sessions s
        LEFT JOIN images i ON s.id = i.session_id
        WHERE s.id = ?
        GROUP BY s.id
    """, (session_id,))

    if not rows:
        raise HTTPException(status_code=404, detail="Session not found")

    row = rows[0]
    return SessionResponse(
        id=row['id'],
        name=row['name'],
        model=row['model'],
        created_at=row['created_at'],
        updated_at=row['updated_at'],
        image_count=row['image_count']
    )

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: int, request: SessionUpdate, db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute_fetchall("SELECT * FROM sessions WHERE id = ?", (session_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Session not found")

    if request.name:
        await db.execute(
            "UPDATE sessions SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (request.name, session_id)
        )
        await db.commit()

    return await get_session(session_id, db)

@router.delete("/{session_id}")
async def delete_session(session_id: int, db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute_fetchall("SELECT * FROM sessions WHERE id = ?", (session_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    await db.commit()

    return {"message": "Session deleted"}

@router.get("/{session_id}/history", response_model=List[ConversationMessage])
async def get_conversation_history(session_id: int, db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute_fetchall("""
        SELECT ch.*, i.filename
        FROM conversation_history ch
        LEFT JOIN images i ON ch.image_id = i.id
        WHERE ch.session_id = ?
        ORDER BY ch.created_at ASC
    """, (session_id,))

    return [
        ConversationMessage(
            id=row['id'],
            role=row['role'],
            message=row['message'],
            image_id=row['image_id'],
            image_url=get_image_url(row['filename']) if row['filename'] else None,
            created_at=row['created_at']
        )
        for row in rows
    ]

@router.post("/{session_id}/message", response_model=ImageResponse)
async def send_message(session_id: int, request: MessageRequest, db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute_fetchall("SELECT * FROM sessions WHERE id = ?", (session_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Session not found")

    session = dict(rows[0])

    await db.execute(
        "INSERT INTO conversation_history (session_id, role, message) VALUES (?, ?, ?)",
        (session_id, 'user', request.message)
    )
    await db.commit()

    result = await generate_image(
        prompt=request.message,
        model=session['model']
    )

    filename = generate_filename()
    file_path = save_image(result['image_data'], filename)

    cursor = await db.execute(
        """INSERT INTO images
           (session_id, filename, file_path, prompt, model, aspect_ratio,
            resolution, response_modality, token_count, thought_signature)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (session_id, filename, file_path, request.message, session['model'],
         '1:1', '1K', 'TEXT_IMAGE', result.get('token_count'),
         result.get('thought_signature'))
    )
    await db.commit()
    image_id = cursor.lastrowid

    await db.execute(
        "INSERT INTO conversation_history (session_id, role, message, image_id) VALUES (?, ?, ?, ?)",
        (session_id, 'assistant', result.get('text_response'), image_id)
    )
    await db.commit()

    await db.execute(
        "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (session_id,)
    )
    await db.commit()

    row = await db.execute_fetchall("SELECT * FROM images WHERE id = ?", (image_id,))
    image = dict(row[0])

    return ImageResponse(
        id=image['id'],
        filename=image['filename'],
        image_url=get_image_url(image['filename']),
        prompt=image['prompt'],
        model=image['model'],
        aspect_ratio=image['aspect_ratio'],
        resolution=image['resolution'],
        response_modality=image['response_modality'],
        text_response=result.get('text_response'),
        created_at=image['created_at']
    )
