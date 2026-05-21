
from __future__ import annotations
import asyncio
import json
from pathlib import Path  ## dọc file
from typing import Optional


async def read_file_safe(path: Path) -> Optional[str]:
    try:
        return await asyncio.to_thread(path.read_text, encoding = "utf-8", errors = "replace")
    except FileNotFoundError:
        return None
    except OSError:
        return None

async def read_files_concurrently(file_paths: list[str], root: Path):
    async def _read(rel_path: str) -> tuple[str, Optional[str]]:
        content = await read_file_safe(root / rel_path)
        return rel_path, content
    
    results = await asyncio.gather(*[_read(p) for p in file_paths], return_exceptions= True)

    # filter
    valid_result = []
    for r in results:
        if isinstance(r, BaseException):
            continue
        valid_result.append(r)

    return {path: content for path, content in valid_result if content is not None}

def truncate_content(content: str, max_chars: int = 8_000) -> str:
    """Truncate content at a line boundary to avoid breaking mid-line code.

    Appends a clear truncation marker that is valid inside code blocks
    (as a comment) so the AI doesn't receive malformed Markdown.
    """
    if len(content) <= max_chars:
        return content

    # Truncate at the nearest newline before max_chars to avoid
    # cutting mid-line, which would break code block syntax.
    truncated = content[:max_chars]
    last_newline = truncated.rfind("\n")
    if last_newline > max_chars * 0.7:  # Only use line boundary if reasonably close
        truncated = truncated[:last_newline]

    return truncated + "\n# ... [truncated for length] ..."


async def resolve_project_name(root: Path) -> str:
    pkg = await read_file_safe(root / "package.json")
    if pkg:
        try:
            data = json.loads(pkg)
            name = data.get("name")
            if name:
                return str(name)
        except json.JSONDecodeError:
            pass

    pyproject = await read_file_safe(root / "pyproject.toml")
    if pyproject:
        for line in pyproject.splitlines():
            if line.strip().startswith("name") and "=" in line:
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    
    return root.name
