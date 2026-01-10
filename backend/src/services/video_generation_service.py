"""
Video Generation Service - Batch video generation and processing.

Handles batch video generation for scenes with progress tracking, retry logic, and error handling.
"""

import aiosqlite
import asyncio
import traceback
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .gemini import generate_video
from .storage import save_video, generate_filename
from .video_service import VideoService
from .scene_service import SceneService
from .frame_service import FrameService

# Database path
DATABASE_PATH = Path(__file__).parent.parent.parent / 'database.db'

# Concurrency limit (set to 1 for SQLite and video generation)
# Video generation is expensive, so we process sequentially
MAX_CONCURRENT_GENERATIONS = 1


class VideoGenerationService:
    """Service for batch video generation."""

    @staticmethod
    async def _create_video_record(
        filename: str,
        file_path: str,
        prompt: str,
        model: str,
        aspect_ratio: str,
        duration: str
    ) -> int:
        """
        Create a video record in the videos table.

        Args:
            filename: Video filename
            file_path: Full file path
            prompt: Motion prompt used
            model: Veo model used
            aspect_ratio: Video aspect ratio
            duration: Video duration

        Returns:
            The created video ID
        """
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                """
                INSERT INTO videos (filename, file_path, prompt, model, aspect_ratio, duration)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (filename, file_path, prompt, model, aspect_ratio, duration)
            )
            await db.commit()
            return cursor.lastrowid

    @staticmethod
    async def _generate_single_scene_video_with_retry(
        scene: Dict[str, Any],
        project_id: str,
        opening_frame_path: str,
        opening_frame_id: int,
        aspect_ratio: str = '16:9',
        duration: str = '5s',
        model: str = 'veo-3.0-generate-001',
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a video for a single scene with retry logic.

        Args:
            scene: Scene record dictionary
            project_id: Project ID for file organization
            opening_frame_path: Path to opening frame image
            opening_frame_id: Opening frame ID for reference
            aspect_ratio: Video aspect ratio
            duration: Video duration
            model: Veo model to use
            max_retries: Maximum number of retry attempts

        Returns:
            Dictionary with success status and optional error message
        """
        scene_id = scene['id']
        scene_number = scene['scene_number']
        scene_description = scene['description']

        # Create motion prompt from scene description
        motion_prompt = f"{scene_description}. Smooth camera movement, cinematic lighting."

        for attempt in range(max_retries):
            try:
                # Generate video using Veo (image-to-video)
                result = await generate_video(
                    prompt=motion_prompt,
                    model=model,
                    aspect_ratio=aspect_ratio,
                    duration=duration,
                    image_path=opening_frame_path
                )

                # Save video to storage
                # Determine extension based on is_mock
                extension = 'gif' if result.get('is_mock', True) else 'mp4'
                filename = generate_filename(extension)
                # Organize by scene: scene_X_timestamp.mp4
                custom_filename = f"scene_{scene_number}_{filename}"
                file_path = save_video(result['video_data'], custom_filename)

                # Create video record in videos table
                video_id = await VideoGenerationService._create_video_record(
                    filename=custom_filename,
                    file_path=file_path,
                    prompt=motion_prompt,
                    model=model,
                    aspect_ratio=aspect_ratio,
                    duration=duration
                )

                # Create scene_video record
                scene_video_id = await VideoService.create_scene_video(
                    project_id=project_id,
                    scene_id=scene_id,
                    video_id=video_id,
                    reference_frame_id=opening_frame_id,
                    prompt=motion_prompt,
                    status='completed'
                )

                return {
                    'success': True,
                    'scene_id': scene_id,
                    'scene_number': scene_number,
                    'video_id': video_id,
                    'scene_video_id': scene_video_id,
                    'filename': custom_filename,
                    'is_mock': result.get('is_mock', True)
                }

            except Exception as e:
                error_msg = f"Scene {scene_number} - Attempt {attempt + 1}/{max_retries}: {str(e)}"

                if attempt < max_retries - 1:
                    # Wait before retry (exponential backoff)
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    # Final failure - create failed scene_video record
                    scene_video_id = await VideoService.create_scene_video(
                        project_id=project_id,
                        scene_id=scene_id,
                        video_id=None,  # No video created
                        reference_frame_id=opening_frame_id,
                        prompt=motion_prompt,
                        status='failed'
                    )

                    return {
                        'success': False,
                        'scene_id': scene_id,
                        'scene_number': scene_number,
                        'scene_video_id': scene_video_id,
                        'error': error_msg,
                        'traceback': traceback.format_exc()
                    }

        return {
            'success': False,
            'scene_id': scene_id,
            'scene_number': scene_number,
            'error': f"Failed after {max_retries} attempts"
        }

    @staticmethod
    async def generate_scene_video(
        project_id: str,
        scene: Dict[str, Any],
        aspect_ratio: str = '16:9',
        model: str = 'veo-3.0-generate-001'
    ) -> Dict[str, Any]:
        """
        Generate a video for a single scene.

        Uses opening frame as starting image and scene description
        as motion prompt for Veo API.

        Args:
            project_id: Project ID
            scene: Scene record dictionary
            aspect_ratio: Video aspect ratio
            model: Veo model to use

        Returns:
            Dictionary with success status and result data
        """
        scene_id = scene['id']

        # Get frames for this scene
        frames = await FrameService.get_frames_for_scene(scene_id)

        # Find approved opening frame
        opening_frame = next(
            (f for f in frames if f['frame_type'] == 'opening' and f['status'] == 'approved'),
            None
        )

        if not opening_frame:
            return {
                'success': False,
                'scene_id': scene_id,
                'error': 'No approved opening frame found for scene'
            }

        if not opening_frame.get('image_path'):
            return {
                'success': False,
                'scene_id': scene_id,
                'error': 'Opening frame has no image path'
            }

        # Determine duration based on scene duration
        scene_duration = scene.get('duration', 5.0)
        duration = '8s' if scene_duration >= 8 else '5s'

        # Generate video
        result = await VideoGenerationService._generate_single_scene_video_with_retry(
            scene=scene,
            project_id=project_id,
            opening_frame_path=opening_frame['image_path'],
            opening_frame_id=opening_frame['id'],
            aspect_ratio=aspect_ratio,
            duration=duration,
            model=model
        )

        return result

    @staticmethod
    async def process_video_batch(
        project_id: str,
        scenes: Optional[List[Dict[str, Any]]] = None,
        aspect_ratio: str = '16:9',
        model: str = 'veo-3.0-generate-001',
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Generate videos for all scenes in a project.

        Processes sequentially to avoid resource issues.

        Args:
            project_id: The project ID
            scenes: Optional list of scenes (will fetch if not provided)
            aspect_ratio: Video aspect ratio
            model: Veo model to use
            progress_callback: Optional callback function for progress updates

        Returns:
            Dictionary with processing results
        """
        # Get scenes if not provided
        if scenes is None:
            scenes = await SceneService.get_scenes_for_project(project_id)

        if not scenes:
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'errors': []
            }

        # Process scenes sequentially (concurrency = 1)
        results = []
        successful = 0
        failed = 0

        for idx, scene in enumerate(scenes):
            result = await VideoGenerationService.generate_scene_video(
                project_id=project_id,
                scene=scene,
                aspect_ratio=aspect_ratio,
                model=model
            )

            results.append(result)

            if result['success']:
                successful += 1
            else:
                failed += 1

            # Call progress callback if provided
            if progress_callback:
                await progress_callback(idx + 1, len(scenes), result)

        # Collect errors
        errors = [r for r in results if not r['success']]

        return {
            'total': len(scenes),
            'successful': successful,
            'failed': failed,
            'errors': errors,
            'results': results
        }

    @staticmethod
    async def regenerate_scene_video(
        project_id: str,
        scene_video_id: int,
        custom_prompt: Optional[str] = None,
        aspect_ratio: str = '16:9',
        model: str = 'veo-3.0-generate-001'
    ) -> Dict[str, Any]:
        """
        Regenerate a video for a scene with optional custom prompt.

        Args:
            project_id: Project ID
            scene_video_id: Scene video ID to regenerate
            custom_prompt: Optional custom motion prompt (uses scene description if None)
            aspect_ratio: Video aspect ratio
            model: Veo model to use

        Returns:
            Dictionary with success status and result data
        """
        # Get existing scene_video
        scene_video = await VideoService.get_video(scene_video_id)
        if not scene_video:
            return {
                'success': False,
                'error': 'Scene video not found'
            }

        # Get scene
        scene = await SceneService.get_scene(scene_video['scene_id'])
        if not scene:
            return {
                'success': False,
                'error': 'Scene not found'
            }

        # Update prompt if custom provided
        if custom_prompt:
            await VideoService.update_video_prompt(scene_video_id, custom_prompt)

        # Delete old scene_video record and generate new one
        await VideoService.delete_video(scene_video_id)

        # Generate new video
        result = await VideoGenerationService.generate_scene_video(
            project_id=project_id,
            scene=scene,
            aspect_ratio=aspect_ratio,
            model=model
        )

        return result
