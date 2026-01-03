import aiosqlite
import json
from typing import Optional, Dict, Any
from datetime import datetime

from ..database import DATABASE_PATH

class WorkflowService:
    """Manages workflow state for video production projects."""
    
    @staticmethod
    async def create_workflow(project_id: str, initial_phase: str = 'planning') -> Dict[str, Any]:
        """Create a new workflow for a project."""
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                """INSERT INTO workflows (project_id, current_phase)
                   VALUES (?, ?)""",
                (project_id, initial_phase)
            )
            await db.commit()
            workflow_id = cursor.lastrowid
            
            return {
                'id': workflow_id,
                'project_id': project_id,
                'current_phase': initial_phase
            }
    
    @staticmethod
    async def get_workflow(project_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow state for a project."""
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM workflows WHERE project_id = ?",
                (project_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            workflow = dict(row)
            if workflow.get('phase_data'):
                workflow['phase_data'] = json.loads(workflow['phase_data'])
            
            return workflow
    
    @staticmethod
    async def advance_phase(
        project_id: str,
        next_phase: str,
        phase_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Advance workflow to next phase."""
        async with aiosqlite.connect(DATABASE_PATH) as db:
            phase_data_json = json.dumps(phase_data) if phase_data else None
            
            await db.execute(
                """UPDATE workflows
                   SET current_phase = ?,
                       phase_data = ?,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE project_id = ?""",
                (next_phase, phase_data_json, project_id)
            )
            
            # Also update project status
            await db.execute(
                """UPDATE projects
                   SET status = ?,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (next_phase, project_id)
            )
            
            await db.commit()
            
            return await WorkflowService.get_workflow(project_id)
    
    @staticmethod
    async def checkpoint(
        project_id: str,
        checkpoint_name: str
    ) -> None:
        """Save a checkpoint in the workflow."""
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """UPDATE workflows
                   SET checkpoint = ?,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE project_id = ?""",
                (checkpoint_name, project_id)
            )
            await db.commit()
    
    @staticmethod
    async def get_phase_progress(project_id: str) -> Dict[str, Any]:
        """Get detailed progress for current phase."""
        workflow = await WorkflowService.get_workflow(project_id)
        if not workflow:
            return {}
        
        phase = workflow['current_phase']
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            progress = {'phase': phase}
            
            if phase == 'script':
                cursor = await db.execute(
                    """SELECT COUNT(*) as count, 
                       SUM(CASE WHEN approved = 1 THEN 1 ELSE 0 END) as approved
                       FROM scripts WHERE project_id = ?""",
                    (project_id,)
                )
                row = await cursor.fetchone()
                progress['scripts_total'] = row[0]
                progress['scripts_approved'] = row[1] or 0
            
            elif phase == 'frames':
                cursor = await db.execute(
                    """SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                       SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved
                       FROM frames WHERE project_id = ?""",
                    (project_id,)
                )
                row = await cursor.fetchone()
                progress['frames_total'] = row[0]
                progress['frames_completed'] = row[1] or 0
                progress['frames_approved'] = row[2] or 0
            
            return progress
