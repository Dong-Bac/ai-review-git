from __future__ import annotations
from typing import Optional

from src.types import Prompt, ReviewContext
from src.rules import get_default_rules
from src.utils.files import truncate_content
from src.memory.models import MemoryResult


# ── System prompt ────────────────────────────────────────────

def _build_system_prompt(rules: str) -> str:
    effective_rules = rules.strip() or get_default_rules()

    return f"""Bạn là một kỹ sư phần mềm cao cấp thực hiện đánh giá mã nguồn.
Mục tiêu của bạn là đưa ra phản hồi rõ ràng, có thể hành động và mang tính xây dựng.

## Hướng dẫn Đánh giá

{effective_rules}

## Thang điểm Đánh giá (tổng: 10)

Sau khi phân tích, bạn PHẢI chấm điểm tổng thể theo thang 10 với các tiêu chí sau:

| Tiêu chí | Trọng số | Mô tả |
|----------|----------|-------|
| 🐛 Tính đúng đắn | 3.0 | Không có lỗi logic, bug, edge case không xử lý |
| 🔒 Bảo mật | 2.0 | Không có lỗ hổng, exposed secrets, injection risks |
| ⚡ Hiệu suất | 1.5 | Code hiệu quả, không lãng phí tài nguyên |
| 🎨 Chất lượng mã | 2.0 | Dễ đọc, đặt tên tốt, cấu trúc hợp lý, best practices |
| 📚 Khả năng bảo trì | 1.5 | Dễ mở rộng, testable, có documentation |

**Cách tính:** Mỗi tiêu chí được chấm từ 0–10, sau đó nhân với trọng số.
Tổng điểm = Σ(điểm_tiêu_chí × trọng_số) / 10

## Phân loại Mức độ Nghiêm trọng

Mỗi vấn đề tìm thấy PHẢI được gắn nhãn mức độ:
- 🔴 **Critical** — Có thể gây crash, mất dữ liệu, lỗ hổng bảo mật
- 🟠 **Major** — Logic sai, hiệu năng kém nghiêm trọng
- 🟡 **Minor** — Vi phạm coding convention, code khó đọc
- 🔵 **Info** — Gợi ý cải tiến, best practice

## Định dạng Đầu ra

Cấu trúc phản hồi bằng các phần sau (sử dụng markdown headers):

### 📊 Đánh giá Tổng quan
Tóm tắt ngắn gọn về chất lượng chung của changeset.
Kèm bảng điểm chi tiết theo rubric ở trên.

### 🐛 Lỗi & Vấn đề
Liệt kê các lỗi, lỗi logic hoặc hành vi sai, kèm mức độ nghiêm trọng.

### 🔒 Bảo mật
Nêu bật các lỗ hổng bảo mật hoặc pattern rủi ro.

### ⚡ Hiệu suất
Ghi chú các vấn đề về hiệu suất hoặc mã không hiệu quả.

### 🎨 Chất lượng Mã
Nhận xét về khả năng đọc, đặt tên, cấu trúc và best practices.

### ✅ Điểm Tốt
Ghi nhận những gì đã làm tốt.

### 💡 Gợi ý Cải tiến
Các cải tiến có thể hành động mà developer nên cân nhắc.

## Quy tắc quan trọng

1. **Luôn đưa ra điểm số cụ thể** — Không đánh giá chung chung
2. **Mỗi vấn đề phải có mức độ nghiêm trọng** — Dùng emoji 🔴🟠🟡🔵
3. **Mỗi vấn đề phải kèm file & dòng code** — `path/to/file.py:42`
4. **Ưu tiên các vấn đề Critical/Major** — Không sa đà vào chi tiết vụn vặt
5. **Sử dụng ví dụ mã khi minh họa cách sửa lỗi**
6. **Giữ giọng văn xây dựng, không chỉ trích**

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


def _build_review_instructions(ctx: ReviewContext) -> str:
    """Build the review instructions section with scoring requirements."""
    statuses = {f.status for f in ctx.changed_files}
    return f"""## Yêu cầu Đánh giá

Vui lòng đánh giá changeset này theo các yêu cầu sau:

1. **Chấm điểm tổng thể** trên thang 10 (theo rubric đã nêu trong system prompt)
2. **Liệt kê tất cả vấn đề** tìm thấy, kèm:
   - Mức độ nghiêm trọng (🔴 Critical / 🟠 Major / 🟡 Minor / 🔵 Info)
   - Đường dẫn file & số dòng chính xác
   - Giải thích ngắn gọn tại sao đây là vấn đề
   - Đề xuất cách khắc phục (kèm code mẫu nếu cần)
3. **Đưa ra bảng điểm chi tiết** cho từng tiêu chí

### Ngữ cảnh bổ sung
- **Project:** {ctx.project_info.name}
- **Branch:** {ctx.branch}
- **Số file thay đổi:** {len(ctx.changed_files)}
- **Loại thay đổi:** {', '.join(sorted(statuses))}

Hãy đánh giá dựa trên mức độ ảnh hưởng của changeset này đến toàn bộ dự án."""


def _build_memory_context(memory_results: list[MemoryResult]) -> str:
    """Build a markdown section from similar past reviews.

    This section is injected into the user prompt to give the AI
    context about how similar changesets were reviewed before.
    Token budget: ~800 tokens max.
    """
    if not memory_results:
        return ""

    lines = [
        "## 📜 Similar Past Reviews",
        "",
        "The following reviews of similar changesets were found in project history.",
        "Use them as reference for consistency, but evaluate the current changeset independently.",
        "",
    ]

    for i, mr in enumerate(memory_results, 1):
        rec = mr.record
        lines.append(f"### Past Review #{i} (similarity: {mr.similarity:.0%})")
        lines.append("")
        lines.append(f"- **Branch:** {rec.branch or 'unknown'}")
        lines.append(f"- **Files:** {', '.join(rec.files[:5])}{'…' if len(rec.files) > 5 else ''}")
        lines.append(f"- **Issues found:** {rec.issues_count} (🔴 {rec.critical_count} critical, 🟠 {rec.major_count} major)")
        if rec.score_total is not None:
            lines.append(f"- **Score:** {rec.score_total:.1f}/10")
        if rec.summary:
            lines.append(f"- **Summary:** {rec.summary[:300]}")
        lines.append("")

    return "\n".join(lines)


def _build_user_prompt(ctx: ReviewContext, memory_results: Optional[list[MemoryResult]] = None) -> str:
    sections = [
        _build_project_context(ctx),
        _build_commit_context(ctx),
        _build_changed_files_section(ctx),
        _build_diff_section(ctx.diff),
        _build_file_contents_section(ctx),
        _build_memory_context(memory_results or []),
        _build_review_instructions(ctx),
    ]
    return "\n\n".join(s for s in sections if s)


# ── Public entry point ────────────────────────────────────────

def build_prompt(ctx: ReviewContext, memory_results: Optional[list[MemoryResult]] = None) -> Prompt:
    """Assemble the complete Prompt ready for the AI provider."""
    return Prompt(
        system=_build_system_prompt(ctx.rules),
        user=_build_user_prompt(ctx, memory_results=memory_results),
    )
