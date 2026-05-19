
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
    
    results = await asyncio.gather(*[_read(p) for p in file_paths])
    return {path: content for path, content in results if content is not None}

def truncate_content(content: str, max_chars: int = 8_000) -> str:
    if len(content) <= max_chars:
        return content
    return content[:max_chars] + f"\n\n ..."


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
