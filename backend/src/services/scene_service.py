import aiosqlite
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..database import DATABASE_PATH


class SceneService:
    """Manages video scenes in the database."""
    
    @staticmethod
    async def create_scenes(
        project_id: str,
        script_id: int,
        scenes_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Bulk create scenes for a project.
        
        Args:
            project_id: Project ID
            script_id: Associated script ID
            scenes_data: List of scene dicts with keys:
                - scene_number: int
                - description: str
                - opening_frame_prompt: str
                - closing_frame_prompt: Optional[str]
                - camera_direction: str
                - duration: float
                - transition_type: str (default 'cut')
                
        Returns:
            List of created scene dicts
        """
        created_scenes = []
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            for idx, scene_data in enumerate(scenes_data):
                cursor = await db.execute(
                    """INSERT INTO scenes (
                        project_id, script_id, scene_number, description,
                        opening_frame_prompt, closing_frame_prompt,
                        camera_direction, duration, transition_type, order_index
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        project_id,
                        script_id,
                        scene_data.get('scene_number', idx + 1),
                        scene_data['description'],
                        scene_data['opening_frame_prompt'],
                        scene_data.get('closing_frame_prompt'),
                        scene_data.get('camera_direction', 'static'),
                        scene_data['duration'],
                        scene_data.get('transition_type', 'cut'),
                        idx  # order_index starts at 0
                    )
                )
                scene_id = cursor.lastrowid
                
                # Fetch created scene
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("SELECT * FROM scenes WHERE id = ?", (scene_id,))
                row = await cursor.fetchone()
                created_scenes.append(dict(row))
            
            await db.commit()
        
        return created_scenes
    
    @staticmethod
    async def get_scene(scene_id: int) -> Optional[Dict[str, Any]]:
        """Get a single scene by ID."""
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM scenes WHERE id = ?",
                (scene_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            return dict(row)
    
    @staticmethod
    async def get_scenes_for_project(
        project_id: str,
        ordered: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all scenes for a project, optionally ordered.
        
        Args:
            project_id: Project ID
            ordered: If True, order by order_index
            
        Returns:
            List of scene dicts
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            
            if ordered:
                query = """SELECT * FROM scenes 
                          WHERE project_id = ? 
                          ORDER BY order_index ASC"""
            else:
                query = """SELECT * FROM scenes 
                          WHERE project_id = ?"""
            
            cursor = await db.execute(query, (project_id,))
            rows = await cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    @staticmethod
    async def get_scenes_for_script(script_id: int) -> List[Dict[str, Any]]:
        """Get all scenes for a specific script.
        
        Args:
            script_id: Script ID
            
        Returns:
            List of scene dicts ordered by order_index
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT * FROM scenes 
                   WHERE script_id = ? 
                   ORDER BY order_index ASC""",
                (script_id,)
            )
            rows = await cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    @staticmethod
    async def update_scene(
        scene_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a scene's properties.
        
        Args:
            scene_id: Scene ID
            updates: Dict of field names to new values
            
        Returns:
            Updated scene dict
        """
        if not updates:
            raise ValueError("No updates provided")
        
        # Build UPDATE query dynamically from updates dict
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [scene_id]
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                f"UPDATE scenes SET {set_clause} WHERE id = ?",
                values
            )
            await db.commit()
            
            # Return updated scene
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM scenes WHERE id = ?", (scene_id,))
            row = await cursor.fetchone()
            return dict(row)
    
    @staticmethod
    async def reorder_scenes(
        project_id: str,
        new_order: List[int]
    ) -> None:
        """Reorder scenes by updating order_index.
        
        Args:
            project_id: Project ID
            new_order: List of scene_ids in desired order
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            for idx, scene_id in enumerate(new_order):
                await db.execute(
                    "UPDATE scenes SET order_index = ? WHERE id = ? AND project_id = ?",
                    (idx, scene_id, project_id)
                )
            await db.commit()
    
    @staticmethod
    async def delete_scene(scene_id: int) -> None:
        """Delete a scene.
        
        Args:
            scene_id: Scene ID to delete
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "DELETE FROM scenes WHERE id = ?",
                (scene_id,)
            )
            await db.commit()
    
    @staticmethod
    async def get_total_duration(project_id: str) -> float:
        """Get total duration of all scenes in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Total duration in seconds
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                "SELECT SUM(duration) as total FROM scenes WHERE project_id = ?",
                (project_id,)
            )
            row = await cursor.fetchone()
            
            return row[0] if row[0] is not None else 0.0
