import typer
import json
from typing import Optional
import aiosqlite

from ..ui.display import (
    console, print_header, print_success, print_error, print_info, print_warning
)
from ..ui.prompts import prompt_confirm, prompt_text
from ...database import DATABASE_PATH
from ...services.scene_service import SceneService
from ...services.workflow_service import WorkflowService

app = typer.Typer()


async def show_scenes(project_id: str):
    """Show all scenes for a project."""
    print_header("Project Scenes", f"Viewing scenes for {project_id}")
    
    try:
        scenes = await SceneService.get_scenes_for_project(project_id, ordered=True)
        
        if not scenes:
            print_error(f"No scenes found for project {project_id}")
            print_info("Generate scenes by approving a script first")
            print_info(f"Command: nb-studio approve-script {project_id}")
            raise typer.Exit(code=1)
        
        # Calculate total duration
        total_duration = sum(scene['duration'] for scene in scenes)
        
        console.print(f"\n[bold]Total Scenes:[/bold] {len(scenes)}")
        console.print(f"[bold]Total Duration:[/bold] {total_duration:.1f}s\n")
        
        # Display scenes in table
        from rich.table import Table
        table = Table(show_header=True, header_style="bold cyan", show_lines=True)
        table.add_column("#", justify="center", width=4)
        table.add_column("Description", width=40)
        table.add_column("Camera", justify="center", width=12)
        table.add_column("Duration", justify="center", width=8)
        table.add_column("Transition", justify="center", width=10)
        
        for scene in scenes:
            table.add_row(
                str(scene['scene_number']),
                scene['description'][:60] + ("..." if len(scene['description']) > 60 else ""),
                scene['camera_direction'] or "static",
                f"{scene['duration']}s",
                scene['transition_type'] or "cut"
            )
        
        console.print(table)
        
        console.print("\n[bold]View scene details:[/bold]")
        console.print(f"  nb-studio show-scene {project_id} <scene_number>")
        
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"  Approve scenes: [cyan]nb-studio approve-scenes {project_id}[/cyan]")
        
    except Exception as e:
        print_error(f"Failed to show scenes: {str(e)}")
        raise typer.Exit(code=1)


async def show_scene(project_id: str, scene_number: int):
    """Show detailed information about a specific scene."""
    print_header(f"Scene {scene_number}", f"Details for project {project_id}")
    
    try:
        scenes = await SceneService.get_scenes_for_project(project_id)
        scene = next((s for s in scenes if s['scene_number'] == scene_number), None)
        
        if not scene:
            print_error(f"Scene {scene_number} not found")
            raise typer.Exit(code=1)
        
        from rich.panel import Panel
        
        # Scene info
        info = f"""[bold]Scene Number:[/bold] {scene['scene_number']}
[bold]Duration:[/bold] {scene['duration']}s
[bold]Camera:[/bold] {scene['camera_direction'] or 'static'}
[bold]Transition:[/bold] {scene['transition_type'] or 'cut'}

[bold]Description:[/bold]
{scene['description']}

[bold]Opening Frame Prompt:[/bold]
{scene['opening_frame_prompt']}
"""
        
        if scene['closing_frame_prompt']:
            info += f"""
[bold]Closing Frame Prompt:[/bold]
{scene['closing_frame_prompt']}
"""
        
        console.print(Panel(info, border_style="cyan"))
        
        console.print("\n[bold]Actions:[/bold]")
        console.print(f"  Edit scene: [cyan]nb-studio edit-scene {project_id} {scene_number}[/cyan]")
        console.print(f"  View all scenes: [cyan]nb-studio show-scenes {project_id}[/cyan]")
        
    except Exception as e:
        print_error(f"Failed to show scene: {str(e)}")
        raise typer.Exit(code=1)


