import typer
from rich.console import Console
from typing import Optional
import asyncio

# Create main Typer app
app = typer.Typer(
    name="nb-studio",
    help="Nano Banana Video Production CLI - AI-assisted video workflow",
    add_completion=False,
    rich_markup_mode="rich"
)

# Create Rich console for output
console = Console()

# Import command modules
from .commands import project, script, scenes, frames, videos

# Main commands at root level
@app.command("create-video")
def create_video_command(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Project name"),
    wizard: bool = typer.Option(False, "--wizard", "-w", help="Use wizard mode")
):
    """Create a new video production project."""
    asyncio.run(project.create_video(name=name, wizard=wizard))

@app.command("list-projects")
def list_projects_command(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status")
):
    """List all video projects."""
    asyncio.run(project.list_projects(status=status))

@app.command("show-project")
def show_project_command(
    project_id: str = typer.Argument(..., help="Project ID")
):
    """Show detailed information about a project."""
    asyncio.run(project.show_project(project_id=project_id))

@app.command("delete-project")
def delete_project_command(
    project_id: str = typer.Argument(..., help="Project ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
):
    """Delete a video project."""
    asyncio.run(project.delete_project(project_id=project_id, force=force))

@app.command("resume")
def resume_command(
    project_id: str = typer.Argument(..., help="Project ID to resume")
):
    """Resume an interrupted project."""
    asyncio.run(project.resume_project(project_id=project_id))

# Script commands
@app.command("generate-script")
def generate_script_command(
    project_id: str = typer.Argument(..., help="Project ID"),
    regenerate: bool = typer.Option(False, "--regenerate", "-r", help="Regenerate even if script exists")
):
    """Generate a script for the video project."""
    asyncio.run(script.generate_script(project_id=project_id, regenerate=regenerate))

@app.command("show-script")
def show_script_command(
    project_id: str = typer.Argument(..., help="Project ID"),
    version: Optional[int] = typer.Option(None, "--version", "-v", help="Specific version to show")
):
    """Show the script for a project."""
    asyncio.run(script.show_script(project_id=project_id, version=version))

@app.command("approve-script")
def approve_script_command(
    project_id: str = typer.Argument(..., help="Project ID")
):
    """Approve the script and generate scene breakdown."""
    asyncio.run(script.approve_script(project_id=project_id))

@app.command("list-scripts")
def list_scripts_command(
    project_id: str = typer.Argument(..., help="Project ID")
):
    """List all script versions for a project."""
    asyncio.run(script.list_scripts(project_id=project_id))

# Scene commands
@app.command("show-scenes")
def show_scenes_command(
    project_id: str = typer.Argument(..., help="Project ID")
):
    """Show all scenes for a project."""
    asyncio.run(scenes.show_scenes(project_id=project_id))

@app.command("show-scene")
def show_scene_command(
    project_id: str = typer.Argument(..., help="Project ID"),
    scene_number: int = typer.Argument(..., help="Scene number")
):
    """Show detailed information about a specific scene."""
    asyncio.run(scenes.show_scene(project_id=project_id, scene_number=scene_number))

@app.command("approve-scenes")
def approve_scenes_command(
    project_id: str = typer.Argument(..., help="Project ID")
):
    """Approve scenes and create frame generation tasks."""
    asyncio.run(scenes.approve_scenes(project_id=project_id))

@app.command("edit-scene")
def edit_scene_command(
    project_id: str = typer.Argument(..., help="Project ID"),
    scene_number: int = typer.Argument(..., help="Scene number")
):
    """Edit a scene's properties."""
    asyncio.run(scenes.edit_scene(project_id=project_id, scene_number=scene_number))

# Frame commands
@app.command("generate-frames")
def generate_frames_command(
    project_id: str = typer.Argument(..., help="Project ID")
):
    """Generate all pending frames for a project."""
    asyncio.run(frames.generate_frames(project_id=project_id))

@app.command("show-frames")
def show_frames_command(
    project_id: str = typer.Argument(..., help="Project ID"),
    scene: Optional[int] = typer.Option(None, "--scene", "-s", help="Filter by scene number")
):
    """Show all frames for a project."""
    asyncio.run(frames.show_frames(project_id=project_id, scene=scene))

@app.command("show-frame")
def show_frame_command(
    project_id: str = typer.Argument(..., help="Project ID"),
    frame_id: int = typer.Argument(..., help="Frame ID")
):
    """Show detailed information about a specific frame."""
    asyncio.run(frames.show_frame(project_id=project_id, frame_id=frame_id))

@app.command("approve-frame")
def approve_frame_command(
    project_id: str = typer.Argument(..., help="Project ID"),
    frame_id: int = typer.Argument(..., help="Frame ID")
):
    """Approve a single frame."""
    asyncio.run(frames.approve_frame(project_id=project_id, frame_id=frame_id))

@app.command("approve-all-frames")
def approve_all_frames_command(
    project_id: str = typer.Argument(..., help="Project ID")
):
    """Approve all completed frames in a project."""
    asyncio.run(frames.approve_all_frames(project_id=project_id))

@app.command("regenerate-frame")
def regenerate_frame_command(
    project_id: str = typer.Argument(..., help="Project ID"),
    frame_id: int = typer.Argument(..., help="Frame ID"),
    feedback: Optional[str] = typer.Option(None, "--feedback", "-f", help="Feedback for prompt refinement")
):
    """Regenerate a frame with optional feedback."""
    asyncio.run(frames.regenerate_frame(project_id=project_id, frame_id=frame_id, feedback=feedback))

# Video commands
@app.command("generate-videos")
def generate_videos_command(
    project_id: str = typer.Argument(..., help="Project ID")
):
    """Generate videos for all scenes in a project."""
    asyncio.run(videos.generate_videos(project_id=project_id))

@app.command("show-videos")
def show_videos_command(
    project_id: str = typer.Argument(..., help="Project ID"),
    scene: Optional[int] = typer.Option(None, "--scene", "-s", help="Filter by scene number")
):
    """Show all videos for a project."""
    asyncio.run(videos.show_videos(project_id=project_id, scene=scene))

@app.command("show-video")
def show_video_command(
    project_id: str = typer.Argument(..., help="Project ID"),
    video_id: int = typer.Argument(..., help="Video ID")
):
    """Show detailed information about a specific video."""
    asyncio.run(videos.show_video(project_id=project_id, video_id=video_id))

@app.command("approve-video")
def approve_video_command(
    project_id: str = typer.Argument(..., help="Project ID"),
    video_id: int = typer.Argument(..., help="Video ID")
):
    """Approve a single video."""
    asyncio.run(videos.approve_video(project_id=project_id, video_id=video_id))

@app.command("approve-all-videos")
def approve_all_videos_command(
    project_id: str = typer.Argument(..., help="Project ID")
):
    """Approve all completed videos in a project."""
    asyncio.run(videos.approve_all_videos(project_id=project_id))

@app.command("regenerate-video")
def regenerate_video_command(
    project_id: str = typer.Argument(..., help="Project ID"),
    video_id: int = typer.Argument(..., help="Video ID"),
    motion_prompt: Optional[str] = typer.Option(None, "--motion-prompt", "-m", help="Custom motion prompt")
):
    """Regenerate a video with optional custom motion prompt."""
    asyncio.run(videos.regenerate_video(project_id=project_id, video_id=video_id, motion_prompt=motion_prompt))

@app.callback()
def callback():
    """
    Nano Banana Video Production CLI
    
    Create professional short-form videos through an AI-assisted workflow.
    """
    pass

# Entry point for CLI
def main():
    """Main entry point for the CLI."""
    app()

if __name__ == "__main__":
    main()
