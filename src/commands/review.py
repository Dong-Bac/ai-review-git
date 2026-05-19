"""
`ai-review review` command handler.
Orchestrates the full review workflow — no business logic, only coordination.
"""

from __future__ import annotations
import asyncio
from pathlib import Path

from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import load_config
from src.git import is_git_repository, get_git_diff_info
from src.ai import create_ai_provider, build_prompt
from src.rules import load_rules
from src.utils.files import read_files_concurrently, resolve_project_name
from src.utils.terminal import success, warn, error, print_review
from src.types import ReviewContext


async def run_review() -> None:
    root = Path.cwd()

    # ── 1. Load config (fail fast) ───────────────────────────
    try:
        config = load_config()
    except ValueError as exc:
        error("Configuration error", str(exc))
        raise SystemExit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:

        # ── 2. Verify git repo ───────────────────────────────
        task = progress.add_task("Checking git repository...", total=None)
        if not await is_git_repository(root):
            progress.stop()
            error("Not a git repository.", "Run this command from inside a git project.")
            raise SystemExit(1)
        progress.remove_task(task)
        success("Git repository detected.")

        # ── 3. Read staged diff ──────────────────────────────
        task = progress.add_task("🔍 Reading git diff...", total=None)
        try:
            git_info = await get_git_diff_info(root)
        except Exception as exc:
            progress.stop()
            error("Failed to read git diff.", str(exc))
            raise SystemExit(1)

        if git_info.is_empty:
            progress.stop()
            warn("No staged changes found.")
            warn("Stage your changes first:  git add <files>")
            raise SystemExit(0)

        progress.remove_task(task)
        success(f"Git diff ready — {len(git_info.changed_files)} file(s) changed.")

        # ── 4. Read file contents ────────────────────────────
        task = progress.add_task("📄 Loading files...", total=None)
        non_deleted = [f.path for f in git_info.changed_files if f.status != "deleted"]
        file_contents = await read_files_concurrently(non_deleted, root)

        # Attach content back to changed files
        changed_files = [
            f.__class__(
                path=f.path,
                status=f.status,
                content=file_contents.get(f.path),
            )
            for f in git_info.changed_files
        ]

        progress.remove_task(task)
        success(f"Loaded {len(file_contents)} file(s).")

        # ── 5. Load rules + project info ─────────────────────
        rules, project_name = await asyncio.gather(
            load_rules(root),
            resolve_project_name(root),
        )
        if rules:
            success("Custom rules loaded from .roo/rules.md")

        # ── 6. Build context + prompt ────────────────────────
        context = ReviewContext(
            diff=git_info.diff,
            changed_files=changed_files,
            branch=git_info.branch,
            rules=rules,
            project_info=type("ProjectInfo", (), {  # lightweight inline object
                "name": project_name,
                "root_path": str(root.resolve()),
            })(),
        )
        prompt = build_prompt(context)

        # ── 7. Call AI ───────────────────────────────────────
        task = progress.add_task("🤖 Asking AI...", total=None)
        try:
            provider = create_ai_provider(config)
            result = await provider.ask(prompt)
        except RuntimeError as exc:
            progress.stop()
            error("AI request failed.", str(exc))
            raise SystemExit(1)

        progress.remove_task(task)

    tokens_info = f", ~{result.tokens_used} tokens" if result.tokens_used else ""
    success(f"Review completed (model: {result.model}{tokens_info}).")

    # ── 8. Print result ──────────────────────────────────────
    print_review(result.content, result.model)
