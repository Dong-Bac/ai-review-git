import asyncio
import typer
from typing import Optional

app = typer.Typer(
    name="ai-review",
    help="AI-powered code review for your git staged changes",
    add_completion=False,
    pretty_exceptions_enable_locals=False,
)

@app.command("review")
def review() -> None:
    from src.commands.review import run_review
    asyncio.run(run_review())

if __name__ == "__main__":
    app()



