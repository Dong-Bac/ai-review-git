import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

# Force UTF-8 encoding for stdout/stderr on Windows to handle Vietnamese/Unicode
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

console = Console()
error_console = Console(stderr=True)


def info(message: str) -> None:
    console.print(f"[cyan]>> {message}[/cyan]")

def success(message: str) -> None:
    console.print(f"[green]>> {message}[/green]")


def warn(message: str) -> None:
    console.print(f"[yellow]>> {message}[/yellow]")


def error(message: str, detail: str = "") -> None:
    error_console.print(f"[red]!! {message}[/red]")
    if detail:
        error_console.print(f"[dim]{detail}[/dim]")


def print_review(content: str, model: str) -> None:
    """Render the AI review as beautifully formatted Markdown inside a panel."""
    console.print()
    console.print(
        Panel(
            Markdown(content),
            title=f"[bold blue]AI Code Review[/bold blue]",
            subtitle=f"[dim]Model: {model}[/dim]",
            border_style="blue",
            padding=(1, 2),
        )
    )
    console.print()

def stream_review(chunk: str, model: str, is_first: bool = False) -> None:
    if is_first:
        console.print()
        
    console.print(chunk, end="")
