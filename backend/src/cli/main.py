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
from .commands import project

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
