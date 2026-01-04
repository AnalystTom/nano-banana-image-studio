"""
Batch Service - Concurrent processing and batch job management.

Handles batch image generation with progress tracking, retry logic, and error handling.
"""

import aiosqlite
import asyncio
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import traceback

from .gemini import generate_image
from .storage import save_image, generate_filename
from .frame_service import FrameService

# Database path
DATABASE_PATH = Path(__file__).parent.parent.parent / 'database.db'

# Concurrency limit (set to 1 to avoid SQLite locking issues)
# SQLite has limited concurrent write support, so we process sequentially
MAX_CONCURRENT_GENERATIONS = 1


class BatchService:
    """Service for managing batch operations."""

    @staticmethod
    async def create_batch_job(
        project_id: str,
        job_type: str,
        total_items: int
    ) -> int:
        """
        Create a new batch job record.

        Args:
            project_id: The project ID
            job_type: Type of batch job (e.g., 'frame_generation')
            total_items: Total number of items to process

        Returns:
            The created job ID
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                """
                INSERT INTO batch_jobs (project_id, job_type, status, total_items, completed_items, failed_items)
                VALUES (?, ?, 'running', ?, 0, 0)
                """,
                (project_id, job_type, total_items)
            )
            await db.commit()
            return cursor.lastrowid

    @staticmethod
    async def update_batch_progress(
        job_id: int,
        completed: int,
        failed: int
    ) -> bool:
        """
        Update batch job progress.

        Args:
            job_id: The batch job ID
            completed: Number of successfully completed items
            failed: Number of failed items

        Returns:
            True if update successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """
                UPDATE batch_jobs
                SET completed_items = ?, failed_items = ?
                WHERE id = ?
                """,
                (completed, failed, job_id)
            )
            await db.commit()
            return True

    @staticmethod
    async def mark_job_complete(job_id: int) -> bool:
        """
        Mark a batch job as completed.

        Args:
            job_id: The batch job ID

        Returns:
            True if update successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """
                UPDATE batch_jobs
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (job_id,)
            )
            await db.commit()
            return True

    @staticmethod
    async def mark_job_failed(job_id: int, error: str) -> bool:
        """
        Mark a batch job as failed with error.

        Args:
            job_id: The batch job ID
            error: Error message

        Returns:
            True if update successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """
                UPDATE batch_jobs
                SET status = 'failed', error_log = ?
                WHERE id = ?
                """,
                (error, job_id)
            )
            await db.commit()
            return True

    @staticmethod
    async def get_batch_status(job_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the status of a batch job.

        Args:
            job_id: The batch job ID

        Returns:
            Batch job record as dictionary or None if not found
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT * FROM batch_jobs WHERE id = ?
                """,
                (job_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    async def append_error_log(job_id: int, error_message: str) -> bool:
        """
        Append an error message to the batch job error log.

        Args:
            job_id: The batch job ID
            error_message: Error message to append

        Returns:
            True if update successful
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Get current error log
            cursor = await db.execute(
                """SELECT error_log FROM batch_jobs WHERE id = ?""",
                (job_id,)
            )
            row = await cursor.fetchone()
            current_log = row[0] if row and row[0] else ""

            # Append new error with timestamp
            timestamp = datetime.now().isoformat()
            new_entry = f"[{timestamp}] {error_message}\n"
            updated_log = current_log + new_entry

            # Update
            await db.execute(
                """
                UPDATE batch_jobs
                SET error_log = ?
                WHERE id = ?
                """,
                (updated_log, job_id)
            )
            await db.commit()
            return True

    @staticmethod
    async def _generate_single_frame_with_retry(
        frame: Dict[str, Any],
        project_id: str,
        aspect_ratio: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a single frame with retry logic.

        Args:
            frame: Frame record dictionary
            project_id: Project ID for file organization
            aspect_ratio: Aspect ratio for image generation
            max_retries: Maximum number of retry attempts

        Returns:
            Dictionary with success status and optional error message
        """
        frame_id = frame['id']
        prompt = frame['prompt']
        scene_number = frame['scene_number']
        frame_type = frame['frame_type']

        for attempt in range(max_retries):
            try:
                # Update status to generating
                await FrameService.update_frame_status(frame_id, 'generating')

                # Generate image using Gemini
                result = await generate_image(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    resolution='2K'
                )

                # Save image to storage
                filename = generate_filename('png')
                # Organize by project: scene_X_opening/closing_timestamp.png
                custom_filename = f"scene_{scene_number}_{frame_type}_{filename}"
                file_path = save_image(result['image_data'], custom_filename)

                # Create image record in database
                async with aiosqlite.connect(DATABASE_PATH) as db:
                    cursor = await db.execute(
                        """
                        INSERT INTO images (filename, file_path, prompt, model, aspect_ratio, resolution, is_mock)
                        VALUES (?, ?, ?, ?, ?, '2K', ?)
                        """,
                        (custom_filename, file_path, prompt, 'gemini-2.5-flash-image', aspect_ratio, result.get('is_mock', True))
                    )
                    await db.commit()
                    image_id = cursor.lastrowid

                # Update frame with image_id and mark as completed
                await FrameService.update_frame_status(frame_id, 'completed', image_id)

                return {
                    'success': True,
                    'frame_id': frame_id,
                    'image_id': image_id,
                    'filename': custom_filename,
                    'is_mock': result.get('is_mock', True)
                }

            except Exception as e:
                error_msg = f"Frame {frame_id} (Scene {scene_number}, {frame_type}) - Attempt {attempt + 1}/{max_retries}: {str(e)}"

                if attempt < max_retries - 1:
                    # Wait before retry (exponential backoff)
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    # Final failure
                    await FrameService.update_frame_status(frame_id, 'failed')
                    return {
                        'success': False,
                        'frame_id': frame_id,
                        'error': error_msg,
                        'traceback': traceback.format_exc()
                    }

        return {
            'success': False,
            'frame_id': frame_id,
            'error': f"Failed after {max_retries} attempts"
        }

    @staticmethod
    async def process_frame_batch(
        project_id: str,
        frames: List[Dict[str, Any]],
        aspect_ratio: str = '16:9',
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Process a batch of frames concurrently with controlled concurrency.

        Args:
            project_id: The project ID
            frames: List of frame records to process
            aspect_ratio: Aspect ratio for image generation
            progress_callback: Optional callback function for progress updates

        Returns:
            Dictionary with processing results
        """
        if not frames:
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'errors': []
            }

        # Create batch job
        job_id = await BatchService.create_batch_job(
            project_id=project_id,
            job_type='frame_generation',
            total_items=len(frames)
        )

        # Semaphore to limit concurrent operations
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_GENERATIONS)

        async def generate_with_semaphore(frame):
            async with semaphore:
                return await BatchService._generate_single_frame_with_retry(
                    frame, project_id, aspect_ratio
                )

        # Process all frames concurrently (limited by semaphore)
        results = []
        completed = 0
        failed = 0

        for coro in asyncio.as_completed([generate_with_semaphore(f) for f in frames]):
            result = await coro
            results.append(result)

            if result['success']:
                completed += 1
            else:
                failed += 1
                # Log error to batch job
                await BatchService.append_error_log(job_id, result.get('error', 'Unknown error'))

            # Update progress
            await BatchService.update_batch_progress(job_id, completed, failed)

            # Call progress callback if provided
            if progress_callback:
                await progress_callback(completed + failed, len(frames), result)

        # Mark job as complete
        await BatchService.mark_job_complete(job_id)

        # Collect errors
        errors = [r for r in results if not r['success']]

        return {
            'job_id': job_id,
            'total': len(frames),
            'successful': completed,
            'failed': failed,
            'errors': errors,
            'results': results
        }
