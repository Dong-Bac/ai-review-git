"""
`ai-review review` command handler.
Orchestrates the full review workflow — no business logic, only coordination.
"""

from __future__ import annotations
import asyncio
from pathlib import Path

from rich.progress import Progress, SpinnerColumn, TextColumn

from src.cache import ReviewCache
from src.config import load_config
from src.git import is_git_repository, get_git_diff_info
from src.ai import create_ai_provider, build_prompt
from src.rules import load_rules
from src.utils.files import read_files_concurrently, resolve_project_name
from src.utils.terminal import stream_review, success, warn, error, print_review
from src.types import ReviewContext, ReviewResult, ProjectInfo
from src.utils.logger import setup_logging
from src.memory import get_memory_store, embed_diff, MemoryQuery
import logging

logger = logging.getLogger(__name__)

AI_REVIEW_ROOT = Path(__file__).resolve().parent.parent.parent

async def run_review(
    use_env: bool = False,
    verbose: bool = False,
    no_cache: bool = False,
    cache_ttl: int = 300,
    persistent_cache: bool = False,
    no_memory: bool = False,
) -> None:
    setup_logging(verbose = verbose)
    root = Path.cwd()
    # ── 0. Initialise cache ──────────────────────────────────
    cache = ReviewCache(ttl_seconds=cache_ttl, persistent=persistent_cache)

    # ── 1. Load config (fail fast) ───────────────────────────
    try:
        if use_env:
            config = load_config(env_path=AI_REVIEW_ROOT)
        else:
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
            project_info=ProjectInfo(name=project_name, root_path=str(root.resolve())),
        )

        # ── 6b. Vector memory: retrieve similar past reviews ──
        memory_results = None
        if config.memory.enabled and not no_memory:
            try:
                store = get_memory_store(
                    db_path=config.memory.db_path,
                    project=project_name,
                )
                if store is not None:
                    diff_embedding = embed_diff(git_info.diff)
                    file_paths = [f.path for f in changed_files]
                    memory_results = store.query_similar(
                        MemoryQuery(
                            diff_embedding=diff_embedding,
                            files=file_paths,
                            branch=git_info.branch,
                            top_k=config.memory.top_k,
                        )
                    )
                    if memory_results:
                        success(f"Found {len(memory_results)} similar past review(s).")
            except Exception as exc:
                logger.warning("Vector memory retrieval failed: %s", exc)

        prompt = build_prompt(context, memory_results=memory_results)

        # ── 7. Check cache (unless --no-cache) ───────────────
        cache_key = ReviewCache.make_key(git_info.diff)
        if not no_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                progress.stop()
                success("Review loaded from cache.")
                print_review(cached.content, cached.model)
                return

        # ── 8. Call AI ───────────────────────────────────────
        task = progress.add_task("🤖 Asking AI...", total=None)
        progress.stop()
        try:
            provider = create_ai_provider(config)
            collected_content = []
            async for chunk in provider.stream(prompt=prompt):
                collected_content.append(chunk.content)
                stream_review(chunk.content, config.model, is_first=(len(collected_content) == 1))
                if chunk.finish_reason:
                    break
            full_content = "".join(collected_content)
        except RuntimeError as exc:
            error("AI request failed.", str(exc))
            raise SystemExit(1)

        progress.remove_task(task)

    # ── 9. Store result in cache ─────────────────────────────
    result = ReviewResult(content=full_content, model=config.model)
    cache.set(cache_key, result)

    # ── 9b. Save to vector memory for future retrieval ──────
    if config.memory.enabled and not no_memory and memory_results is not None:
        try:
            store = get_memory_store(
                db_path=config.memory.db_path,
                project=project_name,
            )
            if store is not None:
                from src.memory.models import ReviewRecord
                diff_embedding = embed_diff(git_info.diff)
                file_paths = [f.path for f in changed_files]
                record = ReviewRecord.from_review_result(
                    result=result,
                    diff_hash=cache_key,
                    branch=git_info.branch,
                    project=project_name,
                    files=file_paths,
                    embedding=diff_embedding,
                )
                store.add_review(record)
        except Exception as exc:
            logger.warning("Failed to save review to vector memory: %s", exc)

    # ── 10. Print result ─────────────────────────────────────
    print_review(full_content, config.model)
    success("Review completed")
