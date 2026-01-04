"""
Frame Commands - CLI commands for frame generation and management.

Handles frame generation, display, approval, and regeneration workflows.
"""

import asyncio
from typing import Optional
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
import aiosqlite

from ...services.frame_service import FrameService
from ...services.batch_service import BatchService
from ...services.scene_service import SceneService
from ...services.workflow_service import WorkflowService
from ...services.claude_service import ClaudeService
from ..ui.display import (
    print_header, print_success, print_error, print_warning, print_info,
    display_frames_grid, display_frame_detail, console
)
from ..ui.prompts import prompt_confirm
from ...database import DATABASE_PATH


async def generate_frames(project_id: str):
    """
    Generate all pending frames for a project.

    Args:
        project_id: The project ID
    """
    print_header("Frame Generation", f"Project: {project_id}")

    # Get project details
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        project = await cursor.fetchone()

        if not project:
            print_error(f"Project {project_id} not found")
            return

        project = dict(project)

    # Get pending frames
    pending_frames = await FrameService.get_pending_frames(project_id)

    if not pending_frames:
        print_info("No pending frames to generate")
        print_info("All frames have already been generated or are in progress")
        return

    print_info(f"Found {len(pending_frames)} pending frames to generate")

    # Check if using mock mode
    import os
    is_mock = not os.getenv('GEMINI_API_KEY')
    if is_mock:
        print_warning("⚠ Using mock mode (GEMINI_API_KEY not set)")

    # Confirm before generating
    if not prompt_confirm(f"\nGenerate {len(pending_frames)} frames?"):
        print_info("Generation cancelled")
        return

    # Get aspect ratio from project
    aspect_ratio = project.get('aspect_ratio', '16:9')

    # Progress tracking
    progress_data = {
        'completed': 0,
        'failed': 0,
        'current_frame': None
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
        task_id = progress.add_task("[cyan]Generating frames...", total=len(pending_frames))

        # Process batch
        result = await BatchService.process_frame_batch(
            project_id=project_id,
            frames=pending_frames,
            aspect_ratio=aspect_ratio,
            progress_callback=lambda c, t, r: progress.update(task_id, advance=1) or progress_callback(c, t, r)
        )

    # Display results
    console.print()
    if result['successful'] > 0:
        print_success(f"Successfully generated {result['successful']} frames")

    if result['failed'] > 0:
        print_error(f"Failed to generate {result['failed']} frames")
        print_info("Use 'nb-studio regenerate-frame' to retry failed frames")

    print_info(f"\nNext steps:")
    print_info(f"  • Review frames: nb-studio show-frames {project_id}")
    print_info(f"  • Approve all: nb-studio approve-all-frames {project_id}")


async def show_frames(project_id: str, scene: Optional[int] = None):
    """
    Show all frames for a project.

    Args:
        project_id: The project ID
        scene: Optional scene number to filter by
    """
    print_header("Frame Status", f"Project: {project_id}")

    # Get frames
    if scene:
        # Get scene ID first
        scenes = await SceneService.get_scenes_for_project(project_id)
        scene_record = next((s for s in scenes if s['scene_number'] == scene), None)
        if not scene_record:
            print_error(f"Scene {scene} not found")
            return
        frames = await FrameService.get_frames_for_scene(scene_record['id'])
        print_info(f"Showing frames for Scene {scene}")
    else:
        frames = await FrameService.get_frames_for_project(project_id)

    if not frames:
        print_warning("No frames found for this project")
        print_info("Generate frames with: nb-studio generate-frames {project_id}")
        return

    # Get approval stats
    stats = await FrameService.get_approval_stats(project_id)

    # Display grid
    display_frames_grid(frames, stats)

    # Suggest next actions
    console.print()
    if stats['pending'] > 0:
        print_info(f"💡 Generate pending frames: nb-studio generate-frames {project_id}")
    elif stats['completed'] > 0 and stats['approved'] < stats['total']:
        print_info(f"💡 Approve all frames: nb-studio approve-all-frames {project_id}")
    elif stats['approved'] == stats['total']:
        print_success("✓ All frames approved! Ready for video generation")
        print_info(f"💡 Next: nb-studio generate-videos {project_id}")


async def show_frame(project_id: str, frame_id: int):
    """
    Show detailed information about a specific frame.

    Args:
        project_id: The project ID
        frame_id: The frame ID
    """
    # Get frame
    frame = await FrameService.get_frame(frame_id)

    if not frame:
        print_error(f"Frame {frame_id} not found")
        return

    if frame['project_id'] != project_id:
        print_error(f"Frame {frame_id} does not belong to project {project_id}")
        return

    # Get scene information
    scene = await SceneService.get_scene(frame['scene_id'])

    # Display detail
    print_header("Frame Details", f"Frame ID: {frame_id}")
    display_frame_detail(frame, scene)

    # Show action options
    console.print()
    status = frame.get('status', 'unknown')

    if status == 'completed':
        print_info("Available actions:")
        print_info(f"  • Approve: nb-studio approve-frame {project_id} {frame_id}")
        print_info(f"  • Regenerate: nb-studio regenerate-frame {project_id} {frame_id}")
    elif status == 'approved':
        print_success("✓ Frame approved")
    elif status == 'pending':
        print_info(f"Generate this frame: nb-studio generate-frames {project_id}")
    elif status == 'failed':
        print_error("Frame generation failed")
        print_info(f"Retry: nb-studio regenerate-frame {project_id} {frame_id}")


async def approve_frame(project_id: str, frame_id: int):
    """
    Approve a single frame.

    Args:
        project_id: The project ID
        frame_id: The frame ID to approve
    """
    # Get frame
    frame = await FrameService.get_frame(frame_id)

    if not frame:
        print_error(f"Frame {frame_id} not found")
        return

    if frame['project_id'] != project_id:
        print_error(f"Frame {frame_id} does not belong to project {project_id}")
        return

    # Check if already approved
    if frame['status'] == 'approved':
        print_info("Frame is already approved")
        return

    # Approve
    await FrameService.approve_frame(frame_id)
    print_success(f"✓ Frame {frame_id} approved")

    # Check if all frames approved
    stats = await FrameService.get_approval_stats(project_id)
    if stats['approved'] == stats['total']:
        console.print()
        print_success("🎉 All frames approved!")
        print_info("Advancing workflow to video generation phase...")

        # Advance workflow
        await WorkflowService.advance_phase(project_id, 'videos')
        print_info(f"💡 Next: nb-studio generate-videos {project_id}")
    else:
        remaining = stats['total'] - stats['approved']
        print_info(f"{remaining} frames remaining to approve")


async def approve_all_frames(project_id: str):
    """
    Approve all completed frames in a project.

    Args:
        project_id: The project ID
    """
    print_header("Approve All Frames", f"Project: {project_id}")

    # Get stats
    stats = await FrameService.get_approval_stats(project_id)

    if stats['total'] == 0:
        print_error("No frames found for this project")
        return

    if stats['approved'] == stats['total']:
        print_info("All frames are already approved")
        return

    # Get completed frames (not yet approved)
    all_frames = await FrameService.get_frames_for_project(project_id)
    frames_to_approve = [f for f in all_frames if f['status'] == 'completed']

    if not frames_to_approve:
        print_warning("No completed frames to approve")
        if stats['pending'] > 0:
            print_info(f"{stats['pending']} frames are still pending generation")
        if stats['failed'] > 0:
            print_info(f"{stats['failed']} frames failed to generate")
        return

    # Show summary
    print_info(f"Frames to approve: {len(frames_to_approve)}")
    print_info(f"Current status: {stats['approved']}/{stats['total']} approved")

    # Confirm
    if not prompt_confirm(f"\nApprove {len(frames_to_approve)} frames?"):
        print_info("Approval cancelled")
        return

    # Approve all
    approved_count = 0
    for frame in frames_to_approve:
        await FrameService.approve_frame(frame['id'])
        approved_count += 1

    print_success(f"✓ Approved {approved_count} frames")

    # Check if all frames are now approved
    updated_stats = await FrameService.get_approval_stats(project_id)
    if updated_stats['approved'] == updated_stats['total']:
        console.print()
        print_success("🎉 All frames approved!")
        print_info("Advancing workflow to video generation phase...")

        # Advance workflow
        await WorkflowService.advance_phase(project_id, 'videos')
        print_success("✓ Workflow advanced to 'videos' phase")
        print_info(f"\n💡 Next steps:")
        print_info(f"  • Generate videos: nb-studio generate-videos {project_id}")
    else:
        remaining = updated_stats['total'] - updated_stats['approved']
        print_warning(f"{remaining} frames still need attention (pending/failed/rejected)")


async def regenerate_frame(project_id: str, frame_id: int, feedback: Optional[str] = None):
    """
    Regenerate a frame with optional feedback for prompt refinement.

    Args:
        project_id: The project ID
        frame_id: The frame ID to regenerate
        feedback: Optional feedback for prompt refinement
    """
    print_header("Regenerate Frame", f"Frame ID: {frame_id}")

    # Get frame
    frame = await FrameService.get_frame(frame_id)

    if not frame:
        print_error(f"Frame {frame_id} not found")
        return

    if frame['project_id'] != project_id:
        print_error(f"Frame {frame_id} does not belong to project {project_id}")
        return

    current_prompt = frame['prompt']
    print_info(f"Current prompt: {current_prompt[:100]}...")

    # Refine prompt if feedback provided
    new_prompt = current_prompt
    if feedback:
        print_info("Refining prompt with Claude...")
        try:
            refined = await ClaudeService.refine_prompt(
                original_prompt=current_prompt,
                feedback=feedback
            )
            new_prompt = refined['refined_prompt']
            print_success("✓ Prompt refined")
            console.print(f"\n[bold]New prompt:[/bold] {new_prompt}\n")
        except Exception as e:
            print_error(f"Failed to refine prompt: {e}")
            print_info("Using original prompt...")

    # Update prompt if changed
    if new_prompt != current_prompt:
        await FrameService.update_frame_prompt(frame_id, new_prompt)

    # Mark as rejected with feedback
    await FrameService.reject_frame(frame_id, feedback)

    # Get project for aspect ratio
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        project = dict(await cursor.fetchone())

    aspect_ratio = project.get('aspect_ratio', '16:9')

    # Regenerate
    print_info("Regenerating frame...")

    # Update to pending status
    await FrameService.update_frame_status(frame_id, 'pending')

    # Create single-item batch
    result = await BatchService.process_frame_batch(
        project_id=project_id,
        frames=[frame],
        aspect_ratio=aspect_ratio
    )

    if result['successful'] > 0:
        print_success("✓ Frame regenerated successfully")
        print_info(f"View result: nb-studio show-frame {project_id} {frame_id}")
    else:
        print_error("Failed to regenerate frame")
        if result['errors']:
            error = result['errors'][0]
            print_error(f"Error: {error.get('error', 'Unknown error')}")
