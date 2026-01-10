"""
Video Commands - CLI commands for video generation and management.

Handles video generation, display, approval, and regeneration workflows.
"""

import asyncio
from typing import Optional
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
import aiosqlite

from ...services.video_service import VideoService
from ...services.video_generation_service import VideoGenerationService
from ...services.scene_service import SceneService
from ...services.workflow_service import WorkflowService
from ...services.frame_service import FrameService
from ..ui.display import (
    print_header, print_success, print_error, print_warning, print_info,
    display_videos_grid, display_video_detail, console
)
from ..ui.prompts import prompt_confirm
from ...database import DATABASE_PATH


async def generate_videos(project_id: str):
    """
    Generate videos for all scenes in a project.

    Args:
        project_id: The project ID
    """
    print_header("Video Generation", f"Project: {project_id}")

    # Get project details
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        project = await cursor.fetchone()

        if not project:
            print_error(f"Project {project_id} not found")
            return

        project = dict(project)

    # Check workflow phase
    workflow = await WorkflowService.get_workflow(project_id)
    if workflow['current_phase'] != 'videos':
        print_warning(f"Current phase is '{workflow['current_phase']}', expected 'videos'")
        print_info("Ensure all frames are approved before generating videos")
        return

    # Get all scenes
    scenes = await SceneService.get_scenes_for_project(project_id)

    if not scenes:
        print_error("No scenes found for this project")
        return

    print_info(f"Found {len(scenes)} scenes to generate videos for")

    # Check frame approval status
    frame_stats = await FrameService.get_approval_stats(project_id)
    if frame_stats['approved'] != frame_stats['total']:
        print_error(f"Not all frames are approved ({frame_stats['approved']}/{frame_stats['total']})")
        print_info("Approve frames first: nb-studio approve-all-frames {project_id}")
        return

    # Check if videos already exist
    existing_videos = await VideoService.get_videos_for_project(project_id)
    if existing_videos:
        print_warning(f"{len(existing_videos)} videos already exist for this project")
        if not prompt_confirm("Regenerate all videos?"):
            print_info("Video generation cancelled")
            return

    # Check if using mock mode
    import os
    is_mock = not os.getenv('GEMINI_API_KEY')
    if is_mock:
        print_warning("⚠ Using mock mode (GEMINI_API_KEY not set)")
        print_info("Videos will be generated as animated GIFs for demo purposes")

    # Confirm before generating
    console.print()
    print_info(f"This will generate {len(scenes)} videos using:")
    print_info(f"  • Model: Veo 3.0 (Google)")
    print_info(f"  • Method: Image-to-video (from opening frames)")
    print_info(f"  • Estimated time: ~{len(scenes) * 60} seconds")
    console.print()

    if not prompt_confirm(f"Generate {len(scenes)} scene videos?"):
        print_info("Video generation cancelled")
        return

    # Progress tracking
    progress_data = {
        'completed': 0,
        'failed': 0
    }

    async def progress_callback(current, total, result):
        """Callback for batch progress updates."""
        progress_data['completed'] = current
        if not result['success']:
            progress_data['failed'] += 1

    # Create Rich progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task_id = progress.add_task("[cyan]Generating videos...", total=len(scenes))

        # Process batch
        result = await VideoGenerationService.process_video_batch(
            project_id=project_id,
            scenes=scenes,
            aspect_ratio='16:9',
            model='veo-3.0-generate-001',
            progress_callback=lambda c, t, r: progress.update(task_id, advance=1) or progress_callback(c, t, r)
        )

    # Display results
    console.print()
    if result['successful'] > 0:
        print_success(f"Successfully generated {result['successful']} videos")

    if result['failed'] > 0:
        print_error(f"Failed to generate {result['failed']} videos")
        print_info("Use 'nb-studio regenerate-video' to retry failed videos")

    print_info(f"\nNext steps:")
    print_info(f"  • Review videos: nb-studio show-videos {project_id}")
    print_info(f"  • Approve all: nb-studio approve-all-videos {project_id}")


async def show_videos(project_id: str, scene: Optional[int] = None):
    """
    Show all videos for a project.

    Args:
        project_id: The project ID
        scene: Optional scene number to filter by
    """
    print_header("Video Status", f"Project: {project_id}")

    # Get videos
    if scene:
        # Get scene ID first
        scenes = await SceneService.get_scenes_for_project(project_id)
        scene_record = next((s for s in scenes if s['scene_number'] == scene), None)
        if not scene_record:
            print_error(f"Scene {scene} not found")
            return
        videos = await VideoService.get_videos_for_scene(scene_record['id'])
        print_info(f"Showing videos for Scene {scene}")
    else:
        videos = await VideoService.get_videos_for_project(project_id)

    if not videos:
        print_warning("No videos found for this project")
        print_info(f"Generate videos with: nb-studio generate-videos {project_id}")
        return

    # Get approval stats
    stats = await VideoService.get_approval_stats(project_id)

    # Display grid
    display_videos_grid(videos, stats)

    # Suggest next actions
    console.print()
    if stats['failed'] > 0:
        print_info(f"💡 Regenerate failed videos: nb-studio regenerate-video {project_id} <video_id>")
    elif stats['completed'] > 0 and stats['approved'] < stats['total']:
        print_info(f"💡 Approve all videos: nb-studio approve-all-videos {project_id}")
    elif stats['approved'] == stats['total']:
        print_success("✓ All videos approved! Ready for final assembly")
        print_info(f"💡 Next: nb-studio assemble-video {project_id}")


