"""
Frame Service - Database operations for frame management.

Handles CRUD operations for frames, status updates, and approval workflows.
"""

import aiosqlite
from typing import List, Dict, Any, Optional
from pathlib import Path

# Database path
DATABASE_PATH = Path(__file__).parent.parent.parent / 'database.db'


class FrameService:
    """Service for managing frame database operations."""

    @staticmethod
    async def get_frame(frame_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single frame by ID.

        Args:
            frame_id: The frame ID to retrieve

        Returns:
            Frame record as dictionary or None if not found
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT f.*, i.filename as image_filename, i.file_path as image_path
                FROM frames f
                LEFT JOIN images i ON f.image_id = i.id
                WHERE f.id = ?
                """,
                (frame_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    async def get_frames_for_project(
        project_id: str,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all frames for a project, optionally filtered by status.

        Args:
            project_id: The project ID
            status_filter: Optional status to filter by (pending, generating, completed, approved, failed, rejected)

        Returns:
            List of frame records
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row

            if status_filter:
                cursor = await db.execute(
                    """
                    SELECT f.*, s.scene_number, i.filename as image_filename
                    FROM frames f
                    JOIN scenes s ON f.scene_id = s.id
                    LEFT JOIN images i ON f.image_id = i.id
                    WHERE f.project_id = ? AND f.status = ?
                    ORDER BY s.scene_number, f.frame_type
                    """,
                    (project_id, status_filter)
                )
            else:
                cursor = await db.execute(
                    """
                    SELECT f.*, s.scene_number, i.filename as image_filename
                    FROM frames f
                    JOIN scenes s ON f.scene_id = s.id
                    LEFT JOIN images i ON f.image_id = i.id
                    WHERE f.project_id = ?
                    ORDER BY s.scene_number, f.frame_type
                    """,
                    (project_id,)
                )

            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def get_frames_for_scene(scene_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all frames for a specific scene.

        Args:
            scene_id: The scene ID

        Returns:
            List of frame records for the scene
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT f.*, i.filename as image_filename, i.file_path as image_path
                FROM frames f
                LEFT JOIN images i ON f.image_id = i.id
                WHERE f.scene_id = ?
                ORDER BY f.frame_type
                """,
                (scene_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def update_frame_status(
        frame_id: int,
        status: str,
        image_id: Optional[int] = None
    ) -> bool:
        """
        Update frame status and optionally link to generated image.

        Args:
            frame_id: The frame ID to update
            status: New status (pending, generating, completed, approved, failed, rejected)
            image_id: Optional image ID to link

        Returns:
            True if update successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            if image_id is not None:
                await db.execute(
                    """
                    UPDATE frames
                    SET status = ?, image_id = ?
                    WHERE id = ?
                    """,
                    (status, image_id, frame_id)
                )
            else:
                await db.execute(
                    """
                    UPDATE frames
                    SET status = ?
                    WHERE id = ?
                    """,
                    (status, frame_id)
                )
            await db.commit()
            return True

    @staticmethod
    async def approve_frame(frame_id: int) -> bool:
        """
        Mark a frame as approved.

        Args:
            frame_id: The frame ID to approve

        Returns:
            True if approval successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """
                UPDATE frames
                SET status = 'approved'
                WHERE id = ?
                """,
                (frame_id,)
            )
            await db.commit()
            return True

    @staticmethod
    async def reject_frame(frame_id: int, feedback: Optional[str] = None) -> bool:
        """
        Mark a frame as rejected with optional feedback.

        Args:
            frame_id: The frame ID to reject
            feedback: Optional feedback for regeneration

        Returns:
            True if rejection successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """
                UPDATE frames
                SET status = 'rejected', approval_feedback = ?
                WHERE id = ?
                """,
                (feedback, frame_id)
            )
            await db.commit()
            return True

    @staticmethod
    async def update_frame_prompt(frame_id: int, new_prompt: str) -> bool:
        """
        Update the prompt for a frame (used for regeneration).

        Args:
            frame_id: The frame ID
            new_prompt: New prompt text

        Returns:
            True if update successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """
                UPDATE frames
                SET prompt = ?
                WHERE id = ?
                """,
                (new_prompt, frame_id)
            )
            await db.commit()
            return True

    @staticmethod
    async def get_pending_frames(project_id: str) -> List[Dict[str, Any]]:
        """
        Get all frames that need generation (status = pending).

        Args:
            project_id: The project ID

        Returns:
            List of pending frame records
        """
        return await FrameService.get_frames_for_project(project_id, status_filter='pending')

    @staticmethod
    async def get_approval_stats(project_id: str) -> Dict[str, int]:
        """
        Get approval statistics for a project.

        Args:
            project_id: The project ID

        Returns:
            Dictionary with counts: total, pending, generating, completed, approved, failed, rejected
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                """
                SELECT status, COUNT(*) as count
                FROM frames
                WHERE project_id = ?
                GROUP BY status
                """,
                (project_id,)
            )
            rows = await cursor.fetchall()

            stats = {
                'total': 0,
                'pending': 0,
                'generating': 0,
                'completed': 0,
                'approved': 0,
                'failed': 0,
                'rejected': 0
            }

            for row in rows:
                status, count = row
                stats[status] = count
                stats['total'] += count

            return stats
