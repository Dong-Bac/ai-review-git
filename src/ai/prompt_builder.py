from __future__ import annotations
from src.types import Prompt, ReviewContext
from src.rules import get_default_rules
from src.utils.files import truncate_content


# ── System prompt ────────────────────────────────────────────

def _build_system_prompt(rules: str) -> str:
    effective_rules = rules.strip() or get_default_rules()

    return f"""You are an expert senior software engineer performing a thorough code review.
Your goal is to provide clear, actionable, and constructive feedback.

## Your Review Guidelines

{effective_rules}

## Output Format

Structure your response using these sections (use markdown headers):

### 🐛 Bugs & Issues
List any bugs, logic errors, or incorrect behaviour found.

### 🔒 Security
Highlight any security vulnerabilities or risky patterns.

### ⚡ Performance
Note performance concerns or inefficient code.

### 🎨 Code Quality
Comment on readability, naming, structure, and best practices.

### ✅ What's Good
Acknowledge what's done well.

### 💡 Suggestions
Actionable improvements the developer should consider.

Keep the review concise. Focus on the most important issues.
Use code examples when illustrating a fix."""


# ── User prompt sections ──────────────────────────────────────

def _build_project_context(ctx: ReviewContext) -> str:
    return (
        f"## Project Context\n\n"
        f"- **Name:** {ctx.project_info.name}\n"
        f"- **Branch:** {ctx.branch}\n"
        f"- **Changed Files:** {len(ctx.changed_files)}"
    )


def _build_changed_files_section(ctx: ReviewContext) -> str:
    if not ctx.changed_files:
        return ""
    lines = "\n".join(f"- [{f.status}] {f.path}" for f in ctx.changed_files)
    return f"## Changed Files\n\n{lines}"


def _build_diff_section(diff: str) -> str:
    truncated = truncate_content(diff, max_chars=12_000)
    return f"## Git Diff (Staged Changes)\n\n```diff\n{truncated}\n```"


def _build_file_contents_section(ctx: ReviewContext) -> str:
    files_with_content = [
        f for f in ctx.changed_files
        if f.content and f.status != "deleted"
    ]
    if not files_with_content:
        return ""

    blocks: list[str] = []
    for f in files_with_content:
        ext = f.path.rsplit(".", 1)[-1] if "." in f.path else ""
        truncated = truncate_content(f.content or "", max_chars=6_000)
        blocks.append(f"### {f.path}\n```{ext}\n{truncated}\n```")

    return "## File Contents\n\n" + "\n\n".join(blocks)


def _build_user_prompt(ctx: ReviewContext) -> str:
    sections = [
        _build_project_context(ctx),
        _build_changed_files_section(ctx),
        _build_diff_section(ctx.diff),
        _build_file_contents_section(ctx),
        "---",
        "Please review the above changes and provide structured feedback.",
    ]
    return "\n\n".join(s for s in sections if s)


# ── Public entry point ────────────────────────────────────────

def build_prompt(ctx: ReviewContext) -> Prompt:
    """Assemble the complete Prompt ready for the AI provider."""
    return Prompt(
        system=_build_system_prompt(ctx.rules),
        user=_build_user_prompt(ctx),
    )
