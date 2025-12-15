from fastapi import APIRouter, Depends, HTTPException
import aiosqlite
from ..database import get_db
from ..models import GenerateRequest, EditRequest, ImageResponse
from ..services.gemini import generate_image, edit_image
from ..services.storage import generate_filename, save_image, get_image_url

router = APIRouter(prefix="/api", tags=["generate"])

@router.post("/generate", response_model=ImageResponse)
async def create_image(request: GenerateRequest, db: aiosqlite.Connection = Depends(get_db)):
    try:
        result = await generate_image(
            prompt=request.prompt,
            model=request.model,
            aspect_ratio=request.aspect_ratio,
            resolution=request.resolution,
            response_modality=request.response_modality,
            google_search_enabled=request.google_search_enabled
        )

        filename = generate_filename()
        file_path = save_image(result['image_data'], filename)

        cursor = await db.execute(
            """INSERT INTO images
               (session_id, filename, file_path, prompt, model, aspect_ratio,
                resolution, response_modality, google_search_enabled, token_count,
                thought_signature, grounding_metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (request.session_id, filename, file_path, request.prompt, request.model,
             request.aspect_ratio, request.resolution, request.response_modality,
             request.google_search_enabled, result.get('token_count'),
             result.get('thought_signature'), result.get('grounding_metadata'))
        )
        await db.commit()
        image_id = cursor.lastrowid

        row = await db.execute_fetchall(
            "SELECT * FROM images WHERE id = ?", (image_id,)
        )
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit", response_model=ImageResponse)
async def edit_existing_image(request: EditRequest, db: aiosqlite.Connection = Depends(get_db)):
    row = await db.execute_fetchall(
        "SELECT * FROM images WHERE id = ?", (request.image_id,)
    )
    if not row:
        raise HTTPException(status_code=404, detail="Image not found")

    original = dict(row[0])

    result = await edit_image(
        image_path=original['file_path'],
        prompt=request.prompt,
        model=request.model,
        aspect_ratio=request.aspect_ratio or original['aspect_ratio'],
        resolution=request.resolution or original['resolution']
    )

    filename = generate_filename()
    file_path = save_image(result['image_data'], filename)

    cursor = await db.execute(
        """INSERT INTO images
           (session_id, filename, file_path, prompt, model, aspect_ratio,
            resolution, response_modality, token_count)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (original.get('session_id'), filename, file_path, request.prompt, request.model,
         request.aspect_ratio or original['aspect_ratio'],
         request.resolution or original['resolution'],
         original['response_modality'], result.get('token_count'))
    )
    await db.commit()
    new_id = cursor.lastrowid

    await db.execute(
        """INSERT INTO image_versions (original_image_id, edited_image_id, edit_prompt)
           VALUES (?, ?, ?)""",
        (request.image_id, new_id, request.prompt)
    )
    await db.commit()

    row = await db.execute_fetchall("SELECT * FROM images WHERE id = ?", (new_id,))
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
