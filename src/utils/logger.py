"""
Structured logging cho ai-review.
- Ghi ra console (stderr) qua RichHandler
- Ghi ra file tại ~/.ai-review/logs/
- Mức log mặc định: WARNING (chỉ hiện warning/error)
- --verbose bật DEBUG
"""

from __future__ import annotations
import logging
import sys
from datetime import datetime
from pathlib import Path
from rich.logging import RichHandler

LOG_DIR = Path.home() / ".ai_review" / "logs"

def setup_logging(verbose: bool = False) -> None:
    """Khởi tạo logging một lần duy nhất"""
    if logging.getLogger().hasHandlers():
        return
    
    level = logging.DEBUG if verbose else logging.WARNING

    console_handler = RichHandler(
        rich_tracebacks = True,
        show_time=True,
        show_path=False,
        markup=True,
    ) 
    console_handler.setLevel(level)

    # ── File handler (xoay theo ngày) ─────────────────────────
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = LOG_DIR / f"ai-review-{today}.log"

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # File luôn ghi DEBUG
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(file_formatter)

     # ── Root logger ───────────────────────────────────────────
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    # ── Dọn log cũ (giữ 7 ngày) ──────────────────────────────
    _cleanup_old_logs(days=7)

def _cleanup_old_logs(days: int = 7) -> None:
    """Xoá file log cũ hơn `days` ngày."""
    import time
    cutoff = time.time() - days * 86_400
    for f in LOG_DIR.iterdir():
        if f.suffix == ".log" and f.stat().st_mtime < cutoff:
            f.unlink()