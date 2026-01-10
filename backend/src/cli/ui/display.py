from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.tree import Tree
from rich.markdown import Markdown
from typing import List, Dict, Any, Optional

console = Console()

# Color scheme constants
COLOR_SUCCESS = "green"
COLOR_ERROR = "red"
COLOR_WARNING = "yellow"
COLOR_INFO = "blue"
COLOR_CLAUDE = "magenta"
COLOR_PROMPT = "cyan"

def print_header(title: str, subtitle: Optional[str] = None):
    """Display a formatted header panel."""
    content = f"[bold]{title}[/bold]"
    if subtitle:
        content += f"\n{subtitle}"
    
    console.print(Panel(
        content,
        border_style=COLOR_INFO,
        padding=(1, 2)
    ))

def print_success(message: str):
    """Display a success message."""
    console.print(f"[{COLOR_SUCCESS}]✓[/{COLOR_SUCCESS}] {message}")

def print_error(message: str):
    """Display an error message."""
    console.print(f"[{COLOR_ERROR}]✗[/{COLOR_ERROR}] {message}")

def print_warning(message: str):
    """Display a warning message."""
    console.print(f"[{COLOR_WARNING}]⚠[/{COLOR_WARNING}] {message}")

def print_info(message: str):
    """Display an info message."""
    console.print(f"[{COLOR_INFO}]ℹ[/{COLOR_INFO}] {message}")

