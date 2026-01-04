import aiosqlite
import re
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..database import DATABASE_PATH


class ScriptService:
    """Manages video scripts in the database."""
    
    @staticmethod
    def count_scenes(script_content: str) -> int:
        """Count scenes by looking for scene headers.
        
        Matches patterns like:
        - ## Scene 1
        - Scene 1:
        - SCENE 1
        """
        patterns = [
            r'##\s*Scene\s+\d+',  # Markdown headers
            r'Scene\s+\d+:',       # Scene X:
            r'SCENE\s+\d+',        # SCENE X
        ]
        
        matches = set()
        for pattern in patterns:
            found = re.findall(pattern, script_content, re.IGNORECASE)
            matches.update(found)
        
        return len(matches) if matches else 1  # At least 1 scene
    
    @staticmethod
    async def create_script(
        project_id: str,
        content: str,
        version: int = 1
    ) -> Dict[str, Any]:
        """Create a new script for a project.
        
        Args:
            project_id: Project ID
            content: Script content (markdown formatted)
            version: Script version number (default 1)
            
        Returns:
            Dict with script data including id
        """
        # Count scenes in content
        scene_count = ScriptService.count_scenes(content)
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                """INSERT INTO scripts (project_id, version, content, scene_count)
                   VALUES (?, ?, ?, ?)""",
                (project_id, version, content, scene_count)
            )
            await db.commit()
            script_id = cursor.lastrowid
            
            # Return the created script
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM scripts WHERE id = ?", (script_id,))
            row = await cursor.fetchone()
            return dict(row)
    
    @staticmethod
    async def get_script(script_id: int) -> Optional[Dict[str, Any]]:
        """Get a script by ID."""
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM scripts WHERE id = ?",
                (script_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            return dict(row)
    
    @staticmethod
    async def get_scripts_for_project(
        project_id: str,
        approved_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all scripts for a project, optionally filtered.
        
        Args:
            project_id: Project ID
            approved_only: If True, only return approved scripts
            
        Returns:
            List of script dicts, ordered by version DESC
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            
            if approved_only:
                query = """SELECT * FROM scripts 
                          WHERE project_id = ? AND approved = 1 
                          ORDER BY version DESC"""
            else:
                query = """SELECT * FROM scripts 
                          WHERE project_id = ? 
                          ORDER BY version DESC"""
            
            cursor = await db.execute(query, (project_id,))
            rows = await cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    @staticmethod
    async def get_latest_script(project_id: str) -> Optional[Dict[str, Any]]:
        """Get the most recent script for a project."""
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT * FROM scripts 
                   WHERE project_id = ? 
                   ORDER BY version DESC 
                   LIMIT 1""",
                (project_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            return dict(row)
    
    @staticmethod
    async def approve_script(script_id: int) -> Dict[str, Any]:
        """Mark a script as approved.
        
        Args:
            script_id: Script ID to approve
            
        Returns:
            Updated script dict
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """UPDATE scripts
                   SET approved = 1, approved_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (script_id,)
            )
            await db.commit()
            
            # Return updated script
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM scripts WHERE id = ?", (script_id,))
            row = await cursor.fetchone()
            return dict(row)
    
    @staticmethod
    async def get_next_version(project_id: str) -> int:
        """Get the next version number for a project's scripts.
        
        Args:
            project_id: Project ID
            
        Returns:
            Next version number (1 if no scripts exist)
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                """SELECT MAX(version) as max_version 
                   FROM scripts 
                   WHERE project_id = ?""",
                (project_id,)
            )
            row = await cursor.fetchone()
            
            max_version = row[0] if row[0] is not None else 0
            return max_version + 1
    
    @staticmethod
    async def get_approved_script(project_id: str) -> Optional[Dict[str, Any]]:
        """Get the approved script for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Approved script dict or None
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT * FROM scripts 
                   WHERE project_id = ? AND approved = 1 
                   ORDER BY approved_at DESC 
                   LIMIT 1""",
                (project_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            return dict(row)
