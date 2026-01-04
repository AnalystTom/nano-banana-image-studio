import typer
import json
from typing import Optional
import aiosqlite

from ..ui.display import (
    console, print_header, print_success, print_error, print_info, print_warning,
    display_script, display_markdown
)
from ..ui.prompts import prompt_confirm, prompt_text
from ...database import DATABASE_PATH
from ...services.claude_service import ClaudeService
from ...services.script_service import ScriptService
from ...services.scene_service import SceneService
from ...services.workflow_service import WorkflowService

app = typer.Typer()


async def generate_script(project_id: str, regenerate: bool = False):
    """Generate a script for a project using Claude."""
    print_header("Generate Script", f"Creating script for project {project_id}")
    
    try:
        # Get project details
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            project = await cursor.fetchone()
            
            if not project:
                print_error(f"Project not found: {project_id}")
                raise typer.Exit(code=1)
            
            project_dict = dict(project)
            config = json.loads(project_dict['config'])
        
        # Check if script already exists
        if not regenerate:
            existing = await ScriptService.get_latest_script(project_id)
            if existing:
                print_warning(f"Script already exists (version {existing['version']})")
                if not prompt_confirm("Generate a new version?"):
                    print_info("Script generation cancelled")
                    return
        
        # Generate script using Claude
        console.print("\n[bold magenta]Claude is writing your script...[/bold magenta]\n")
        
        script_result = await ClaudeService.generate_script(
            project_id=project_id,
            narrative=config['narrative'],
            style=config.get('style', 'cinematic'),
            target_duration=config.get('target_duration', 30),
            aspect_ratio=config.get('aspect_ratio', '16:9')
        )
        
        # Save script to database
        next_version = await ScriptService.get_next_version(project_id)
        script = await ScriptService.create_script(
            project_id=project_id,
            content=script_result['content'],
            version=next_version
        )
        
        # Display script
        display_script(script['content'], script['scene_count'])
        
        print_success(f"Script generated (version {script['version']})")
        print_info(f"Scenes identified: {script['scene_count']}")
        if script_result.get('is_mock'):
            print_warning("⚠ Using mock mode (ANTHROPIC_API_KEY not set)")
        else:
            print_info(f"Tokens used: {script_result.get('token_count', 0)}")
        
        # Update workflow
        await WorkflowService.advance_phase(project_id, 'script')
        
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"1. Review script: [cyan]nb-studio show-script {project_id}[/cyan]")
        console.print(f"2. Approve script: [cyan]nb-studio approve-script {project_id}[/cyan]")
        console.print(f"3. Regenerate: [cyan]nb-studio generate-script {project_id} --regenerate[/cyan]")
        
    except Exception as e:
        print_error(f"Failed to generate script: {str(e)}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)


async def show_script(project_id: str, version: Optional[int] = None):
    """Show the script for a project."""
    print_header("Project Script", f"Viewing script for {project_id}")
    
    try:
        if version:
            # Get specific version
            scripts = await ScriptService.get_scripts_for_project(project_id)
            script = next((s for s in scripts if s['version'] == version), None)
            if not script:
                print_error(f"Script version {version} not found")
                raise typer.Exit(code=1)
        else:
            # Get latest
            script = await ScriptService.get_latest_script(project_id)
            if not script:
                print_error(f"No script found for project {project_id}")
                print_info(f"Generate one with: nb-studio generate-script {project_id}")
                raise typer.Exit(code=1)
        
        # Display script
        console.print(f"\n[bold]Version:[/bold] {script['version']}")
        console.print(f"[bold]Created:[/bold] {script['created_at']}")
        console.print(f"[bold]Scenes:[/bold] {script['scene_count']}")
        console.print(f"[bold]Approved:[/bold] {'✓ Yes' if script['approved'] else '✗ No'}")
        if script['approved']:
            console.print(f"[bold]Approved at:[/bold] {script['approved_at']}")
        
        console.print("\n" + "─" * 80 + "\n")
        display_markdown(script['content'])
        console.print("\n" + "─" * 80)
        
        if not script['approved']:
            console.print("\n[bold]Actions:[/bold]")
            console.print(f"  Approve: [cyan]nb-studio approve-script {project_id}[/cyan]")
            console.print(f"  Regenerate: [cyan]nb-studio generate-script {project_id} --regenerate[/cyan]")
        
    except Exception as e:
        print_error(f"Failed to show script: {str(e)}")
        raise typer.Exit(code=1)


async def approve_script(project_id: str):
    """Approve the current script and generate scenes."""
    print_header("Approve Script", f"Approving script for {project_id}")
    
    try:
        # Get latest script
        script = await ScriptService.get_latest_script(project_id)
        if not script:
            print_error(f"No script found for project {project_id}")
            raise typer.Exit(code=1)
        
        if script['approved']:
            print_warning(f"Script version {script['version']} is already approved")
            if not prompt_confirm("Approve anyway (will re-generate scenes)?"):
                return
        
        # Show script summary
        console.print(f"\n[bold]Script version {script['version']}:[/bold]")
        console.print(f"Scenes: {script['scene_count']}")
        console.print(f"Preview: {script['content'][:200]}...\n")
        
        if not prompt_confirm("Approve this script and generate scenes?"):
            print_info("Script approval cancelled")
            return
        
        # Approve script
        approved_script = await ScriptService.approve_script(script['id'])
        print_success(f"Script approved (version {approved_script['version']})")
        
        # Generate scene breakdown
        console.print("\n[bold magenta]Claude is breaking down the script into scenes...[/bold magenta]\n")
        
        # Get project config
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT config FROM projects WHERE id = ?", (project_id,))
            row = await cursor.fetchone()
            config = json.loads(row['config'])
        
        scenes_data = await ClaudeService.breakdown_into_scenes(
            project_id=project_id,
            script_content=approved_script['content'],
            target_duration=config.get('target_duration', 30),
            style=config.get('style', 'cinematic')
        )
        
        # Ensure consistency
        scenes_data = await ClaudeService.ensure_consistency(
            project_id=project_id,
            scenes=scenes_data,
            style=config.get('style', 'cinematic')
        )
        
        # Save scenes to database
        scenes = await SceneService.create_scenes(
            project_id=project_id,
            script_id=approved_script['id'],
            scenes_data=scenes_data
        )
        
        print_success(f"Created {len(scenes)} scenes")
        
        # Update workflow
        await WorkflowService.advance_phase(project_id, 'scenes')
        
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"1. Review scenes: [cyan]nb-studio show-scenes {project_id}[/cyan]")
        console.print(f"2. Approve scenes: [cyan]nb-studio approve-scenes {project_id}[/cyan]")
        
    except Exception as e:
        print_error(f"Failed to approve script: {str(e)}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)


async def list_scripts(project_id: str):
    """List all script versions for a project."""
    print_header("Script Versions", f"All versions for {project_id}")
    
    try:
        scripts = await ScriptService.get_scripts_for_project(project_id)
        
        if not scripts:
            print_info(f"No scripts found for project {project_id}")
            return
        
        from rich.table import Table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Version", justify="center")
        table.add_column("Scenes", justify="center")
        table.add_column("Approved", justify="center")
        table.add_column("Created", justify="right")
        
        for script in scripts:
            table.add_row(
                str(script['version']),
                str(script['scene_count']),
                "✓" if script['approved'] else "✗",
                script['created_at'][:19]
            )
        
        console.print(table)
        
        console.print(f"\n[bold]View a specific version:[/bold]")
        console.print(f"  nb-studio show-script {project_id} --version N")
        
    except Exception as e:
        print_error(f"Failed to list scripts: {str(e)}")
        raise typer.Exit(code=1)
