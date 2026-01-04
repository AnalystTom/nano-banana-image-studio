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
from .commands import project, script, scenes

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
