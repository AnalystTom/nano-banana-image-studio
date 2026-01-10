"""
Video Service - Database operations for scene video management.

Handles CRUD operations for scene videos, status updates, and approval workflows.
"""

import aiosqlite
from typing import List, Dict, Any, Optional
from pathlib import Path

# Database path
DATABASE_PATH = Path(__file__).parent.parent.parent / 'database.db'


class VideoService:
    """Service for managing scene video database operations."""

    @staticmethod
    async def create_scene_video(
        project_id: str,
        scene_id: int,
        video_id: int,
        reference_frame_id: int,
        prompt: str,
        status: str = 'completed'
    ) -> int:
        """
        Create a scene video record.

        Args:
            project_id: The project ID
            scene_id: The scene ID
            video_id: The video ID (from videos table)
            reference_frame_id: The frame used as starting image
            prompt: Motion prompt used for generation
            status: Initial status (default: completed)

        Returns:
            The created scene_video ID
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                """
                INSERT INTO scene_videos
                (project_id, scene_id, video_id, reference_frame_id, prompt, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (project_id, scene_id, video_id, reference_frame_id, prompt, status)
            )
            await db.commit()
            return cursor.lastrowid

    @staticmethod
    async def get_video(video_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single scene video by ID.

        Args:
            video_id: The scene_video ID to retrieve

        Returns:
            Scene video record as dictionary or None if not found
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT sv.*, v.filename as video_filename, v.file_path as video_path,
                       v.duration, v.aspect_ratio, s.scene_number, s.description as scene_description
                FROM scene_videos sv
                LEFT JOIN videos v ON sv.video_id = v.id
                LEFT JOIN scenes s ON sv.scene_id = s.id
                WHERE sv.id = ?
                """,
                (video_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    async def get_videos_for_project(
        project_id: str,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all scene videos for a project, optionally filtered by status.

        Args:
            project_id: The project ID
            status_filter: Optional status to filter by (pending, generating, completed, approved, failed, rejected)

        Returns:
            List of scene video records
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row

            if status_filter:
                cursor = await db.execute(
                    """
                    SELECT sv.*, s.scene_number, v.filename as video_filename, v.duration
                    FROM scene_videos sv
                    JOIN scenes s ON sv.scene_id = s.id
                    LEFT JOIN videos v ON sv.video_id = v.id
                    WHERE sv.project_id = ? AND sv.status = ?
                    ORDER BY s.scene_number
                    """,
                    (project_id, status_filter)
                )
            else:
                cursor = await db.execute(
                    """
                    SELECT sv.*, s.scene_number, v.filename as video_filename, v.duration
                    FROM scene_videos sv
                    JOIN scenes s ON sv.scene_id = s.id
                    LEFT JOIN videos v ON sv.video_id = v.id
                    WHERE sv.project_id = ?
                    ORDER BY s.scene_number
                    """,
                    (project_id,)
                )

            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def get_videos_for_scene(scene_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all videos for a specific scene.

        Args:
            scene_id: The scene ID

        Returns:
            List of scene video records
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT sv.*, v.filename as video_filename, v.file_path as video_path
                FROM scene_videos sv
                LEFT JOIN videos v ON sv.video_id = v.id
                WHERE sv.scene_id = ?
                ORDER BY sv.created_at DESC
                """,
                (scene_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def update_video_status(
        video_id: int,
        status: str,
        video_file_id: Optional[int] = None
    ) -> bool:
        """
        Update scene video status and optionally link to generated video.

        Args:
            video_id: The scene_video ID to update
            status: New status (pending, generating, completed, approved, failed, rejected)
            video_file_id: Optional video ID (from videos table) to link

        Returns:
            True if update successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            if video_file_id is not None:
                await db.execute(
                    """
                    UPDATE scene_videos
                    SET status = ?, video_id = ?
                    WHERE id = ?
                    """,
                    (status, video_file_id, video_id)
                )
            else:
                await db.execute(
                    """
                    UPDATE scene_videos
                    SET status = ?
                    WHERE id = ?
                    """,
                    (status, video_id)
                )
            await db.commit()
            return True

    @staticmethod
    async def approve_video(video_id: int) -> bool:
        """
        Mark a scene video as approved.

        Args:
            video_id: The scene_video ID to approve

        Returns:
            True if approval successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """
                UPDATE scene_videos
                SET status = 'approved'
                WHERE id = ?
                """,
                (video_id,)
            )
            await db.commit()
            return True

    @staticmethod
    async def reject_video(video_id: int, feedback: Optional[str] = None) -> bool:
        """
        Mark a scene video as rejected with optional feedback.

        Args:
            video_id: The scene_video ID to reject
            feedback: Optional feedback for regeneration

        Returns:
            True if rejection successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """
                UPDATE scene_videos
                SET status = 'rejected', approval_feedback = ?
                WHERE id = ?
                """,
                (feedback, video_id)
            )
            await db.commit()
            return True

    @staticmethod
    async def update_video_prompt(video_id: int, new_prompt: str) -> bool:
        """
        Update the motion prompt for a scene video (used for regeneration).

        Args:
            video_id: The scene_video ID
            new_prompt: New motion prompt text

        Returns:
            True if update successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """
                UPDATE scene_videos
                SET prompt = ?
                WHERE id = ?
                """,
                (new_prompt, video_id)
            )
            await db.commit()
            return True

    @staticmethod
    async def update_trim_settings(
        video_id: int,
        trim_start: Optional[float] = None,
        trim_end: Optional[float] = None
    ) -> bool:
        """
        Update trim settings for a scene video.

        Args:
            video_id: The scene_video ID
            trim_start: Start time in seconds (None to keep current)
            trim_end: End time in seconds (None to keep current)

        Returns:
            True if update successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            updates = []
            values = []

            if trim_start is not None:
                updates.append("trim_start = ?")
                values.append(trim_start)

            if trim_end is not None:
                updates.append("trim_end = ?")
                values.append(trim_end)

            if not updates:
                return True

            values.append(video_id)
            query = f"UPDATE scene_videos SET {', '.join(updates)} WHERE id = ?"

            await db.execute(query, values)
            await db.commit()
            return True

    @staticmethod
    async def get_pending_videos(project_id: str) -> List[Dict[str, Any]]:
        """
        Get all videos that need generation (status = pending).

        Args:
            project_id: The project ID

        Returns:
            List of pending scene video records
        """
        return await VideoService.get_videos_for_project(project_id, status_filter='pending')

    @staticmethod
    async def get_approval_stats(project_id: str) -> Dict[str, int]:
        """
        Get approval statistics for a project's videos.

        Args:
            project_id: The project ID

        Returns:
            Dictionary with counts: total, pending, generating, completed, approved, failed, rejected
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                """
                SELECT status, COUNT(*) as count
                FROM scene_videos
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

    @staticmethod
    async def delete_video(video_id: int) -> bool:
        """
        Delete a scene video record.

        Args:
            video_id: The scene_video ID to delete

        Returns:
            True if deletion successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """
                DELETE FROM scene_videos
                WHERE id = ?
                """,
                (video_id,)
            )
            await db.commit()
            return True
