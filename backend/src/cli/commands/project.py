import typer
import json
import uuid
from datetime import datetime
from typing import Optional
import aiosqlite
from pathlib import Path

from ..ui.display import (
    console, print_header, print_success, print_error, print_info,
    display_project_table, display_project_detail
)
from ..ui.prompts import prompt_project_details, prompt_confirm
from ...database import DATABASE_PATH
from ...services.workflow_service import WorkflowService

app = typer.Typer()

# Project workspace directory
PROJECTS_DIR = Path(__file__).parent.parent.parent.parent.parent / 'projects'
PROJECTS_DIR.mkdir(exist_ok=True)

def generate_project_id() -> str:
    """Generate unique project ID."""
    return f"proj_{uuid.uuid4().hex[:12]}"

async def create_project_workspace(project_id: str, name: str) -> Path:
    """Create project directory structure."""
    project_dir = PROJECTS_DIR / project_id
    project_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (project_dir / 'frames').mkdir(exist_ok=True)
    (project_dir / 'videos').mkdir(exist_ok=True)
    (project_dir / 'output').mkdir(exist_ok=True)
    (project_dir / 'logs').mkdir(exist_ok=True)
    
    # Create project.json metadata file
    metadata = {
        "id": project_id,
        "name": name,
        "created_at": datetime.now().isoformat()
    }
    
    with open(project_dir / 'project.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return project_dir

async def create_video(name: Optional[str] = None, wizard: bool = False):
    """Create a new video production project."""
    print_header("Create New Video Project", "Initialize a new video production workflow")
    
    try:
        # Get project details
        if wizard or not name:
            details = prompt_project_details()
            project_name = details['name']
            config = {
                "aspect_ratio": details['aspect_ratio'],
                "target_duration": int(details['target_duration'].rstrip('s')),
                "style": details['style'],
                "narrative": details['narrative']
            }
        else:
            project_name = name
            # Use defaults for non-wizard mode
            narrative = typer.prompt("Enter your video narrative/concept")
            config = {
                "aspect_ratio": "16:9",
                "target_duration": 30,
                "style": "cinematic",
                "narrative": narrative
            }
        
        # Generate project ID
        project_id = generate_project_id()
        
        # Create database entry
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Insert project
            await db.execute(
                """INSERT INTO projects (id, name, status, config)
                   VALUES (?, ?, ?, ?)""",
                (project_id, project_name, 'planning', json.dumps(config))
            )
            
            # Create workflow
            await db.execute(
                """INSERT INTO workflows (project_id, current_phase)
                   VALUES (?, ?)""",
                (project_id, 'planning')
            )
            
            await db.commit()
        
        # Create project workspace
        project_dir = await create_project_workspace(project_id, project_name)
        
        print_success(f"Project created: {project_name}")
        print_info(f"Project ID: {project_id}")
        print_info(f"Workspace: {project_dir}")
        
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"1. Generate script: [cyan]nb-studio generate-script {project_id}[/cyan]")
        console.print(f"2. Or resume anytime: [cyan]nb-studio resume {project_id}[/cyan]")
        
    except Exception as e:
        print_error(f"Failed to create project: {str(e)}")
        raise typer.Exit(code=1)

async def list_projects(status: Optional[str] = None):
    """List all video projects."""
    print_header("Video Projects")
    
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            
            if status:
                query = "SELECT * FROM projects WHERE status = ? ORDER BY updated_at DESC"
                cursor = await db.execute(query, (status,))
            else:
                query = "SELECT * FROM projects ORDER BY updated_at DESC"
                cursor = await db.execute(query)
            
            rows = await cursor.fetchall()
            
            if not rows:
                print_info("No projects found")
                return
            
            projects = [dict(row) for row in rows]
            display_project_table(projects)
            
    except Exception as e:
        print_error(f"Failed to list projects: {str(e)}")
        raise typer.Exit(code=1)

