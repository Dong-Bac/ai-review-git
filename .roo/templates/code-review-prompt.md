# Code Review Prompt Template

> Template for generating AI code review prompts.
> Used by [`src/ai/prompt_builder.py`](../../src/ai/prompt_builder.py:1).

## System Prompt Structure

```
Bạn là một kỹ sư phần mềm cao cấp thực hiện đánh giá mã nguồn.
Mục tiêu của bạn là đưa ra phản hồi rõ ràng, có thể hành động và mang tính xây dựng.

## Hướng dẫn Đánh giá
{project_rules}

## Thang điểm Đánh giá (tổng: 10)
| Tiêu chí | Trọng số | Mô tả |
|----------|----------|-------|
| 🐛 Tính đúng đắn | 3.0 | Không có lỗi logic, bug, edge case không xử lý |
| 🔒 Bảo mật | 2.0 | Không có lỗ hổng, exposed secrets, injection risks |
| ⚡ Hiệu suất | 1.5 | Code hiệu quả, không lãng phí tài nguyên |
| 🎨 Chất lượng mã | 2.0 | Dễ đọc, đặt tên tốt, cấu trúc hợp lý, best practices |
| 📚 Khả năng bảo trì | 1.5 | Dễ mở rộng, testable, có documentation |

## Phân loại Mức độ Nghiêm trọng
- 🔴 Critical — Crash, mất dữ liệu, lỗ hổng bảo mật
- 🟠 Major — Logic sai, hiệu năng kém nghiêm trọng
- 🟡 Minor — Vi phạm convention, code khó đọc
- 🔵 Info — Gợi ý cải tiến, best practice

## Định dạng Đầu ra
### 📊 Đánh giá Tổng quan
### 🐛 Lỗi & Vấn đề
### 🔒 Bảo mật
### ⚡ Hiệu suất
### 🎨 Chất lượng Mã
### ✅ Điểm Tốt
### 💡 Gợi ý Cải tiến
```

## User Prompt Structure

```
## Project Context
- Name: {project_name}
- Branch: {branch}
- Changed Files: {count}

## Changed Files
- [status] path/to/file.py

## Git Diff (Staged Changes)
```diff
{diff_content}
```

## File Contents
### path/to/file.py
```python
{file_content}
```

## Yêu cầu Đánh giá
1. Chấm điểm tổng thể trên thang 10
2. Liệt kê vấn đề kèm mức độ nghiêm trọng + file:dòng
3. Đưa ra bảng điểm chi tiết
```

## Key Constants

| Constant | Value | Location |
|----------|-------|----------|
| `MAX_DIFF_CHARS` | 12,000 | [`src/ai/prompt_builder.py`](../../src/ai/prompt_builder.py:106) |
| `MAX_FILE_CHARS` | 6,000 | [`src/ai/prompt_builder.py`](../../src/ai/prompt_builder.py:121) |
| `MAX_TOKENS` | 8,192 | [`src/config.py`](../../src/config.py:24) |
| `CACHE_TTL` | 300s | [`src/index.py`](../../src/index.py:27) |
