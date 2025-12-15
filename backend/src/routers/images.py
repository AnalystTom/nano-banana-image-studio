from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
import aiosqlite
from ..database import get_db
from ..models import ImageResponse
from ..services.storage import get_image_url, delete_image
from typing import List, Optional
from pathlib import Path

router = APIRouter(prefix="/api/images", tags=["images"])

@router.get("", response_model=List[ImageResponse])
async def list_images(
    model: Optional[str] = None,
    aspect_ratio: Optional[str] = None,
    resolution: Optional[str] = None,
    session_id: Optional[int] = None,
    sort_by: str = Query("newest", enum=["newest", "oldest"]),
    db: aiosqlite.Connection = Depends(get_db)
):
    query = "SELECT * FROM images WHERE 1=1"
    params = []

    if model:
        query += " AND model = ?"
        params.append(model)
    if aspect_ratio:
        query += " AND aspect_ratio = ?"
        params.append(aspect_ratio)
    if resolution:
        query += " AND resolution = ?"
        params.append(resolution)
    if session_id:
        query += " AND session_id = ?"
        params.append(session_id)

    order = "DESC" if sort_by == "newest" else "ASC"
    query += f" ORDER BY created_at {order}"

    rows = await db.execute_fetchall(query, params)

    return [
        ImageResponse(
            id=row['id'],
            filename=row['filename'],
            image_url=get_image_url(row['filename']),
            prompt=row['prompt'],
            model=row['model'],
            aspect_ratio=row['aspect_ratio'],
            resolution=row['resolution'],
            response_modality=row['response_modality'],
            created_at=row['created_at']
        )
        for row in rows
    ]

@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: int, db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute_fetchall("SELECT * FROM images WHERE id = ?", (image_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Image not found")

    row = rows[0]
    return ImageResponse(
        id=row['id'],
        filename=row['filename'],
        image_url=get_image_url(row['filename']),
        prompt=row['prompt'],
        model=row['model'],
        aspect_ratio=row['aspect_ratio'],
        resolution=row['resolution'],
        response_modality=row['response_modality'],
        created_at=row['created_at']
    )

@router.get("/{image_id}/download")
async def download_image(image_id: int, db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute_fetchall("SELECT * FROM images WHERE id = ?", (image_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Image not found")

    image = dict(rows[0])
    file_path = Path(image['file_path'])

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found")

    return FileResponse(
        path=str(file_path),
        filename=image['filename'],
        media_type="image/png"
    )

@router.get("/{image_id}/versions")
async def get_image_versions(image_id: int, db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute_fetchall("""
        SELECT iv.*, i.filename, i.prompt as version_prompt
        FROM image_versions iv
        JOIN images i ON iv.edited_image_id = i.id
        WHERE iv.original_image_id = ?
        ORDER BY iv.created_at DESC
    """, (image_id,))

    return [
        {
            "id": row['id'],
            "original_image_id": row['original_image_id'],
            "edited_image_id": row['edited_image_id'],
            "edit_prompt": row['edit_prompt'],
            "image_url": get_image_url(row['filename']),
            "created_at": row['created_at']
        }
        for row in rows
    ]

@router.delete("/{image_id}")
async def delete_image_record(image_id: int, db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute_fetchall("SELECT * FROM images WHERE id = ?", (image_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Image not found")

    image = dict(rows[0])
    delete_image(image['filename'])

    await db.execute("DELETE FROM images WHERE id = ?", (image_id,))
    await db.commit()

    return {"message": "Image deleted"}

@router.delete("/bulk")
async def bulk_delete_images(image_ids: List[int], db: aiosqlite.Connection = Depends(get_db)):
    deleted = 0
    for image_id in image_ids:
        rows = await db.execute_fetchall("SELECT * FROM images WHERE id = ?", (image_id,))
        if rows:
            image = dict(rows[0])
            delete_image(image['filename'])
            await db.execute("DELETE FROM images WHERE id = ?", (image_id,))
            deleted += 1

    await db.commit()
    return {"message": f"Deleted {deleted} images"}
