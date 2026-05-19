from __future__ import annotations
from pathlib import Path
from src.utils.files import read_file_safe

RULES_FILE = Path(".roo") / "rules.md"

DEFAULT_RULES = """
    ## Default Review Rules
    -  Check for code correctness and potential bugs
    - Look for security vulnerabilities (injection, auth issues, exposed secrets)
    - Review code style and readability
    - Identify performance concerns
    - Suggest improvements where applicable
    - Keep feedback constructive and actionable
""".strip()



def get_default_rules() -> str:
    return DEFAULT_RULES

async def load_rules(root: Path) -> str:
    content = await read_file_safe(root / RULES_FILE)
    return content.strip() if content else get_default_rules()