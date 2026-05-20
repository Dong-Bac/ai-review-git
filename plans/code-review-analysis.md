# AI-Review Python — Kế hoạch Đánh giá và Cải tiến Mã Toàn diện

## Tổng quan

Tài liệu này cung cấp phân tích kỹ lưỡng về mã nguồn [`ai-review-py`](pyproject.toml:1) từ nhiều khía cạnh: kiến ​​trúc, chất lượng mã, bảo mật, hiệu suất, khả năng bảo trì, khả năng mở rộng và trải nghiệm người dùng. Mỗi phát hiện được phân loại theo mức độ nghiêm trọng và bao gồm các khuyến nghị có thể thực hiện được.

---

## 1. 🔴 Các Vấn đề Nghiêm trọng

### 1.1 Cấu hình Không khớp: `.env.example` so với [`config.py`](src/config.py:6)

| Tệp | Biến được sử dụng |

|---|---|

| [`.env.example`](.env.example:2) | `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL`, `DEEPSEEK_BASE_URL` |

| [`src/config.py`](src/config.py:8) | `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL`, `DEEPSEEK_BASE_URL` |

| [`README.md`](README.md:32) | `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_BASE_URL` |

**Vấn đề:** Tài liệu README mô tả các biến môi trường của OpenRouter, nhưng mã nguồn thực tế và tệp `.env.example` lại sử dụng các tên cụ thể của DeepSeek. Điều này gây nhầm lẫn và dẫn đến việc người dùng cấu hình sai công cụ.

**Giải pháp:** Đồng bộ hóa cả ba nguồn. Hoặc:
- Đổi tên các biến môi trường thành `OPENROUTER_*` và cập nhật mã nguồn cho phù hợp (khuyến nghị — tổng quát hơn), HOẶC

- Cập nhật README để khớp với tên thực tế của DeepSeek.

### 1.2 Nhà cung cấp DeepSeek được mã hóa cứng — Không có lựa chọn nhà cung cấp

[`src/ai/__init__.py`](src/ai/__init__.py:10) luôn trả về `DeepSeekProvider`, bỏ qua bất kỳ lựa chọn nào dựa trên cấu hình. README và cấu hình cho thấy hỗ trợ OpenRouter, nhưng không có cách nào để chuyển đổi nhà cung cấp.

**Khắc phục:** Thêm trường cấu hình `provider` và một factory điều phối đến triển khai chính xác.

---

## 2. 🟠 Các vấn đề về kiến ​​trúc và thiết kế

### 2.1 Không có cơ chế thử lại / ngắt mạch cho các cuộc gọi API AI

[`src/ai/providers.py`](src/ai/providers.py:47) thực hiện một yêu cầu HTTP duy nhất với thời gian chờ 120 giây. Nếu API bị giới hạn tốc độ hoặc tạm thời ngừng hoạt động, toàn bộ quá trình xem xét sẽ thất bại.

**Khuyến nghị:** Thực hiện:
- Thử lại theo cấp số nhân (3 lần thử)

- Phát hiện giới hạn tốc độ từ phản hồi HTTP 429
- Giảm hiệu suất một cách nhẹ nhàng (ví dụ: "Dịch vụ AI không khả dụng, hãy thử lại sau")

### 2.2 Không hỗ trợ truyền dữ liệu trực tuyến

Mã nguồn có một đoạn mã được chú thích cho việc truyền dữ liệu trực tuyến ([`providers.py`](src/ai/providers.py:82)), nhưng nó chưa được triển khai. Người dùng phải đợi phản hồi đầy đủ trước khi thấy bất kỳ đầu ra nào.

**Khuyến nghị:** Triển khai truyền dữ liệu trực tuyến thông qua SSE để có trải nghiệm người dùng tốt hơn, đặc biệt là đối với các đánh giá lớn.

### 2.3 Không có lớp bộ nhớ đệm

