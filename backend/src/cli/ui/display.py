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