async def show_project(project_id: str):
    """Show detailed information about a project."""
    print_header(f"Project Details: {project_id}")
    
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            
            # Get project
            cursor = await db.execute(
                "SELECT * FROM projects WHERE id = ?", (project_id,)
            )
            project_row = await cursor.fetchone()
            
            if not project_row:
                print_error(f"Project not found: {project_id}")
                raise typer.Exit(code=1)
            
            project = dict(project_row)
            
            # Get workflow
            cursor = await db.execute(
                "SELECT * FROM workflows WHERE project_id = ?", (project_id,)
            )
            workflow_row = await cursor.fetchone()
            workflow = dict(workflow_row) if workflow_row else {}
            
            # Get script count
            cursor = await db.execute(
                "SELECT COUNT(*) as count FROM scripts WHERE project_id = ?",
                (project_id,)
            )
            script_count = (await cursor.fetchone())['count']
            
            # Get scene count
            cursor = await db.execute(
                "SELECT COUNT(*) as count FROM scenes WHERE project_id = ?",
                (project_id,)
            )
            scene_count = (await cursor.fetchone())['count']
            
            # Display
            display_project_detail(project, workflow)
            
            # Display stats
            console.print(f"\n[bold]Statistics:[/bold]")
            console.print(f"  Scripts: {script_count}")
            console.print(f"  Scenes: {scene_count}")
            
    except Exception as e:
        print_error(f"Failed to show project: {str(e)}")
        raise typer.Exit(code=1)

async def delete_project(project_id: str, force: bool = False):
    """Delete a video project."""
    print_header(f"Delete Project: {project_id}")
    
    try:
        # Check if project exists
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM projects WHERE id = ?", (project_id,)
            )
            project = await cursor.fetchone()
            
            if not project:
                print_error(f"Project not found: {project_id}")
                raise typer.Exit(code=1)
            
            # Confirm deletion
            if not force:
                if not prompt_confirm(f"Delete project '{project['name']}'?"):
                    print_info("Deletion cancelled")
                    return
            
            # Delete from database (cascade will handle related tables)
            await db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            await db.commit()
        
        # Delete project workspace
        project_dir = PROJECTS_DIR / project_id
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)
        
        print_success(f"Project deleted: {project['name']}")
        
    except Exception as e:
        print_error(f"Failed to delete project: {str(e)}")
        raise typer.Exit(code=1)

async def resume_project(project_id: str):
    """Resume an interrupted project."""
    print_header(f"Resume Project: {project_id}")
    
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            
            # Get project
            cursor = await db.execute(
                "SELECT * FROM projects WHERE id = ?", (project_id,)
            )
            project = await cursor.fetchone()
            
            if not project:
                print_error(f"Project not found: {project_id}")
                raise typer.Exit(code=1)
            
            # Get workflow
            cursor = await db.execute(
                "SELECT * FROM workflows WHERE project_id = ?", (project_id,)
            )
            workflow = await cursor.fetchone()
            
            if not workflow:
                print_error(f"No workflow found for project")
                raise typer.Exit(code=1)
            
            current_phase = workflow['current_phase']
            
            console.print(f"[bold]Project:[/bold] {project['name']}")
            console.print(f"[bold]Status:[/bold] {project['status']}")
            console.print(f"[bold]Current Phase:[/bold] {current_phase}")
            
            # Guide user to next command based on phase
            phase_commands = {
                'planning': f"nb-studio generate-script {project_id}",
                'script': f"nb-studio show-script {project_id}",
                'scenes': f"nb-studio show-scenes {project_id}",
                'frames': f"nb-studio show-frames {project_id}",
                'videos': f"nb-studio show-videos {project_id}",
                'assembly': f"nb-studio show-timeline {project_id}",
            }
            
            next_cmd = phase_commands.get(current_phase, f"nb-studio show-project {project_id}")
            
            console.print(f"\n[bold]Next step:[/bold]")
            console.print(f"  [cyan]{next_cmd}[/cyan]")
            
    except Exception as e:
        print_error(f"Failed to resume project: {str(e)}")
        raise typer.Exit(code=1)