def display_project_table(projects: List[Dict[str, Any]]):
    """Display projects in a formatted table."""
    table = Table(title="Video Projects", show_header=True, header_style="bold cyan")
    
    table.add_column("ID", style="dim", width=15)
    table.add_column("Name", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Created", justify="right")
    table.add_column("Updated", justify="right")
    
    for project in projects:
        status_color = {
            "planning": COLOR_INFO,
            "script": COLOR_PROMPT,
            "frames": COLOR_WARNING,
            "videos": COLOR_WARNING,
            "assembly": COLOR_WARNING,
            "completed": COLOR_SUCCESS
        }.get(project['status'], "white")
        
        table.add_row(
            project['id'],
            project['name'],
            f"[{status_color}]{project['status']}[/{status_color}]",
            project['created_at'][:10] if project.get('created_at') else 'N/A',
            project['updated_at'][:10] if project.get('updated_at') else 'N/A'
        )
    
    console.print(table)

def display_project_detail(project: Dict[str, Any], workflow: Dict[str, Any]):
    """Display detailed project information."""
    # Project info panel
    info_content = f"""[bold]Name:[/bold] {project['name']}
[bold]ID:[/bold] {project['id']}
[bold]Status:[/bold] {project['status']}
[bold]Created:[/bold] {project.get('created_at', 'N/A')}
[bold]Updated:[/bold] {project.get('updated_at', 'N/A')}"""
    
    console.print(Panel(info_content, title="Project Information", border_style=COLOR_INFO))
    
    # Workflow status
    workflow_tree = Tree(f"[bold]Current Phase:[/bold] {workflow['current_phase']}")
    console.print(Panel(workflow_tree, title="Workflow Status", border_style=COLOR_PROMPT))

def create_progress_bar() -> Progress:
    """Create a configured progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    )

def display_markdown(content: str):
    """Display markdown content."""
    md = Markdown(content)
    console.print(md)

def display_script(script_content: str, scene_count: int):
    """Display script in a formatted panel."""
    console.print(Panel(
        script_content[:500] + ("..." if len(script_content) > 500 else ""),
        title=f"Generated Script ({scene_count} scenes)",
        border_style=COLOR_CLAUDE,
        padding=(1, 2)
    ))

def display_frames_grid(frames: List[Dict[str, Any]], stats: Optional[Dict[str, int]] = None):
    """Display frames in a table format with status indicators."""
    table = Table(title="Frame Generation Status", show_header=True, header_style="bold cyan")

    table.add_column("ID", style="dim", width=8)
    table.add_column("Scene", justify="center", width=8)
    table.add_column("Type", justify="center", width=10)
    table.add_column("Status", justify="center", width=12)
    table.add_column("Image", style="dim", width=30)
    table.add_column("Created", justify="right", width=12)

    # Status colors mapping
    status_colors = {
        'pending': COLOR_WARNING,
        'generating': COLOR_INFO,
        'completed': COLOR_SUCCESS,
        'approved': "bright_green",
        'failed': COLOR_ERROR,
        'rejected': "orange"
    }

    for frame in frames:
        status = frame.get('status', 'unknown')
        status_color = status_colors.get(status, "white")

        table.add_row(
            str(frame['id']),
            f"Scene {frame.get('scene_number', '?')}",
            frame.get('frame_type', 'unknown').title(),
            f"[{status_color}]{status}[/{status_color}]",
            frame.get('image_filename', 'None')[:30] if frame.get('image_filename') else '-',
            frame.get('created_at', 'N/A')[:10] if frame.get('created_at') else 'N/A'
        )

    console.print(table)

    # Display statistics if provided
    if stats:
        stats_content = f"""[bold]Total:[/bold] {stats['total']} frames
[bold]Approved:[/bold] [{status_colors['approved']}]{stats['approved']}[/{status_colors['approved']}] | [bold]Completed:[/bold] [{status_colors['completed']}]{stats['completed']}[/{status_colors['completed']}] | [bold]Pending:[/bold] [{status_colors['pending']}]{stats['pending']}[/{status_colors['pending']}]
[bold]Failed:[/bold] [{status_colors['failed']}]{stats['failed']}[/{status_colors['failed']}] | [bold]Rejected:[/bold] [{status_colors['rejected']}]{stats['rejected']}[/{status_colors['rejected']}] | [bold]Generating:[/bold] [{status_colors['generating']}]{stats['generating']}[/{status_colors['generating']}]"""

        console.print(Panel(stats_content, title="Statistics", border_style=COLOR_INFO))

def display_frame_detail(frame: Dict[str, Any], scene: Optional[Dict[str, Any]] = None):
    """Display detailed information about a single frame."""
    status_colors = {
        'pending': COLOR_WARNING,
        'generating': COLOR_INFO,
        'completed': COLOR_SUCCESS,
        'approved': "bright_green",
        'failed': COLOR_ERROR,
        'rejected': "orange"
    }

    status = frame.get('status', 'unknown')
    status_color = status_colors.get(status, "white")

    # Frame information
    info_content = f"""[bold]Frame ID:[/bold] {frame['id']}
[bold]Scene:[/bold] Scene {frame.get('scene_number', '?')}
[bold]Type:[/bold] {frame.get('frame_type', 'unknown').title()}
[bold]Status:[/bold] [{status_color}]{status}[/{status_color}]
[bold]Created:[/bold] {frame.get('created_at', 'N/A')}"""

    if frame.get('image_filename'):
        info_content += f"\n[bold]Image:[/bold] {frame['image_filename']}"

    if frame.get('image_path'):
        info_content += f"\n[bold]Path:[/bold] {frame['image_path']}"

    if frame.get('approval_feedback'):
        info_content += f"\n[bold]Feedback:[/bold] {frame['approval_feedback']}"

    console.print(Panel(info_content, title="Frame Information", border_style=COLOR_INFO))

    # Prompt panel
    prompt_text = frame.get('prompt', 'No prompt available')
    console.print(Panel(
        prompt_text,
        title="Image Generation Prompt",
        border_style=COLOR_PROMPT,
        padding=(1, 2)
    ))

    # Scene context if provided
    if scene:
        scene_content = f"""[bold]Scene {scene.get('scene_number', '?')}:[/bold] {scene.get('title', 'Untitled')}
[bold]Duration:[/bold] {scene.get('duration', 0)}s
[bold]Description:[/bold] {scene.get('description', 'No description')[:200]}..."""

        console.print(Panel(scene_content, title="Scene Context", border_style="dim"))

def display_generation_progress(current: int, total: int, status_message: str):
    """Display generation progress information."""
    percentage = (current / total * 100) if total > 0 else 0

    progress_content = f"""[bold]Progress:[/bold] {current}/{total} frames ({percentage:.1f}%)
[bold]Status:[/bold] {status_message}"""

    console.print(Panel(progress_content, border_style=COLOR_INFO))

def display_videos_grid(videos: List[Dict[str, Any]], stats: Optional[Dict[str, int]] = None):
    """Display scene videos in a table format with status indicators."""
    table = Table(title="Scene Video Status", show_header=True, header_style="bold cyan")

    table.add_column("ID", style="dim", width=8)
    table.add_column("Scene", justify="center", width=8)
    table.add_column("Duration", justify="center", width=10)
    table.add_column("Status", justify="center", width=12)
    table.add_column("Video File", style="dim", width=30)
    table.add_column("Created", justify="right", width=12)

    # Status colors mapping
    status_colors = {
        'pending': COLOR_WARNING,
        'generating': COLOR_INFO,
        'completed': COLOR_SUCCESS,
        'approved': "bright_green",
        'failed': COLOR_ERROR,
        'rejected': "orange"
    }

    for video in videos:
        status = video.get('status', 'unknown')
        status_color = status_colors.get(status, "white")

        table.add_row(
            str(video['id']),
            f"Scene {video.get('scene_number', '?')}",
            video.get('duration', '?'),
            f"[{status_color}]{status}[/{status_color}]",
            video.get('video_filename', 'None')[:30] if video.get('video_filename') else '-',
            video.get('created_at', 'N/A')[:10] if video.get('created_at') else 'N/A'
        )

    console.print(table)

    # Display statistics if provided
    if stats:
        stats_content = f"""[bold]Total:[/bold] {stats['total']} videos
[bold]Approved:[/bold] [{status_colors['approved']}]{stats['approved']}[/{status_colors['approved']}] | [bold]Completed:[/bold] [{status_colors['completed']}]{stats['completed']}[/{status_colors['completed']}] | [bold]Pending:[/bold] [{status_colors['pending']}]{stats['pending']}[/{status_colors['pending']}]
[bold]Failed:[/bold] [{status_colors['failed']}]{stats['failed']}[/{status_colors['failed']}] | [bold]Rejected:[/bold] [{status_colors['rejected']}]{stats['rejected']}[/{status_colors['rejected']}] | [bold]Generating:[/bold] [{status_colors['generating']}]{stats['generating']}[/{status_colors['generating']}]"""

        console.print(Panel(stats_content, title="Statistics", border_style=COLOR_INFO))

def display_video_detail(video: Dict[str, Any], scene: Optional[Dict[str, Any]] = None):
    """Display detailed information about a single scene video."""
    status_colors = {
        'pending': COLOR_WARNING,
        'generating': COLOR_INFO,
        'completed': COLOR_SUCCESS,
        'approved': "bright_green",
        'failed': COLOR_ERROR,
        'rejected': "orange"
    }

    status = video.get('status', 'unknown')
    status_color = status_colors.get(status, "white")

    # Video information
    info_content = f"""[bold]Video ID:[/bold] {video['id']}
[bold]Scene:[/bold] Scene {video.get('scene_number', '?')}
[bold]Status:[/bold] [{status_color}]{status}[/{status_color}]
[bold]Duration:[/bold] {video.get('duration', 'N/A')}
[bold]Aspect Ratio:[/bold] {video.get('aspect_ratio', 'N/A')}
[bold]Created:[/bold] {video.get('created_at', 'N/A')}"""

    if video.get('video_filename'):
        info_content += f"\n[bold]Video File:[/bold] {video['video_filename']}"

    if video.get('video_path'):
        info_content += f"\n[bold]Path:[/bold] {video['video_path']}"

    if video.get('trim_start') or video.get('trim_end'):
        info_content += f"\n[bold]Trim:[/bold] {video.get('trim_start', 0)}s - {video.get('trim_end', 'end')}s"

    if video.get('approval_feedback'):
        info_content += f"\n[bold]Feedback:[/bold] {video['approval_feedback']}"

    console.print(Panel(info_content, title="Video Information", border_style=COLOR_INFO))

    # Motion prompt panel
    prompt_text = video.get('prompt', 'No motion prompt available')
    console.print(Panel(
        prompt_text,
        title="Motion Prompt (Veo API)",
        border_style=COLOR_PROMPT,
        padding=(1, 2)
    ))

    # Scene context if provided
    if scene:
        scene_content = f"""[bold]Scene {scene.get('scene_number', '?')}:[/bold] {scene.get('title', 'Untitled') if scene.get('title') else 'Scene'}
[bold]Duration:[/bold] {scene.get('duration', 0)}s
[bold]Description:[/bold] {scene.get('description', 'No description')[:200]}..."""

        console.print(Panel(scene_content, title="Scene Context", border_style="dim"))
