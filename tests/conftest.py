"""
Shared fixtures and configuration for ai-review tests.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_diff() -> str:
    return """diff --git a/src/example.py b/src/example.py
index abc..def 100644
--- a/src/example.py
+++ b/src/example.py
@@ -1,3 +1,4 @@
 def hello():
-    print("world")
+    name = "world"
+    print(f"Hello, {name}!")
"""


@pytest.fixture
def sample_review_content() -> str:
    return """### 📊 Đánh giá Tổng quan

Changeset nhỏ, chất lượng tốt.

| Tiêu chí | Điểm |
|----------|------|
| Tính đúng đắn | 9/10 |
| Bảo mật | 10/10 |

### 🐛 Lỗi & Vấn đề
- 🔴 **Critical**: Không có
- 🟠 **Major**: Thiếu type hints
"""


@pytest.fixture
def sample_cache_key() -> str:
    return "abc123def456"
