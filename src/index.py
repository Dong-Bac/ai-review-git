import asyncio
import typer
from typing import Optional

app = typer.Typer(
    name="ai-review",
    help="AI-powered code review for your git staged changes",
    add_completion=False,
    pretty_exceptions_show_locals=False,
)

@app.command("review")
def review(
    verbose: bool = typer.Option(
      False, "--verbose", "-v",
      help="Enable DEBUG-level logging"  
    ),
    no_cache: bool = typer.Option(
        False, "--no-cache",
        help="Bypass cache and force a fresh AI call",
    ),
    cache_ttl: int = typer.Option(
        300, "--cache-ttl",
        help="Cache TTL in seconds (default: 300)",
    ),
    persistent_cache: bool = typer.Option(
        False, "--persistent-cache",
        help="Use SQLite persistent cache (survives restarts)",
    ),
) -> None:
    from src.commands.review import run_review
    asyncio.run(run_review(
        verbose = verbose, 
        no_cache=no_cache, 
        cache_ttl=cache_ttl,
        persistent_cache=persistent_cache,))

if __name__ == "__main__":
    app()