Mỗi lần gọi đánh giá đều truy cập API AI, ngay cả khi cùng một sự khác biệt đã được đánh giá trước đó. Điều này lãng phí token và thời gian.

**Khuyến nghị:** Thêm bộ nhớ đệm tùy chọn (ví dụ: mã băm của sự khác biệt → kết quả đánh giá được lưu trong bộ nhớ đệm) với TTL hoặc cờ `--no-cache`.

### 2.4 Không xử lý lỗi cho các lỗi cục bộ trong quá trình đọc đồng thời

[`src/utils/files.py`](src/utils/files.py:17) sử dụng `asyncio.gather` mà không có `return_exceptions=True`. Nếu một lần đọc tệp thất bại, tất cả các lần đọc đều thất bại.

**Khuyến nghị:** Sử dụng `return_exceptions=True` và lọc các lỗi một cách khéo léo.

### 2.5 Việc tạo `ReviewContext` sử dụng `type()` nội tuyến thay vì Dataclass

[`src/commands/review.py`](src/commands/review.py:96) tạo một đối tượng `ProjectInfo` bằng cách sử dụng `type("ProjectInfo", (), {...})()` thay vì dataclass [`ProjectInfo`](src/types.py:29) hiện có.

**Khắc phục:** Sử dụng dataclass `ProjectInfo` thực sự.

** ### 2.6 Không có sự phân tách trách nhiệm trong `review.py`

[`src/commands/review.py`](src/commands/review.py:21) chứa quá nhiều trách nhiệm: tải cấu hình, thao tác git, đọc tệp, xây dựng lời nhắc, gọi AI và hiển thị đầu ra. Điều này vi phạm Nguyên tắc Trách nhiệm Đơn nhất.

**Khuyến nghị:** Tách logic điều phối vào một lớp `ReviewService` chuyên dụng.

** ---

## 3. 🟡 Chất lượng và khả năng bảo trì mã

### 3.1 Thiếu chú thích kiểu dữ liệu

- [`src/utils/files.py`](src/utils/files.py:17): Kiểu trả về của `read_files_concurrently` bị thiếu (`-> dict[str, Optional[str]]`)

- [`src/utils/files.py`](src/utils/files.py:31): Kiểu trả về của `resolve_project_name` là `str` nhưng có thể được chỉ định rõ ràng hơn

### 3.2 Phát hiện tập tin Git không hiệu quả

[`src/git/index.py`](src/git/index.py:52) gọi `repo.index.diff("HEAD")` hai lần (dòng 67 và 81), gây trùng lặp công việc. Logic để phát hiện các tập tin đã được thêm vào vùng chờ quá phức tạp.

**Khuyến nghị:** Đơn giản hóa thành một lệnh `git diff --cached --name-status` duy nhất.

### 3.3 Mã số đặc biệt để cắt bớt nội dung

[`src/ai/prompt_builder.py`](src/ai/prompt_builder.py:64,79) sử dụng giới hạn ký tự `12_000` và `6_000` được mã hóa cứng. Chúng nên là các hằng số có thể cấu hình.

### 3.4 Không có ghi nhật ký

Toàn bộ mã nguồn sử dụng kiểu xuất `print` thông qua Rich. Không có nhật ký có cấu trúc để gỡ lỗi hoặc kiểm toán.

**Khuyến nghị:** Thêm một mô-đun `logging` với các cấp độ ghi nhật ký có thể cấu hình.

### 3.5 Các tệp `__init__.py` trống

[`src/commands/__init__.py`](src/commands/__init__.py:1) và [`src/utils/__init__.py`](src/utils/__init__.py:1) đều trống. Mặc dù vẫn hoạt động, chúng nên xuất các API công khai để việc nhập khẩu được gọn gàng hơn.

### 3.6 `truncate_content` tạo ra Markdown không hợp lệ

[`src/utils/files.py`](src/utils/files.py:28) thêm `\n\n ...` sau khi cắt bớt nội dung.