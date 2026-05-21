from __future__ import annotations
from src.types import Prompt, ReviewContext
from src.rules import get_default_rules
from src.utils.files import truncate_content


# ── System prompt ────────────────────────────────────────────

def _build_system_prompt(rules: str) -> str:
    effective_rules = rules.strip() or get_default_rules()

    return f"""Bạn là một kỹ sư phần mềm cao cấp thực hiện đánh giá mã nguồn.
Mục tiêu của bạn là đưa ra phản hồi rõ ràng, có thể hành động và mang tính xây dựng.

## Hướng dẫn Đánh giá

{effective_rules}

## Định dạng Đầu ra

Cấu trúc phản hồi bằng các phần sau (sử dụng markdown headers):

### 🐛 Lỗi & Vấn đề
Liệt kê các lỗi, lỗi logic hoặc hành vi sai.

### 🔒 Bảo mật
Nêu bật các lỗ hổng bảo mật hoặc pattern rủi ro.

### ⚡ Hiệu suất
Ghi chú các vấn đề về hiệu suất hoặc mã không hiệu quả.

### 🎨 Chất lượng Mã
Nhận xét về khả năng đọc, đặt tên, cấu trúc và best practices.

### ✅ Điểm Tốt
Ghi nhận những gì đã làm tốt.

### 💡 Gợi ý
Các cải tiến có thể hành động mà developer nên cân nhắc.

Giữ đánh giá ngắn gọn. Tập trung vào các vấn đề quan trọng nhất.
Sử dụng ví dụ mã khi minh họa cách sửa lỗi.

**QUAN TRỌNG: Trả lời HOÀN TOÀN bằng tiếng Việt.**"""


# ── User prompt sections ──────────────────────────────────────

def _build_project_context(ctx: ReviewContext) -> str:
    return (
        f"## Project Context\n\n"
        f"- **Name:** {ctx.project_info.name}\n"
        f"- **Branch:** {ctx.branch}\n"
        f"- **Changed Files:** {len(ctx.changed_files)}"
    )

def _build_commit_context(ctx: ReviewContext) -> str:
    return(
        f"## Commit Context\n\n"
        f"- **Branch:** {ctx.branch}\n"
        f"- **Purpose:** Review staged changes before commit\n"
        f"- **Scope:** {len(ctx.changed_files)} file changed\n"
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
        _build_commit_context(ctx),
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