async def approve_scenes(project_id: str):
    """Approve scenes and create frame generation tasks."""
    print_header("Approve Scenes", f"Approving scenes for {project_id}")
    
    try:
        scenes = await SceneService.get_scenes_for_project(project_id, ordered=True)
        
        if not scenes:
            print_error(f"No scenes found for project {project_id}")
            raise typer.Exit(code=1)
        
        # Show summary
        total_duration = sum(scene['duration'] for scene in scenes)
        frame_count = len(scenes)  # Opening frames
        frame_count += sum(1 for s in scenes if s['closing_frame_prompt'])  # Closing frames
        
        console.print(f"\n[bold]Scenes:[/bold] {len(scenes)}")
        console.print(f"[bold]Total Duration:[/bold] {total_duration:.1f}s")
        console.print(f"[bold]Frames to Generate:[/bold] {frame_count}")
        
        if not prompt_confirm("\nApprove these scenes and proceed to frame generation?"):
            print_info("Scene approval cancelled")
            return
        
        # Create frame records
        console.print("\n[bold]Creating frame generation tasks...[/bold]")
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            for scene in scenes:
                # Create opening frame
                await db.execute(
                    """INSERT INTO frames (project_id, scene_id, frame_type, prompt, status)
                       VALUES (?, ?, ?, ?, ?)""",
                    (project_id, scene['id'], 'opening', scene['opening_frame_prompt'], 'pending')
                )
                
                # Create closing frame if specified
                if scene['closing_frame_prompt']:
                    await db.execute(
                        """INSERT INTO frames (project_id, scene_id, frame_type, prompt, status)
                           VALUES (?, ?, ?, ?, ?)""",
                        (project_id, scene['id'], 'closing', scene['closing_frame_prompt'], 'pending')
                    )
            
            await db.commit()
        
        print_success(f"Created {frame_count} frame generation tasks")
        
        # Update workflow
        await WorkflowService.advance_phase(project_id, 'frames')
        
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"1. Generate frames: [cyan]nb-studio generate-frames {project_id}[/cyan]")
        console.print(f"2. View frame status: [cyan]nb-studio show-frames {project_id}[/cyan]")
        
    except Exception as e:
        print_error(f"Failed to approve scenes: {str(e)}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)


async def edit_scene(project_id: str, scene_number: int):
    """Edit a scene's properties."""
    print_header(f"Edit Scene {scene_number}", f"Editing scene for {project_id}")
    
    try:
        scenes = await SceneService.get_scenes_for_project(project_id)
        scene = next((s for s in scenes if s['scene_number'] == scene_number), None)
        
        if not scene:
            print_error(f"Scene {scene_number} not found")
            raise typer.Exit(code=1)
        
        console.print("\n[bold]What would you like to edit?[/bold]")
        console.print("1. Description")
        console.print("2. Opening frame prompt")
        console.print("3. Closing frame prompt")
        console.print("4. Camera direction")
        console.print("5. Duration")
        
        choice = prompt_text("Enter number (1-5)", required=True)
        
        updates = {}
        
        if choice == "1":
            new_desc = prompt_text("New description", default=scene['description'])
            updates['description'] = new_desc
        elif choice == "2":
            new_prompt = prompt_text("New opening frame prompt", default=scene['opening_frame_prompt'])
            updates['opening_frame_prompt'] = new_prompt
        elif choice == "3":
            new_prompt = prompt_text("New closing frame prompt", default=scene['closing_frame_prompt'] or "")
            updates['closing_frame_prompt'] = new_prompt if new_prompt else None
        elif choice == "4":
            camera_options = ["static", "pan-left", "pan-right", "zoom-in", "zoom-out", "tilt-up", "tilt-down"]
            console.print(f"\nOptions: {', '.join(camera_options)}")
            new_camera = prompt_text("New camera direction", default=scene['camera_direction'] or "static")
            updates['camera_direction'] = new_camera
        elif choice == "5":
            new_duration = prompt_text("New duration (seconds)", default=str(scene['duration']))
            updates['duration'] = float(new_duration)
        else:
            print_error("Invalid choice")
            return
        
        # Update scene
        updated_scene = await SceneService.update_scene(scene['id'], updates)
        print_success(f"Scene {scene_number} updated")
        
        # Show updated scene
        console.print("\n[bold]Updated scene:[/bold]")
        await show_scene(project_id, scene_number)
        
    except Exception as e:
        print_error(f"Failed to edit scene: {str(e)}")
        raise typer.Exit(code=1)
