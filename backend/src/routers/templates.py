from fastapi import APIRouter, Depends, HTTPException
import aiosqlite
from ..database import get_db
from ..models import TemplateCreate, TemplateResponse
from typing import List

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.get("", response_model=List[TemplateResponse])
async def list_templates(db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute_fetchall("SELECT * FROM prompt_templates ORDER BY category, name")

    return [
        TemplateResponse(
            id=row['id'],
            name=row['name'],
            category=row['category'],
            template=row['template'],
            description=row['description'],
            created_at=row['created_at']
        )
        for row in rows
    ]

@router.post("", response_model=TemplateResponse)
async def create_template(request: TemplateCreate, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute(
        "INSERT INTO prompt_templates (name, category, template, description) VALUES (?, ?, ?, ?)",
        (request.name, request.category, request.template, request.description)
    )
    await db.commit()
    template_id = cursor.lastrowid

    rows = await db.execute_fetchall("SELECT * FROM prompt_templates WHERE id = ?", (template_id,))
    row = rows[0]

    return TemplateResponse(
        id=row['id'],
        name=row['name'],
        category=row['category'],
        template=row['template'],
        description=row['description'],
        created_at=row['created_at']
    )

@router.delete("/{template_id}")
async def delete_template(template_id: int, db: aiosqlite.Connection = Depends(get_db)):
    rows = await db.execute_fetchall("SELECT * FROM prompt_templates WHERE id = ?", (template_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Template not found")

    await db.execute("DELETE FROM prompt_templates WHERE id = ?", (template_id,))
    await db.commit()

    return {"message": "Template deleted"}
