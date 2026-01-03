import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from typing import Optional, List, Dict

console = Console()

def prompt_text(
    question: str,
    default: Optional[str] = None,
    required: bool = True
) -> str:
    """Prompt user for text input."""
    while True:
        result = Prompt.ask(question, default=default, console=console)
        if result or not required:
            return result
        console.print("[red]This field is required[/red]")

def prompt_choice(
    question: str,
    choices: List[str],
    default: Optional[str] = None
) -> str:
    """Prompt user to select from choices."""
    return Prompt.ask(
        question,
        choices=choices,
        default=default,
        console=console
    )

def prompt_confirm(
    question: str,
    default: bool = False
) -> bool:
    """Prompt user for yes/no confirmation."""
    return Confirm.ask(question, default=default, console=console)

def prompt_project_details() -> Dict[str, str]:
    """Interactive wizard for project creation."""
    console.print("\n[bold cyan]🎬 Create New Video Project[/bold cyan]\n")
    
    name = prompt_text("Project name", required=True)
    narrative = prompt_text("Main narrative/story", required=True)
    
    duration = prompt_choice(
        "Target duration",
        choices=["15s", "30s", "60s"],
        default="30s"
    )
    
    aspect_ratio = prompt_choice(
        "Aspect ratio",
        choices=["16:9", "9:16", "1:1"],
        default="16:9"
    )
    
    style = prompt_choice(
        "Style theme",
        choices=["cinematic", "minimal", "vibrant", "dark"],
        default="cinematic"
    )
    
    return {
        "name": name,
        "narrative": narrative,
        "target_duration": duration,
        "aspect_ratio": aspect_ratio,
        "style": style
    }
