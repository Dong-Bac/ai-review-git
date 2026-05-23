from __future__ import annotations
from pathlib import Path
from src.utils.files import read_file_safe

RULES_FILE = Path(".roo") / "rules.md"

DEFAULT_RULES = """
## Default Review Rules

### 1. Tính đúng đắn (Correctness)
- Kiểm tra lỗi logic, off-by-one, null pointer, race condition
- Xác minh xử lý edge cases (empty input, boundary values, exceptions)
- Kiểm tra type safety và type hints nhất quán
- Rà soát xử lý lỗi (try/catch phù hợp, không nuốt lỗi)

### 2. Bảo mật (Security)
- Phát hiện hardcoded secrets, API keys, passwords
- Kiểm tra SQL injection, command injection, path traversal
- Rà soát authentication/authorization logic
- Kiểm tra input validation và sanitization
- Cảnh báo nếu dùng eval(), exec(), hoặc unsafe deserialization

### 3. Hiệu suất (Performance)
- Phát hiện N+1 queries, vòng lặp không cần thiết
- Kiểm tra sử dụng bộ nhớ, memory leaks
- Rà soát I/O operations không cần async/await
- Kiểm tra caching opportunities
- Cảnh báo các thuật toán không tối ưu (O(n²) thay vì O(n log n))

### 4. Chất lượng mã (Code Quality)
- Đặt tên biến/hàm/class rõ ràng, có ý nghĩa
- Tuân thủ DRY, SOLID principles
- Kiểm tra độ phức tạp (cyclomatic complexity)
- Rà soát error handling (try/catch phù hợp)
- Kiểm tra unit test coverage cho logic mới
- Đảm bảo code formatting nhất quán

### 5. Khả năng bảo trì (Maintainability)
- Code dễ đọc, có comment khi cần
- Cấu trúc module hợp lý, ít dependency vòng
- Có documentation cho public APIs
- Tuân thủ project conventions
- Dễ dàng thêm tính năng mới mà không phá vỡ existing code
""".strip()



def get_default_rules() -> str:
    return DEFAULT_RULES

async def load_rules(root: Path) -> str:
    content = await read_file_safe(root / RULES_FILE)
    return content.strip() if content else get_default_rules()