async def show_video(project_id: str, video_id: int):
    """
    Show detailed information about a specific video.

    Args:
        project_id: The project ID
        video_id: The scene_video ID
    """
    # Get video
    video = await VideoService.get_video(video_id)

    if not video:
        print_error(f"Video {video_id} not found")
        return

    if video['project_id'] != project_id:
        print_error(f"Video {video_id} does not belong to project {project_id}")
        return

    # Get scene information
    scene = await SceneService.get_scene(video['scene_id'])

    # Display detail
    print_header("Video Details", f"Video ID: {video_id}")
    display_video_detail(video, scene)

    # Show action options
    console.print()
    status = video.get('status', 'unknown')

    if status == 'completed':
        print_info("Available actions:")
        print_info(f"  • Approve: nb-studio approve-video {project_id} {video_id}")
        print_info(f"  • Regenerate: nb-studio regenerate-video {project_id} {video_id}")
    elif status == 'approved':
        print_success("✓ Video approved")
    elif status == 'failed':
        print_error("Video generation failed")
        print_info(f"Retry: nb-studio regenerate-video {project_id} {video_id}")


async def approve_video(project_id: str, video_id: int):
    """
    Approve a single video.

    Args:
        project_id: The project ID
        video_id: The scene_video ID to approve
    """
    # Get video
    video = await VideoService.get_video(video_id)

    if not video:
        print_error(f"Video {video_id} not found")
        return

    if video['project_id'] != project_id:
        print_error(f"Video {video_id} does not belong to project {project_id}")
        return

    # Check if already approved
    if video['status'] == 'approved':
        print_info("Video is already approved")
        return

    # Approve
    await VideoService.approve_video(video_id)
    print_success(f"✓ Video {video_id} approved")

    # Check if all videos approved
    stats = await VideoService.get_approval_stats(project_id)
    if stats['approved'] == stats['total']:
        console.print()
        print_success("🎉 All videos approved!")
        print_info("Advancing workflow to assembly phase...")

        # Advance workflow
        await WorkflowService.advance_phase(project_id, 'assembly')
        print_info(f"💡 Next: nb-studio assemble-video {project_id}")
    else:
        remaining = stats['total'] - stats['approved']
        print_info(f"{remaining} videos remaining to approve")


async def approve_all_videos(project_id: str):
    """
    Approve all completed videos in a project.

    Args:
        project_id: The project ID
    """
    print_header("Approve All Videos", f"Project: {project_id}")

    # Get stats
    stats = await VideoService.get_approval_stats(project_id)

    if stats['total'] == 0:
        print_error("No videos found for this project")
        return

    if stats['approved'] == stats['total']:
        print_info("All videos are already approved")
        return

    # Get completed videos (not yet approved)
    all_videos = await VideoService.get_videos_for_project(project_id)
    videos_to_approve = [v for v in all_videos if v['status'] == 'completed']

    if not videos_to_approve:
        print_warning("No completed videos to approve")
        if stats['failed'] > 0:
            print_info(f"{stats['failed']} videos failed to generate")
        return

    # Show summary
    print_info(f"Videos to approve: {len(videos_to_approve)}")
    print_info(f"Current status: {stats['approved']}/{stats['total']} approved")

    # Confirm
    if not prompt_confirm(f"\nApprove {len(videos_to_approve)} videos?"):
        print_info("Approval cancelled")
        return

    # Approve all
    approved_count = 0
    for video in videos_to_approve:
        await VideoService.approve_video(video['id'])
        approved_count += 1

    print_success(f"✓ Approved {approved_count} videos")

    # Check if all videos are now approved
    updated_stats = await VideoService.get_approval_stats(project_id)
    if updated_stats['approved'] == updated_stats['total']:
        console.print()
        print_success("🎉 All videos approved!")
        print_info("Advancing workflow to assembly phase...")

        # Advance workflow
        await WorkflowService.advance_phase(project_id, 'assembly')
        print_success("✓ Workflow advanced to 'assembly' phase")
        print_info(f"\n💡 Next steps:")
        print_info(f"  • Assemble final video: nb-studio assemble-video {project_id}")
    else:
        remaining = updated_stats['total'] - updated_stats['approved']
        print_warning(f"{remaining} videos still need attention (failed/rejected)")


async def regenerate_video(
    project_id: str,
    video_id: int,
    motion_prompt: Optional[str] = None
):
    """
    Regenerate a video with optional custom motion prompt.

    Args:
        project_id: The project ID
        video_id: The scene_video ID to regenerate
        motion_prompt: Optional custom motion prompt
    """
    print_header("Regenerate Video", f"Video ID: {video_id}")

    # Get video
    video = await VideoService.get_video(video_id)

    if not video:
        print_error(f"Video {video_id} not found")
        return

    if video['project_id'] != project_id:
        print_error(f"Video {video_id} does not belong to project {project_id}")
        return

    current_prompt = video['prompt']
    print_info(f"Current motion prompt: {current_prompt[:100]}...")

    # Use custom prompt if provided
    new_prompt = motion_prompt if motion_prompt else current_prompt

    if motion_prompt:
        console.print(f"\n[bold]New motion prompt:[/bold] {new_prompt}\n")
        if not prompt_confirm("Use this new motion prompt?"):
            print_info("Using original prompt...")
            new_prompt = current_prompt

    # Regenerate
    print_info("Regenerating video...")
    print_info("⏱ This may take 30-60 seconds...")

    result = await VideoGenerationService.regenerate_scene_video(
        project_id=project_id,
        scene_video_id=video_id,
        custom_prompt=new_prompt if new_prompt != current_prompt else None
    )

    if result['success']:
        print_success("✓ Video regenerated successfully")
        new_video_id = result.get('scene_video_id')
        print_info(f"View result: nb-studio show-video {project_id} {new_video_id}")
    else:
        print_error("Failed to regenerate video")
        error_msg = result.get('error', 'Unknown error')
        print_error(f"Error: {error_msg}")
